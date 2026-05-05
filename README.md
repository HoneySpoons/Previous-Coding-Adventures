# Previous Coding Adventures

I have an A.A.S. in Math/Science from a community college. I work in architectural millwork — reading drawings, modeling complex custom pieces in CAD, managing the production side of commercial construction jobs. I've been tinkering with code since around 2020, mostly self-directed, mostly chasing things I wanted to understand rather than credentials I wanted to earn.

This repo is honest about what it is: artifacts from someone learning by doing, with AI as a collaborator. You'll find some clean work in here. You'll also find the fingerprints of curiosity over expertise. That's intentional.

---

## How I actually work

My workflow is built around an LLM-powered markdown vault — a personal knowledge base with persistent memory, automation scripts, and a wiki layer that compounds across sessions. I've written about that system in detail [here](https://www.linkedin.com/pulse/i-built-personal-ai-remembers-everything-heres-exact-setup-andresen-qnqse/) (also on [GitHub Gist](https://gist.github.com/HoneySpoons/98b8e9ae8804e21413d68da9916541b1)).

What that means practically: when I don't understand what the computer is doing, I ask the computer. When a script isn't working, I debug with the AI in the loop. When a concept is fuzzy — Descartes' Circle Theorem, Runge-Kutta integration, complex exponentials — I ask questions until it isn't fuzzy anymore, and then I write code that makes the thing visible.

The AI made me a faster and more honest learner, not a shortcut around learning. The scripts in this repo grew exponentially better once that workflow was in place. Not because the AI wrote them for me, but because I could finally ask better questions about what I was building.

---

## Math Explorations (`math/`)

Scripts that use `numpy` and `matplotlib` to make complex math functions visible and interactive. Started as ways to understand things I was curious about. Kept growing.

### `apollonian_gasket.py`

Interactive fractal explorer. Three mutually tangent circles generate a fourth; apply recursively, forever. Built on Descartes' Circle Theorem:

```
(k₁ + k₂ + k₃ + k₄)² = 2(k₁² + k₂² + k₃² + k₄²)
```

Sliders for the three starting curvatures and recursion depth. Scroll to zoom. Animated reveal by generation — circles fade in one depth level at a time. The theorem renders inline on the canvas. The interesting thing about the gasket is what lives in the spaces between the circles: more circles, all the way down.

### `double_pendulum.py`

Chaotic system simulation. Two pendulum arms, one pivot. Drag either bob to a new position and release — the system re-solves from that initial condition and runs a new trajectory. Small change in starting position, completely different path. The equations of motion render in a live panel beside the animation. Uses `scipy.integrate.solve_ivp` with RK45.

### `pi_spiral.py`

Animation of z(θ) = e^(iθ) + e^(iπθ) in the complex plane. Two rotations added together — one rational frequency, one irrational. The curve never closes. Simple script, but it makes something abstract immediately apparent.

**Requirements:**
```
pip install numpy matplotlib scipy
```

---

## Holomat (`holomat/`)

My first attempt at building something like persistent memory AI. Around 2022–2023 I was following a maker called ConceptBytes who was building a holographic desk interface — projecting your screen onto a surface, using hand tracking to control it, always-on mic, GPT connected. The idea was a sort of ambient AI that lived in your physical workspace.

I got part of it working. The hand tracking runs: index finger and thumb pinch gesture as click, fingertip midpoint as cursor, mapped to screen coordinates via MediaPipe and PyAutoGUI. It works. It's clunky. The projector I got from a coworker is still in the box, and the script that was supposed to connect the mic to ChatGPT lives somewhere else on my hard drive.

Too ambitious for the skill level I had at the time. The gap between the concept and the execution was humbling. I'm further along now.

**Requirements:** `opencv-python`, `mediapipe`, `pyautogui`, `numpy`

---

## Changelog App

A mobile-first changelog tool built in React Native / Expo. Runs on iOS, Android, and web.

I built it for my actual job. Commercial millwork production moves fast — scope changes, material delays, GC-driven pivots — and the standard approach to tracking all of that is a whiteboard or a group text. This app logs changes by job number with a category tag (`#delayed`, `#blocked`, `#scope-change`, `#completed`), a description, and a reason. Filter by job. Timestamped. Persistent.

Dark theme. Single-file architecture. AsyncStorage on device.

→ **[changelog-app repo — link coming]**

---

## What's next

The math scripts are what I want to put in front of people interactively — a simple website where you can run them in a browser without installing anything. That's the next project.

The vault system I work in is documented in a plain-language guide I'm publishing soon. It's written for someone with no assumed technical background and covers how to build a personal knowledge base that compounds across AI sessions. If you're curious about the workflow described above, that's where to start.

---

*Dan Andresen — Rensselaer, NY*
