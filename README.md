# Real-Time Fire Detection & Dispatch Server

## Overview
This project is a real-time computer vision server designed to detect live fires using standard webcams. Instead of relying solely on heavy machine learning models, this system utilizes a highly optimized OpenCV pipeline to identify fire based on color, persistence, and dynamic behavioral traits.

Upon positive detection, the server acts as a dispatcher, broadcasting target coordinates via SocketIO to a linked autonomous robot simulation.

## Key Features & Engineering Logic
* **Multi-Layered Filtering:** Uses precise HSV color space masking to isolate high-saturation, high-value colors, effectively ignoring bright white walls and shadows.
* **Dynamic Flicker Detection:** Overcomes the standard "red shirt" false-positive problem. The algorithm tracks rapid pixel-count fluctuations across consecutive frames, differentiating between static orange objects and the chaotic, fluctuating nature of a real flame.
* **Temporal Persistence:** Requires fire to be detected across multiple consecutive frames before triggering an alert, heavily reducing noise and false positives.
* **Real-Time Telemetry:** Integrates a Flask-SocketIO server to instantly emit `fire_detected` (with coordinates) or `fire_gone` payloads to robotic clients.
* **Hardware Optimized:** Implements immediate frame downscaling and frame-skipping logic to run smoothly on standard CPUs without requiring dedicated GPU acceleration.

## Tech Stack
* **Language:** Python 3.x
* **Computer Vision:** OpenCV (`opencv-python`), NumPy
* **Networking:** Flask, Flask-SocketIO

## Installation
This project uses a virtual environment to manage dependencies for clean, reproducible execution.

1. Clone the repository:
   ```bash
   git clone [https://github.com/ParthGaikwad068/fire-detection-vision-server.git](https://github.com/ParthGaikwad068/fire-detection-vision-server.git)
   cd fire-detection-vision-server