# Five Dimensions

A live performance system in which a 2009 Nokia N900 becomes a haptic controller for
multichannel video projection, while a Raspberry Pi 5 on stage listens, reacts and
recues the projections in real time.

**Status:** concept · Week 4 of 15
**Course:** PSAM 5600 B, Small Linux Devices, Large Language Models
Parsons School of Design, Fall 2026

> ⚠️ Nothing here runs yet. This README describes the intent and the architecture
> being built toward. It will be rewritten as things actually work.

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

## Where this is going

Smallest first. Each step works before the next begins.

- [ ] **MVP:** tilt the N900, one projection channel moves
- [ ] Raspberry Pi 5 on the network, receiving and relaying events
- [ ] Multiple projection channels, building toward eight
- [ ] Live voice input altering the projection
- [ ] Audience interaction
- [ ] A full performance

## Setup

<!-- TODO: write this as you build, not at the end. A stranger must be able to set it
     up from here: hardware, install steps, how to start it. -->

Nothing to run yet.

## Co-authorship

Developed with AI models, named explicitly, as course policy and as method.

- **Claude Opus 5:** setup, repository structure, documentation
- **Claude Fable 5.1:** planned

Commits carry `Co-Authored-By:` trailers naming the model that contributed, so the
history is a record of the collaboration rather than a claim made afterward.

## License

[MIT](LICENSE). Anyone may use, modify and build on this work provided the copyright
notice is kept. A performance system is more useful to other artists if they can take
it apart.
