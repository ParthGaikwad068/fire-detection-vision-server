import cv2
import numpy as np

# --- IMPORTANT: ---
# Change this filename to match your image's EXACT name!
# Use the 'dir' command in your terminal if you are unsure.
IMAGE_TO_TUNE = 'test_fire.jpg.png' 
# e.g., 'test_fire.jpg.jpg' or 'test_fire (1).jpg'


# This function does nothing, but it's required for the trackbars
def nothing(x):   
    pass

# --- Setup ---
# Load the image you want to test on
frame = cv2.imread(IMAGE_TO_TUNE)
if frame is None:
    print(f"Error loading {IMAGE_TO_TUNE}. Make sure it's in the folder.")
    print("Check the IMAGE_TO_TUNE variable in this script.")
    exit()

# Resize image if it's too big, to make sure all windows fit
scale = 0.5 # 50%
width = int(frame.shape[1] * scale)
height = int(frame.shape[0] * scale)
frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

# Convert to HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# --- Create the Trackbar Window ---
# This window will have all our sliders
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 600, 300)

# Create 6 trackbars for H, S, V (Low and High)
# H (Hue): 0-179 (OpenCV uses 0-179 for Hue, not 180)
cv2.createTrackbar("H_low", "Trackbars", 10, 179, nothing)
cv2.createTrackbar("H_high", "Trackbars", 40, 179, nothing)

# S (Saturation): 0-255
cv2.createTrackbar("S_low", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("S_high", "Trackbars", 255, 255, nothing)

# V (Value/Brightness): 0-255
cv2.createTrackbar("V_low", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("V_high", "Trackbars", 255, 255, nothing)

print("\n--- HSV Tuner Tool ---")
print(f"Tuning for image: {IMAGE_TO_TUNE}")
print("\nInstructions:")
print("1. Move the sliders to isolate the fire in the 'Mask' window.")
print("   GOAL: Make the fire a SOLID WHITE blob.")
print("2. Press 's' to save and print your values to the terminal.")
print("3. Press 'q' to quit.")

while True:
    # --- Read slider values ---
    h_low = cv2.getTrackbarPos("H_low", "Trackbars")
    h_high = cv2.getTrackbarPos("H_high", "Trackbars")
    s_low = cv2.getTrackbarPos("S_low", "Trackbars")
    s_high = cv2.getTrackbarPos("S_high", "Trackbars")
    v_low = cv2.getTrackbarPos("V_low", "Trackbars")
    v_high = cv2.getTrackbarPos("V_high", "Trackbars")

    # --- Create the mask ---
    lower_bound = np.array([h_low, s_low, v_low])
    upper_bound = np.array([h_high, s_high, v_high])
    
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # --- Show the original image and the mask ---
    cv2.imshow("Original Image", frame)
    cv2.imshow("Mask (Your Goal: Solid White Fire)", mask)

    # --- Key controls ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        print("\n--- SAVED VALUES (Copy these into detect.py) ---")
        print(f"lower_fire = np.array([{h_low}, {s_low}, {v_low}])")
        print(f"upper_fire = np.array([{h_high}, {s_high}, {v_high}])")
        print("--------------------------------------------------")

cv2.destroyAllWindows()