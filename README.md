# 🖱️ Touchless Mouse

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-4B8BBE?style=for-the-badge&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

A webcam-only, gesture-driven mouse controller that lets you move the cursor, click, and scroll using nothing but your hand. Built for shared computers, gloved or wet hands, and anyone who struggles with a physical mouse or touchpad — no extra hardware, no drivers, no cloud services.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Project Context](#project-context)

---

## Features

### 🖐️ Gesture Recognition

- **Strict Five-Gesture Vocabulary** — The engine only recognizes `Move`, `Left Click`, `Right Click`, `Scroll`, and `Idle`. Everything else falls through to `Idle`, so casual hand movement can never trigger an accidental click or scroll.
- **21-Point Hand Landmarking** — MediaPipe extracts fingertips, knuckles, and palm geometry from each frame, giving the recognizer a rich, low-latency hand skeleton.
- **Scale-Invariant Pinch Detection** — Pinch distance is normalized against the measured size of the hand, so click sensitivity stays identical whether the hand is close to or far from the camera.
- **Pinch Hysteresis** — A pinch must be very tight to *begin*, but is allowed to loosen slightly before it *ends*, eliminating the click-flicker that plagued the first prototype.

### 🎯 Cursor Stability & Accuracy

- **Three-Frame Confirmation** — A gesture must be held for three consecutive frames before it registers, so a single corrupted frame can no longer change the application's state.
- **Knuckle-Anchored Tracking** — The cursor follows the index *knuckle* rather than the fingertip. The knuckle barely shifts during a pinch, so the cursor stops slipping off the target button mid-click.
- **Adaptive Smoothing** — Slow hand movement is smoothed aggressively for precision; fast movement is smoothed lightly to preserve responsiveness. Micro-jitter below a configurable threshold is discarded entirely.
- **Single Click Per Pinch** — Each pinch fires exactly one click, followed by a short cooldown before the next is allowed.
- **Latency-Tuned Output** — PyAutoGUI's default action delay is disabled, removing the sluggish feel of the original build.
- **Edge-Reach Mapping** — Only a reduced box within the camera frame is used for tracking, letting the hand reach every screen edge without stretching the arm.

### 🖥️ Live Overlay & Session Control

- **On-Screen HUD** — A live window displays the camera feed, the currently detected gesture, and a compact gesture guide, so the user always knows what the program sees.
- **Keyboard Shortcuts** — Press `P` to pause and `Q` to quit at any time.
- **Fail-Safe Corner Stop** — Moving the *real* mouse into a screen corner immediately halts the program.

### 🧪 Reproducible Test Notebooks

- **Camera-Free Validation** — Four Google Colab notebooks test each pipeline stage independently using uploaded photos, synthetic hand landmarks, and pre-recorded video, with all mouse actions logged to a list instead of executed.
- **Fake-Mouse Simulation** — The control notebook drives a mock mouse object, proving click and scroll logic without touching the host OS.

---

## Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| Hand Tracking & Computer Vision | MediaPipe, OpenCV |
| Gesture Classification Logic | Python 3, NumPy |
| Cursor Kinematics & Smoothing | Pure Python (custom adaptive filter) |
| Mouse / OS Automation | PyAutoGUI |
| Live Overlay Rendering | OpenCV HighGUI |
| Prototyping & Testing | Google Colab, Jupyter Notebook |

---

## System Architecture

1. **Frame Capture** — OpenCV grabs a frame from the webcam inside the main loop, many times per second.
2. **Hand Detection** — MediaPipe locates the hand and returns 21 normalized landmarks (fingertips, knuckles, palm).
3. **Gesture Recognition** — The recognizer evaluates landmark geometry and classifies the frame into one of the five supported gestures, using scale-normalized pinch distances and finger-extension checks.
4. **Temporal Stabilization** — The candidate gesture must persist for three consecutive frames before it is accepted as the active gesture.
5. **Cursor Mapping & Smoothing** — The index knuckle position is mapped from the reduced tracking box onto the full screen resolution and passed through the adaptive smoothing filter.
6. **Action Dispatch** — The mouse controller executes the corresponding action through PyAutoGUI (move, single click, or scroll), respecting click cooldowns.
7. **Overlay Feedback** — The HUD renders the camera view, active gesture, and guide so the user can self-correct in real time.

---

## Getting Started

### Prerequisites

- **Python 3.9 – 3.11** installed and available on your `PATH`
- A working **webcam** (a standard laptop camera is sufficient)
- `pip` package manager
- A display and a real mouse (needed for the corner fail-safe)
- **macOS users:** grant Accessibility permissions to your terminal before running, or PyAutoGUI cannot move the cursor

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/touchless-mouse.git
cd touchless-mouse
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs OpenCV, MediaPipe, PyAutoGUI, and NumPy.

### 3. Launch the Application

```bash
cd src
python main.py
```

### 4. Control the Cursor

```text
Gesture        Action          What Happens
Move           Index finger     Cursor follows your hand
Left click     Thumb + index    One left click
Right click    Thumb + middle   One right click
Scroll         Index + middle   Hand up = scroll up, down = scroll down
Idle           Fist / palm      Nothing happens
```

Press `P` to pause, `Q` to quit, or shove the real mouse into a screen corner to stop the program.

### 5. Run the Colab Notebooks (Optional)

```text
Upload notebooks to Google Colab, then select: Runtime > Run all
```

- `01_hand_tracker.ipynb` — upload a photo; visualizes the 21 landmarks
- `02_gesture_recognizer.ipynb` — runs on its own with synthetic landmarks
- `03_mouse_control.ipynb` — runs on its own against a mock mouse
- `04_main_pipeline.ipynb` — upload a video; reports per-gesture frame counts and simulated actions

### 6. Repository Layout

| File | Purpose |
| :--- | :--- |
| `src/hand_tracker.py` | MediaPipe wrapper returning 21 landmarks |
| `src/gesture_recognizer.py` | Landmark-to-gesture classification |
| `src/mouse_control.py` | Smoothing, click cooldowns, scroll dispatch |
| `src/main.py` | Live pipeline entry point (webcam → HUD → mouse) |
| `requirements.txt` | Pinned dependency list |

> **⚠️ Important:** The live `.py` application requires a physical webcam and a real desktop session. Google Colab runs on a remote machine and **cannot** access your local camera or control your actual cursor — that is why the notebooks deliberately use uploaded photos, synthetic landmarks, and recorded video with a mocked mouse. Also note that detection quality depends on good lighting and a palm facing the camera; the sensitivity constants (pinch thresholds, smoothing factors, cooldowns) live at the top of each source file and may need small per-webcam or per-hand-size adjustments.

---

## API Endpoints

This project is a standalone desktop application and exposes no network services.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| N/A | N/A | No API — all processing runs locally through OpenCV, MediaPipe, and PyAutoGUI |

---

## Project Context

Touchless Mouse began as a simple "control your PC with your hand" experiment and quickly exposed the real engineering problem underneath: the first version technically worked, but it clicked by accident, shook constantly, and gave the user no confidence about what would happen next. This project is the rebuild — a deliberate study in turning a fun demo into a dependable input device through strict gesture vocabulary, temporal confirmation, scale-invariant pinch detection, and adaptive cursor smoothing. It was developed as an academic capstone-style project, with the Colab notebooks included so every stage of the pipeline can be inspected and reproduced without hardware.

<p align="center"><i>Built with Python, MediaPipe, and a stubborn refusal to accept an unreliable demo. 👋</i></p>
