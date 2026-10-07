# Five Dimensions

A live performance built from my family's war archive. Four walls of video carry four
voices that never shared a room. I stand in the middle as the fifth, and the room, the
audience and a phone call to my dead grandfather decide what happens next.

**Status:** proposal · Week 7 of 15
**Course:** PSAM 5600 B, Small Linux Devices, Large Language Models
Parsons School of Design, Fall 2026

> ⚠️ The show doesn't run yet. Parts of it do: see *Where it stands*. This README will
> be rewritten as things actually work.

![First try: moving in front of the projection in the studio](docs/images/first-try-1.jpg)

## What it is

My grandmother Großi was a child who played hide and seek with war planes. Her brother
Andreas was seventeen behind a heavy machine gun, singing. My grandfather Erwin left
thirty minutes of recorded voice, five hundred pages of letters from the front, and
silence. Eighty years later, nobody in my family can sit in one room and go through
this together.

So I'm building the room. Everything goes into one place I call **the Pot**: the
recordings, the letters, the photos. A machine does the patient work of transcribing,
translating and dating, and turns every piece into a fragment that points back to its
recording minute or letter page. On stage, four projection channels each belong to one
voice. The fifth dimension is me, live in the room, asking the questions I didn't dare
to ask.

| Channel | Voice |
|---|---|
| 1 | **Großi**, the child under the planes |
| 2 | **Andreas**, seventeen, singing behind the gun |
| 3 | **Erwin**, thirty minutes of voice, five hundred pages, silence |
| 4 | **The record**: documents, dates, history, what the family left out |
| 5 | **Me**, in the room |

**The one rule:** where the Pot has no source, it says "unknown". I'm allowed to fill
the gray area with my own hopes and fantasies. The machine isn't. There is one
deliberate exception, and the audience is told about it (see *The call*).

## Why

I want people to see the architectural space *and* the digital space of the room we
are all standing in, in a completely new way. Projections, language models and code are
abstract and distant things; I want to make them tangible, responding to my body, my
voice, the space, and the particular set of people present that day. No two
performances should be alike: rather than playing back a fixed composition, the system
reads the room it is in and responds.

I intend this to be frontier avant garde work, and collaborating with AI openly rather
than quietly is part of that provocation.

## How it works

1. **The Pot (before the show).** Recordings, 500+ pages of front-line letters and
   photos go in raw. Each piece becomes a cited fragment: who, when, the minute or
   page it came from, German and English. A large model does the synthesis ahead of
   time; on stage, a small self-hosted model may only *choose* a fragment I already
   approved. It never invents one.
2. **The room (Isadora on the MacBook).** A camera counts the faces in the audience
   and follows my body. The more people in the room, the more voices open. My movement
   moves the video across the four channels, and tilting the Nokia N900 in my hand
   shifts and tilts the whole projection.
3. **The call (N900 + Raspberry Pi 5).** The N900 becomes a phone again. It rings, I
   pick up, and the Pi listens to what I say. My grandfather answers in a voice
   reconstructed from his thirty recorded minutes. He speaks freely, grounded in the
   Pot but not limited to it. This is the one place where the machine is allowed into
   the gray area, and the audience is told so before it happens.

If anything is slow, confused or offline, the current cue holds and the show goes on.

## The three devices

| Device | Role |
|---|---|
| **MacBook Pro M4 Max** (36 GB) | The mothership. Isadora renders the four channels, reads the camera, and speaks the reconstructed voice. |
| **Nokia N900** (Maemo 5, 2009) | The body and the phone: tilt to move the projection, pick up to make the call. Borrowed from the course's Nokia Devices Library. |
| **Raspberry Pi 5** (16 GB) | The ears and the go-between: hears me, asks the model, sends cues to the Mac. |

The Pi 5 and the N900 are both small Linux devices, the two halves of what this course
is named after, sixteen years apart. Both run Linux built on Debian, so the same
commands work on each. The difference is scale: 245 MB of RAM on the N900 against
16 GB on the Pi. The Pi has the power, the N900 has the body.

## Care

The archive belongs to people who are still alive, and to two who can no longer answer.

- **Consent.** I recorded Erwin without asking, and can no longer ask. Großi I ask
  while she can answer, and again. Each relative decides what of theirs goes in.
- **The reconstructed voice.** On the call, a machine speaks as my grandfather and says
  things he never said. It is the one deliberate exception to the rule above, and the
  audience is told so before it happens.
- **Privacy.** Transcription stays on my own computer. Sending anything to a cloud
  service is a choice I make per material, never a default.
- **Showing.** My family hears it before an audience does. Public versions can hide
  names. The archive itself is never published; this repo holds code and documentation,
  not the family's recordings or letters.

## Where it stands (Week 7)

- **Four-channel video projection works** in Isadora, and reacts to me: the live camera
  reads the room, counts faces, and sends cues based on what it sees.
- **Isadora takes cues from another machine over the network**, tested from a second
  computer to mine.
- **The Raspberry Pi 5 is on Wi‑Fi** and I can reach it from my Mac. The first Pi
  script, which sends cues to Isadora, is in this repo (see *Setup*) but hasn't run on
  the Pi yet.
- Claude writes Isadora logic for me in minutes, so I can try ideas fast.
- The archive is collected but not yet organized.

**First try** (video stills): four-channel projection in the studio, with me moving in
front of it.

| | |
|---|---|
| ![Standing in front of the projection](docs/images/first-try-2.jpg) | ![Walking along the projected wall](docs/images/first-try-3.jpg) |

## Not yet (known behaviour)

- The N900 isn't charged or connected, so I haven't read its tilt sensor or loaded the
  game I programmed for it. The call doesn't exist yet.
- The Pi has no microphone or camera yet, and nothing on it talks to the Mac yet.
- There is no performance room yet, and the projector setup depends on that room.

## Next steps

- [ ] Organize the archive into the Pot: inventory first, then a pilot with Erwin's
      thirty minutes and ten letters
- [ ] Run `pi/hello_isadora.py` on the Pi and see the cues arrive in Isadora
- [ ] Give the Pi ears: a clip-on microphone and offline speech-to-text
- [ ] Charge the N900, read its tilt sensor, load my game, and use the tilt in Isadora
      to shift the whole projection
- [ ] Build the call: N900, Pi and Mac talking to each other
- [ ] Bring in my 6K footage of birds and roads in Bucharest as the visual layer
- [ ] Find the room, then plan the projectors around it

## Setup

**First link: the Pi sends cues to Isadora over Wi‑Fi**
([`pi/hello_isadora.py`](pi/hello_isadora.py), standard-library Python, nothing to
install).

1. On the Mac, in Isadora: add an **OSC Listener** and turn on OSC input on port 1234.
2. On the Pi, with the Mac and the Pi on the same Wi‑Fi:
   ```
   git clone https://github.com/Grossi-thisisforyou/five-dimensions
   cd five-dimensions/pi
   python3 hello_isadora.py MAC_IP_ADDRESS
   ```
3. The Pi prints `sent cue 1`, `sent cue 2`, … and Isadora receives `/fivedim/cue`
   with the numbers 1 to 4, one for each projection channel.

## Co-authorship

Developed with AI models, named explicitly, as course policy and as method.

- **Claude Opus 5:** setup, repository structure, first documentation
- **Claude Opus 5.5:** Week 7 pitch update (how it works, care, status, first Pi script)
- **Claude Fable 5.1:** Week 7 README rework for coherence

Commits carry `Co-Authored-By:` trailers naming the model that contributed, so the
history is a record of the collaboration rather than a claim made afterward.

## License

[MIT](LICENSE). Anyone may use, modify and build on this work provided the copyright
notice is kept. A performance system is more useful to other artists if they can take
it apart.
