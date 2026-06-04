import cv2
import numpy as np
import socketio
import time

# Callback function for trackbars
# This function does nothing, but it's required by OpenCV
def nothing(x):
    pass

# --- 1. Connect to the Server ---
sio = socketio.Client()
@sio.event
def connect():
    print("Successfully connected to simulation server!")
@sio.event
def connect_error(data):
    print("Failed to connect to simulation server.")
@sio.event
def disconnect():
    print("Disconnected from simulation server.")

try:
    sio.connect('http://127.0.0.1:5000')
except socketio.exceptions.ConnectionError as e:
    print(f"Connection Error: Is your 'app.py' server running?")
    exit()

# --- 2. Start Your Webcam ---
print("Starting live fire detection...")
print("Press 'q' to quit.")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sio.disconnect()
    exit()

# Create the Tuner Window
# We are creating a new window named "Trackbars"
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 600, 300)

# Create 6 trackbars for H, S, V (Low and High)
# H (Hue): 0-179 (OpenCV uses 0-179 for Hue)
cv2.createTrackbar("H_low", "Trackbars", 10, 179, nothing)
cv2.createTrackbar("H_high", "Trackbars", 40, 179, nothing)

# S (Saturation): 0-255
# Set to our last known "strict" values to filter skin
cv2.createTrackbar("S_low", "Trackbars", 170, 255, nothing)
cv2.createTrackbar("S_high", "Trackbars", 255, 255, nothing)

# V (Value/Brightness): 0-255
# Set to our last known "strict" values to filter skin
cv2.createTrackbar("V_low", "Trackbars", 170, 255, nothing)
cv2.createTrackbar("V_high", "Trackbars", 255, 255, nothing)

# Create 1 trackbar for MIN_AREA
# Max is 30,000 pixels, default is 1000
cv2.createTrackbar("MIN_AREA", "Trackbars", 1000, 30000, nothing)

# We kernel defined here now
kernel = np.ones((9, 9), np.uint8)

# This variable prevents from flooding the server
fire_detected_last_frame = False

#Start the Real-Time Loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    #Run Detection Logic
    
    # Read values from the trackbars in real-time
    h_low = cv2.getTrackbarPos("H_low", "Trackbars")
    h_high = cv2.getTrackbarPos("H_high", "Trackbars")
    s_low = cv2.getTrackbarPos("S_low", "Trackbars")
    s_high = cv2.getTrackbarPos("S_high", "Trackbars")
    v_low = cv2.getTrackbarPos("V_low", "Trackbars")
    v_high = cv2.getTrackbarPos("V_high", "Trackbars")
    MIN_AREA = cv2.getTrackbarPos("MIN_AREA", "Trackbars")
    
    # Create the HSV arrays from the slider values
    lower_fire = np.array([h_low, s_low, v_low])
    upper_fire = np.array([h_high, s_high, v_high])
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    final_mask = cv2.inRange(hsv, lower_fire, upper_fire)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fire_detected_this_frame = False
    for contour in contours:
        # Read the MIN_AREA value directly from the slider
        if cv2.contourArea(contour) > MIN_AREA: 
            fire_detected_this_frame = True
            
            #Draw the Bounding Box
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "FIRE DETECTED", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
            
    #  Show the Result
    cv2.imshow("Mask", final_mask)
    cv2.imshow("Live Fire Detection (Press 'q' to quit)", frame)

    # Tell the Server 
    if fire_detected_this_frame and not fire_detected_last_frame:
        print("ALERT: Fire DETECTED! Telling robot to move.")
        sio.emit('fire_detected', {'x': 5, 'y': 5}) # Tell robot to go to (5,5)
    
    if not fire_detected_this_frame and fire_detected_last_frame:
        print("ALERT: Fire GONE! Telling robot to return.")
        sio.emit('fire_gone') # Tell robot to return to (9,9)
        
    fire_detected_last_frame = fire_detected_this_frame

    # Check if the user pressed the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean Up
print("Shutting down...")
cap.release()
cv2.destroyAllWindows()
sio.disconnect()

