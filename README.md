# Five Dimensions

A live performance system in which a 2009 Nokia N900 becomes a haptic controller for
multichannel video projection, while a Raspberry Pi 5 on stage listens, reacts and
recues the projections in real time.

**Status:** proposal · Week 7 of 15
**Course:** PSAM 5600 B, Small Linux Devices, Large Language Models
Parsons School of Design, Fall 2026

> ⚠️ The show doesn't run yet. Some parts already work: see *Where it stands*. This
> README describes the intent and will be rewritten as things actually work.

![First try: moving in front of the projection in the studio](docs/images/first-try-1.jpg)

## The idea

I want to build a performance environment that is heavily influenced by the space the
performance happens in. My goal is for people to see the architectural space *and* the
digital space of the room we are all standing in, in a completely new way.

The second goal is my own presence inside it: up to eight channels of video projection
responding to my body, my voice, the space itself, and the unique set of audience
members present on that particular day. Projections, LLMs and code are abstract and
distant things. I want to make them tangible.

I intend this to be frontier avant garde work, and collaborating with AI openly rather
than quietly is part of that provocation.

No two performances should be alike. Rather than playing back a fixed composition, the
system reads the room it is in and responds.

## The three devices

| Device | Role |
|---|---|
| **MacBook Pro M4 Max** (36 GB) | The mothership. Renders and drives the projection channels. |
| **Nokia N900** (Maemo 5, 2009) | The haptic link to the physical world: tilt, touch, vibration. Borrowed from the course's Nokia Devices Library. |
| **Raspberry Pi 5** (16 GB) | The agent on the ground, in the space, reacting and altering. |

The Pi 5 and the N900 are both small Linux devices, the two halves of what this course
is named after, sixteen years apart. Both run Linux built on Debian, so the same
commands work on each. The difference is scale: 245 MB of RAM on the N900 against
16 GB on the Pi. The Pi has the power, the N900 has the body.

## How it works

Five Dimensions turns my family's war archive into a room you can stand inside.

1. **The Pot (before the show).** Recordings, 500+ pages of front-line letters and photos go in raw. Each piece becomes a cited fragment: who, when, the minute or page it came from, German and English. Where there is no source, it says "unknown".
2. **The call (N900 + Raspberry Pi 5).** The N900 becomes a phone again. It rings, I pick up, and the Pi listens to what I say. My grandfather answers in a voice reconstructed from his 30 recorded minutes. He speaks freely, grounded in the Pot but not limited to it: the one place in the piece where the machine is allowed into the gray area, and the audience is told so.
3. **The room (Isadora on the MacBook).** A camera counts the faces in the audience and follows my body. The more people in the room, the more voices open; my movement moves the video across four channels: Großi, Andreas, Erwin, and the record.

If anything is slow or offline, the current cue holds and the show goes on.

## Care

The archive belongs to people who are still alive, and to two who can no longer answer.

- **Consent.** I recorded Erwin without asking, and can no longer ask. Großi I ask while she can answer, and again. Each relative decides what of theirs goes in.
- **The reconstructed voice.** On the call, a machine speaks as my grandfather and says things he never said. It is the one deliberate exception to the rule that the machine never fills the gray area, and the audience is told so before it happens.
- **Privacy.** Transcription stays on my own computer. Sending anything to a cloud service is a choice I make per material, never a default.
- **Showing.** My family hears it before an audience does. Public versions can hide names. The archive itself is never published; this repo holds code and documentation, not the family's recordings or letters.

## Where it stands (Week 7)

- **Raspberry Pi 5 is on Wi‑Fi** and I can reach it over my home network.
- **Four-channel video projection works** in Isadora.
- **Isadora reads the live video** and sends cues to the computer based on what it sees (for example, how many faces are in the room).
- **Isadora can take cues from another machine**: tested from a second computer to mine.
- Claude writes Isadora logic for me in minutes, so I can try ideas fast.
- The archive is collected but not yet organized.

**First try** (video stills): four-channel projection in the studio, with me moving in front of it.

| | |
|---|---|
| ![Standing in front of the projection](docs/images/first-try-2.jpg) | ![Walking along the projected wall](docs/images/first-try-3.jpg) |

## Not yet (known behaviour)

- The N900 isn't charged or connected yet, so I haven't read its tilt sensor or loaded the game I programmed for it.
- There is no performance room yet, and the projector setup depends on that room.

## Next steps

- [ ] Organize the archive into the Pot: inventory first, then a pilot with Erwin's 30 minutes and ten letters
- [ ] Charge the N900, read its tilt sensor, and load my game
- [ ] Join the trinity: N900, Pi and Mac talking to each other
- [ ] Use the N900's tilt in Isadora to shift and tilt the whole projection
- [ ] Give the Pi eyes and ears: a microphone first, then a camera
- [ ] Connect the Pi to Isadora the same way my two-computer test worked
- [ ] Find the room, then plan the projectors around it
- [ ] Bring in my 6K footage of birds and roads in Bucharest as the visual layer
- [ ] Build the N900 call

## Setup

**First link: the Pi sends cues to Isadora over Wi‑Fi** ([`pi/hello_isadora.py`](pi/hello_isadora.py), standard-library Python, nothing to install).

1. On the Mac, in Isadora: add an **OSC Listener** and turn on OSC input on port 1234.
2. On the Pi, with the Mac and the Pi on the same Wi‑Fi:
   ```
   git clone https://github.com/Grossi-thisisforyou/five-dimensions
   cd five-dimensions/pi
   python3 hello_isadora.py MAC_IP_ADDRESS
   ```
3. The Pi prints `sent cue 1`, `sent cue 2`, … and Isadora receives `/fivedim/cue` with the numbers 1 to 4, one for each projection channel.

## Co-authorship

Developed with AI models, named explicitly, as course policy and as method.

- **Claude Opus 5:** setup, repository structure, documentation
- **Claude Opus 5.5:** Week 7 pitch update (how it works, status, next steps)
- **Claude Fable 5.1:** planned

Commits carry `Co-Authored-By:` trailers naming the model that contributed, so the
history is a record of the collaboration rather than a claim made afterward.

## License

[MIT](LICENSE). Anyone may use, modify and build on this work provided the copyright
notice is kept. A performance system is more useful to other artists if they can take
it apart.
