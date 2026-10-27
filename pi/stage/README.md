# The room, on the Raspberry Pi

Isadora runs on macOS and Windows only, so it can't run on the Pi. `stage.py` is a
standalone program that does what the Isadora patch does, so the Pi can run the room
without the Mac:

| In the patch | In `stage.py` |
|---|---|
| The camera counts faces: more people, more voices | 1 voice when nobody is seen, 1 more per face, up to 4 |
| The camera follows me: my movement moves the video across the four channels | the wall nearest to where I stand is brightest; the others fall back |
| (new) the microphone | the louder I am, the brighter the wall I'm at |
| Tilting the N900 shifts the whole projection | OSC `/fivedim/tilt` (-1..1) turns the four walls like a ring |
| If anything fails, the current cue holds | each sensor keeps its last value; Space freezes everything |

All of that is in one function, `decide()`, and a few numbers at the top of the file
(`FLOOR`, `SPREAD`, `VOICE_FADE` ...). Changing those is how the piece changes.

## What to plug in

```
USB camera ──┐                              ┌── projector 1
USB mic    ──┤   Raspberry Pi 5   HDMI 0 ───┤── projector 2   (HDMI video wall
             │   stage.py --layout 2x2      ├── projector 3    controller, 1 in,
Wi-Fi: N900, │                              └── projector 4    4 out, 2x2 mode)
the Mac ─────┘
```

- **Four projectors.** A Pi 5 has two HDMI outputs, not four. The simplest way to four
  is one output into an *HDMI video wall controller* (1 input, 4 outputs, set to 2x2):
  `stage.py` draws the four channels as four quarters of one picture, and the box sends
  each quarter to one projector. All four stay in sync because it's one picture.
  The other way is two Pis with two projectors each; that needs the Pis to keep in
  step over the network, which isn't written yet.
- **Camera:** a USB webcam. (A Pi Camera Module works too, but needs extra setup.)
- **Microphone:** a USB microphone or a small USB audio interface. The Pi 5 has no
  microphone input of its own.

## Setup, on the Pi

```
git clone https://github.com/Grossi-thisisforyou/five-dimensions
cd five-dimensions/pi/stage
bash install.sh
python3 stage.py
```

You should see four coloured test walls numbered 1 to 4. Press **D** to see what the
Pi senses: the camera picture with green boxes on faces, the face count, where you
stand, the microphone level, and a line saying `camera: ok   mic: ok`. If one says
"no camera" or "no microphone", that input isn't plugged in or isn't found.

## Your footage

Put one video (or one picture) in each of `~/media/ch1` to `~/media/ch4`, then

```
python3 stage.py --media ~/media --fullscreen
```

The Pi can't play four 6K videos at once. Make a small copy of each clip first, on the
Mac, at the size of one wall (960×540 when the whole picture is 1920×1080):

```
ffmpeg -i bucharest-birds.mov -vf scale=960:540 -c:v libx264 -crf 20 -an ch1.mp4
```

## Keys and cues

| Key | OSC (port 9000) | Does |
|---|---|---|
| 1 to 4 | `/fivedim/solo 1` .. `4` | only that wall |
| 0 | `/fivedim/solo 0` | back to automatic |
| Space | `/fivedim/hold 1` / `0` | hold the picture as it is |
| | `/fivedim/tilt 0.3` | turn the room (from the N900) |
| D | | show the sensors |
| Esc | | quit |

To test cues from another computer, the first script works:
`python3 ../hello_isadora.py PI_ADDRESS --port 9000 --address /fivedim/solo`
cycles the solo through walls 1 to 4.

With `--isadora MAC_ADDRESS:1234`, the Pi also sends what it senses to Isadora
(`/fivedim/faces`, `/fivedim/x`, `/fivedim/level`), so the Mac can stay as the backup.

## Not yet tested

- On a real Pi 5 with a real camera, microphone and video wall controller. It was run
  on a Linux computer with test videos, pictures and OSC cues.
- Face counting uses OpenCV's simple face finder. In a dark theatre it will miss
  faces; an infrared light on the audience, or a better model, would help.
- `install.sh --autostart` (start the show when the Pi turns on).
