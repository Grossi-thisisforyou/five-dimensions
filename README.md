# Five Dimensions

A live performance system in which a 2009 Nokia N900 becomes a haptic controller for
multichannel video projection, while a Raspberry Pi 5 on stage listens, reacts, and
re-cues the projections in real time.

**Status:** concept · Week 4 of 15
**Course:** PSAM 5600 B — Small Linux Devices, Large Language Models
Parsons School of Design, Fall 2026

> ⚠️ Early days. Nothing here runs yet. This README describes the intent and the
> architecture being built toward; it will be rewritten as things actually work.

---

## The idea

I want to build a performance environment that is heavily influenced by the space the
performance happens in. My goal is for people to see the architectural space *and* the
digital space — of the room we are all standing in — in a completely new way.

The second goal is my own presence inside it: up to eight channels of video projection
responding to my body, my voice, the space itself, and the unique set of audience
members present on that particular day. Projections, LLMs and code are abstract and
distant things. I want to make them tangible.

I intend this to be frontier avant-garde work, and collaborating with AI openly rather
than quietly is part of that provocation.

The aim is that no two performances are alike — that the room, the day, and the
particular set of people present all change what happens. Rather than playing back a
fixed composition, the system reads the space it is in and responds.

## The three devices

| Device | Role |
|---|---|
| **MacBook Pro M4 Max** (36 GB) | The mothership — renders and drives the projection channels |
| **Nokia N900** (Maemo 5, 2009) | The haptic link to the physical world — tilt, touch, vibration. Borrowed from the course's Nokia Devices Library. |
| **Raspberry Pi 5** (16 GB) | The agent on the ground — in the space, reacting, delegating, altering |

The N900 is the reason this is a *small Linux device* project. It runs Maemo 5, a real
Debian-based Linux, and carries a 3-axis accelerometer, a resistive touchscreen and a
vibration motor in a device that predates the App Store. Tilting it moves projected
image through the room.

## Where this is going

Ordered smallest-first. Each step is meant to work before the next begins.

- [ ] **MVP** — tilt the N900, one projection channel moves. One device, one input,
      one output, visible in a room.
- [ ] Raspberry Pi 5 on the network, receiving and relaying events
- [ ] Multiple projection channels (building toward 6–8)
- [ ] Live voice input altering the projection in real time
- [ ] Audience interaction
- [ ] A full performance

## Setup

<!-- TODO: once the MVP runs, a stranger must be able to set this up from here.
     Hardware, wiring, install steps, how to start it. The rubric grades exactly
     this. Write it as you go, not at the end. -->

Not yet — there is nothing to run.

## Co-authorship

This project is co-developed with AI models, named explicitly, as a course
requirement and as a matter of method.

- **Claude Opus 5** — setup, repository structure, documentation
- **Claude Fable 5.1** — planned

Commits carry `Co-Authored-By:` trailers naming the model that contributed, so the
history is a legible record of the collaboration rather than a claim made after the
fact.

## License

[MIT](LICENSE) — anyone may use, modify and build on this work provided the copyright
notice is kept. Chosen because a performance system is more useful to other artists if
they can take it apart and adapt it.
