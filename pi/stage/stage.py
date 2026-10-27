#!/usr/bin/env python3
"""Five Dimensions on the Raspberry Pi: the room part of the Isadora patch, standalone.

Isadora doesn't run on a Raspberry Pi, so this program does what the patch does:

    camera  -> counts faces (more people, more voices) and follows the performer
               (where you stand decides which wall leads)
    mic     -> loudness makes the leading wall brighter
    OSC     -> the N900's tilt turns the whole room; cues can solo a wall or hold
    output  -> four channels, drawn on one screen as a 2x2 grid (for a 1-in-4-out
               HDMI video wall controller) or as a 4x1 strip

    python3 stage.py                       # windowed, test patterns, for trying it out
    python3 stage.py --fullscreen          # the show
    python3 stage.py --media ~/media       # ~/media/ch1 ... ch4 hold one video or image each
    python3 stage.py --isadora 192.168.1.20:1234   # also send what the Pi senses to Isadora

Keys: Esc quits, D shows the sensors, 1-4 solo a wall, 0 back to automatic,
Space holds the current picture (the show goes on if a sensor fails).

All the "what reacts to what" lives in decide(). Change that to change the piece.
"""
import argparse
import math
import os
import socket
import struct
import threading
import time
from pathlib import Path

import cv2
import numpy as np

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".m4v"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp"}

# How the room reacts. Plain numbers, so they are easy to tune in rehearsal.
FLOOR = 0.15          # how bright a wall stays when it isn't leading (0 = black)
SPREAD = 0.30         # how wide the performer's "light" is across the walls (0..1)
VOICE_FADE = 0.8      # seconds for a voice to fade in or out
FOLLOW = 0.25         # seconds for the light to follow the performer
LOUD_BOOST = 0.35     # how much the microphone adds to the leading wall
FACES_PER_VOICE = 1   # each this many faces in the audience adds a voice


# --- OSC, standard library only (same format as ../hello_isadora.py) -------------------

def _pad(b):
    b += b"\0"
    return b + b"\0" * (-len(b) % 4)


def osc_message(address, *values):
    tags, data = ",", b""
    for v in values:
        if isinstance(v, int):
            tags, data = tags + "i", data + struct.pack(">i", v)
        else:
            tags, data = tags + "f", data + struct.pack(">f", float(v))
    return _pad(address.encode()) + _pad(tags.encode()) + data


def osc_parse(packet):
    """Return (address, [values]) for a plain OSC message, or None."""
    try:
        end = packet.index(b"\0")
        address = packet[:end].decode()
        i = (end + 4) & ~3
        end = packet.index(b"\0", i)
        tags = packet[i + 1:end].decode()
        i = (end + 4) & ~3
        values = []
        for t in tags:
            if t == "i":
                values.append(struct.unpack(">i", packet[i:i + 4])[0]); i += 4
            elif t == "f":
                values.append(struct.unpack(">f", packet[i:i + 4])[0]); i += 4
            else:
                return None
        return address, values
    except (ValueError, struct.error, UnicodeDecodeError):
        return None


# --- Sensors: each runs in its own thread and only writes into `Senses` ------------------

class Senses:
    """What the Pi currently knows about the room. Read by the main loop."""

    def __init__(self):
        self.faces, self.faces_t = 0, 0.0
        self.x, self.x_t = 0.5, 0.0          # performer across the camera, 0 left .. 1 right
        self.level, self.level_t = 0.0, 0.0  # microphone loudness, 0 .. 1
        self.tilt, self.tilt_t = 0.0, 0.0    # N900 tilt, -1 .. 1
        self.solo = 0                        # 0 automatic, 1..4 one wall only
        self.hold = False
        self.camera_view = None              # small frame for the D overlay
        self.status = {}


def camera_thread(senses, index, stop):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        senses.status["camera"] = f"no camera at /dev/video{index}"
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    cascade = cv2.CascadeClassifier(find_face_model())
    senses.status["camera"] = "ok"
    prev, next_faces = None, 0.0
    while not stop.is_set():
        ok, frame = cap.read()
        if not ok:
            senses.status["camera"] = "camera stopped sending"
            time.sleep(0.5)
            continue
        gray = cv2.cvtColor(cv2.resize(frame, (320, 180)), cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        now = time.monotonic()
        # Where is the performer? The centre of whatever moved since the last frame.
        if prev is not None:
            moved = cv2.threshold(cv2.absdiff(prev, gray), 25, 255, cv2.THRESH_BINARY)[1]
            m = cv2.moments(moved, binaryImage=True)
            if m["m00"] > 150:  # enough pixels moved to be a body, not noise
                senses.x, senses.x_t = 1.0 - m["m10"] / m["m00"] / gray.shape[1], now  # mirrored
        prev = gray
        # How many people? Faces are slower to find, so twice a second is enough.
        if now >= next_faces and not cascade.empty():
            big = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found = cascade.detectMultiScale(big, scaleFactor=1.15, minNeighbors=5, minSize=(24, 24))
            senses.faces, senses.faces_t = len(found), now
            next_faces = now + 0.5
            for (fx, fy, fw, fh) in found:
                cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2)
            senses.camera_view = cv2.resize(frame, (320, 180))
    cap.release()


def find_face_model():
    for d in (getattr(getattr(cv2, "data", None), "haarcascades", ""),
              "/usr/share/opencv4/haarcascades/", "/usr/share/opencv/haarcascades/"):
        p = Path(d) / "haarcascade_frontalface_default.xml"
        if d and p.exists():
            return str(p)
    return ""


def audio_thread(senses, device, stop):
    try:
        import sounddevice as sd
    except (ImportError, OSError) as e:
        senses.status["mic"] = f"sounddevice missing ({e})"
        return

    def callback(indata, frames, t, flags):
        rms = float(np.sqrt(np.mean(np.square(indata)))) + 1e-9
        db = 20 * math.log10(rms)
        senses.level = min(1.0, max(0.0, (db + 50) / 40))  # -50 dB silent .. -10 dB loud
        senses.level_t = time.monotonic()

    try:
        with sd.InputStream(device=device, channels=1, samplerate=48000, blocksize=1024,
                            callback=callback):
            senses.status["mic"] = "ok"
            stop.wait()
    except Exception as e:  # no device, busy device, wrong rate: keep the show running
        senses.status["mic"] = f"no microphone ({e})"


def osc_thread(senses, port, stop):
    """Listen for the N900 (/fivedim/tilt x) and for cues (/fivedim/solo n, /fivedim/hold 0|1)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.settimeout(0.5)
    senses.status["osc"] = f"listening on {port}"
    while not stop.is_set():
        try:
            packet, _ = sock.recvfrom(1024)
        except socket.timeout:
            continue
        msg = osc_parse(packet)
        if not msg or not msg[1]:
            continue
        address, values = msg
        if address == "/fivedim/tilt":
            senses.tilt, senses.tilt_t = max(-1.0, min(1.0, float(values[0]))), time.monotonic()
        elif address in ("/fivedim/solo", "/fivedim/cue"):
            senses.solo = int(values[0]) if 0 <= int(values[0]) <= 4 else 0
        elif address == "/fivedim/hold":
            senses.hold = bool(values[0])
    sock.close()


# --- The four channels -----------------------------------------------------------------

class Channel:
    """One wall: loops a video, shows an image, or draws a test pattern."""

    def __init__(self, number, folder, size):
        self.number, self.size = number, size
        self.cap, self.still, self.frame = None, None, None
        self.next_t, self.period = 0.0, 1 / 25
        files = sorted(p for p in folder.iterdir() if p.suffix.lower() in VIDEO_EXT | IMAGE_EXT) \
            if folder and folder.is_dir() else []
        if files and files[0].suffix.lower() in VIDEO_EXT:
            self.cap = cv2.VideoCapture(str(files[0]))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.period = 1 / fps if 1 <= fps <= 120 else 1 / 25
            self.source = files[0].name
        elif files:
            self.still = self._to_surface(cv2.imread(str(files[0])))
            self.source = files[0].name
        else:
            self.source = "test pattern"

    def _to_surface(self, bgr):
        rgb = cv2.cvtColor(cv2.resize(bgr, self.size, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        return pygame.image.frombuffer(rgb.tobytes(), self.size, "RGB")

    def surface(self, now):
        if self.still is not None:
            return self.still
        if self.cap is None:
            return self._pattern(now)
        if now >= self.next_t or self.frame is None:
            ok, bgr = self.cap.read()
            if not ok:  # end of clip: loop
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, bgr = self.cap.read()
            if ok:
                self.frame = self._to_surface(bgr)
            self.next_t = max(self.next_t + self.period, now - self.period)
        return self.frame if self.frame is not None else self._pattern(now)

    def _pattern(self, now):
        w, h = self.size
        hue = (self.number * 90 + now * 10) % 360
        s = pygame.Surface(self.size)
        c = pygame.Color(0); c.hsva = (hue, 60, 70, 100)
        s.fill(c)
        x = int((math.sin(now + self.number) * 0.4 + 0.5) * w)
        pygame.draw.line(s, (255, 255, 255), (x, 0), (x, h), max(2, w // 80))
        font = pygame.font.Font(None, h // 2)
        label = font.render(str(self.number), True, (255, 255, 255))
        s.blit(label, label.get_rect(center=(w // 2, h // 2)))
        return s


# --- The patch logic -------------------------------------------------------------------

def decide(senses, now):
    """Turn what the Pi senses into a target brightness per wall (four numbers, 0..1)
    and a turn of the whole room (-1..1). This is the part to rewrite in rehearsal."""
    if senses.solo:
        return [1.0 if i + 1 == senses.solo else 0.0 for i in range(4)], senses.tilt

    faces = senses.faces if now - senses.faces_t < 60 else 0  # held for a minute, then reset
    voices = max(1, min(4, 1 + faces // FACES_PER_VOICE))      # nobody seen: one voice remains

    gains = []
    for i in range(4):
        centre = (i + 0.5) / 4                                  # walls at 1/8, 3/8, 5/8, 7/8
        near = max(0.0, 1.0 - abs(senses.x - centre) / SPREAD)  # 1 where you stand, 0 far away
        g = FLOOR + (1 - FLOOR) * near + LOUD_BOOST * senses.level * near
        # The voices that are "in" are the ones nearest the performer.
        rank = sorted(range(4), key=lambda j: abs(senses.x - (j + 0.5) / 4)).index(i)
        gains.append(min(1.0, g) if rank < voices else 0.0)
    return gains, senses.tilt


# --- Drawing ---------------------------------------------------------------------------

def place(layout, size):
    """Where each of the four channels goes on the one output, and how big a channel is."""
    w, h = size
    if layout == "2x2":  # for a 1-in-4-out HDMI video wall controller in 2x2 mode
        cw, ch = w // 2, h // 2
        return [(0, 0), (cw, 0), (0, ch), (cw, ch)], (cw, ch)
    cw, ch = w // 4, h                       # 4x1: one long strip
    return [(i * cw, 0) for i in range(4)], (cw, ch)


def draw_overlay(screen, senses, gains, fps):
    font = pygame.font.Font(None, 28)
    lines = [f"faces {senses.faces}   performer x {senses.x:.2f}   mic {senses.level:.2f}   "
             f"tilt {senses.tilt:+.2f}   solo {senses.solo or 'auto'}   "
             f"{'HOLD' if senses.hold else ''}   {fps:.0f} fps",
             "walls " + "  ".join(f"{g:.2f}" for g in gains),
             "   ".join(f"{k}: {v}" for k, v in senses.status.items())]
    y = 10
    if senses.camera_view is not None:
        rgb = cv2.cvtColor(senses.camera_view, cv2.COLOR_BGR2RGB)
        screen.blit(pygame.image.frombuffer(rgb.tobytes(), (320, 180), "RGB"), (10, y))
        y += 190
    for line in lines:
        img = font.render(line, True, (255, 255, 0), (0, 0, 0))
        screen.blit(img, (10, y)); y += 30


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--media", type=Path, help="folder with ch1, ch2, ch3, ch4 inside")
    ap.add_argument("--layout", choices=["2x2", "4x1"], default="2x2")
    ap.add_argument("--size", default="1920x1080", help="output size (default 1920x1080)")
    ap.add_argument("--fullscreen", action="store_true")
    ap.add_argument("--camera", type=int, default=0, help="camera number (default 0)")
    ap.add_argument("--mic", default=None, help="microphone name or number (default: system default)")
    ap.add_argument("--osc-port", type=int, default=9000, help="port for N900 tilt and cues (default 9000)")
    ap.add_argument("--isadora", help="HOST:PORT, also send faces/x/level to Isadora over OSC")
    ap.add_argument("--seconds", type=float, default=0, help="quit after this long (for testing)")
    args = ap.parse_args()

    size = tuple(int(n) for n in args.size.lower().split("x"))
    mic = int(args.mic) if args.mic and args.mic.isdigit() else args.mic

    pygame.init()
    pygame.mouse.set_visible(not args.fullscreen)
    flags = pygame.FULLSCREEN if args.fullscreen else 0
    screen = pygame.display.set_mode(size, flags)
    pygame.display.set_caption("Five Dimensions")
    size = screen.get_size()
    spots, cell = place(args.layout, size)
    channels = [Channel(i + 1, args.media / f"ch{i + 1}" if args.media else None, cell) for i in range(4)]
    for c in channels:
        print(f"channel {c.number}: {c.source}")

    senses, stop = Senses(), threading.Event()
    for target, extra in ((camera_thread, args.camera), (audio_thread, mic), (osc_thread, args.osc_port)):
        threading.Thread(target=target, args=(senses, extra, stop), daemon=True).start()

    out = None
    if args.isadora:
        host, port = args.isadora.rsplit(":", 1)
        out, out_addr, next_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM), (host, int(port)), 0.0

    clock, start = pygame.time.Clock(), time.monotonic()
    gains, turn, overlay = [0.0] * 4, 0.0, False
    strip = pygame.Surface((cell[0] * 4, cell[1]))
    dark = pygame.Surface(cell)
    try:
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q)):
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_d:
                        overlay = not overlay
                    elif e.key == pygame.K_SPACE:
                        senses.hold = not senses.hold
                    elif pygame.K_0 <= e.key <= pygame.K_4:
                        senses.solo = e.key - pygame.K_0
            now = time.monotonic()
            dt = clock.get_time() / 1000 or 1 / 30

            if not senses.hold:
                target, target_turn = decide(senses, now)
                for i in range(4):  # smooth: voices fade, the light follows
                    rate = dt / (VOICE_FADE if (target[i] == 0) != (gains[i] == 0) else FOLLOW)
                    gains[i] += (target[i] - gains[i]) * min(1.0, rate)
                turn += (target_turn - turn) * min(1.0, dt / FOLLOW)

            # The four walls as one ring; the N900 tilt turns the ring.
            for i, c in enumerate(channels):
                strip.blit(c.surface(now), (i * cell[0], 0))
                dark.set_alpha(int(255 * (1 - max(0.0, min(1.0, gains[i])))))
                strip.blit(dark, (i * cell[0], 0))
            shift = int(turn * cell[0]) % strip.get_width()
            screen.fill((0, 0, 0))
            for i, (x, y) in enumerate(spots):
                src = (i * cell[0] - shift) % strip.get_width()
                part = min(cell[0], strip.get_width() - src)
                screen.blit(strip, (x, y), pygame.Rect(src, 0, part, cell[1]))
                if part < cell[0]:
                    screen.blit(strip, (x + part, y), pygame.Rect(0, 0, cell[0] - part, cell[1]))

            if overlay:
                draw_overlay(screen, senses, gains, clock.get_fps())
            pygame.display.flip()

            if out and now >= next_send:
                for msg in (osc_message("/fivedim/faces", senses.faces),
                            osc_message("/fivedim/x", senses.x),
                            osc_message("/fivedim/level", senses.level)):
                    out.sendto(msg, out_addr)
                next_send = now + 0.1

            if args.seconds and now - start > args.seconds:
                return
            clock.tick(30)
    finally:
        stop.set()
        pygame.quit()


if __name__ == "__main__":
    main()
