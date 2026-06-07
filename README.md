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

## Project Evolution
This project was developed in three distinct engineering phases to systematically solve false-positive detections and integrate autonomous navigation:

* **Stage 1: Kaggle Dataset & Bounding Boxes**
  * Began by utilizing static training images from Kaggle to establish baseline bounding box mechanics and basic visual identification.
* **Stage 2: HSV Filtering & False-Positive Rejection**
  * Transitioned to live webcam feeds. Engineered a custom OpenCV pipeline using precise HSV masking to eliminate static bright lights and walls. 
  * Implemented temporal persistence and pixel-fluctuation algorithms to successfully differentiate between chaotic fire and static red/orange clothing.
* **Stage 3: A* Pathfinding Integration**
  * Built a Flask/SocketIO web simulation. The vision server dynamically broadcasts fire coordinates to a simulated autonomous agent, which calculates the optimal, obstacle-free route using the A* pathfinding algorithm to "extinguish" the target.

## Installation
This project uses a virtual environment to manage dependencies for clean, reproducible execution.

1. Clone the repository:
   ```bash
   git clone [https://github.com/ParthGaikwad068/fire-detection-vision-server.git](https://github.com/ParthGaikwad068/fire-detection-vision-server.git)
   cd fire-detection-vision-server

## Demonstration


## Future Roadmap
This project is under active development. Planned hardware and software integrations include:
- [ ] **Depth Perception (Distance Mapping):** Implementing stereoscopic or monocular depth estimation to output the real-world distance (in meters) from the camera to the fire source.
- [ ] **Hardware Deployment:** Transitioning the A* simulation agent into a physical, wheeled rover equipped with an extinguishing mechanism for real-world testing.