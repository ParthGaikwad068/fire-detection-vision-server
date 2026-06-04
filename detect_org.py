import cv2
import numpy as np

print("Starting fire detection...")

# --- Step 1: Load your test image ---
# We load the image from the file
frame = cv2.imread('test_fire.jpg')

# Error check: Make sure the image loaded
if frame is None:
    print("Error! Could not load 'test_fire.jpg'")
    print("Make sure the image is in the same folder as the script.")
    exit()

# --- Step 2: Convert to HSV Color Space ---
# BGR (default) is bad for color. HSV is good.
# H = Hue (the color), S = Saturation (purity), V = Value (brightness)
# This is the 'HSV Conversion' step [cite: 85]
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
print("Converted image to HSV.")

# --- Step 3: Define HSV Thresholds for Fire ---
# This is the 'Dual-Threshold Masking' [cite: 85]
# Fire is reddish-orange. Red wraps around 0 and 180 in HSV.
# So, we need two separate ranges.

# Range 1: Covers the lower end of red (e.g., dark oranges)
lower_red_1 = np.array([0, 150, 150])   # H_low, S_low, V_low
upper_red_1 = np.array([10, 255, 255])  # H_high, S_high, V_high

# Range 2: Covers the upper end of red (e.g., pinkish reds)
lower_red_2 = np.array([170, 150, 150]) # H_low, S_low, V_low
upper_red_2 = np.array([180, 255, 255]) # H_high, S_high, V_high

# --- Step 4: Create the Masks ---
# A 'mask' is a black-and-white image. White pixels are
# 'fire', black pixels are 'not fire'.
mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

# Combine the two masks into one.
# This finds all pixels that are in *either* range.
final_mask = cv2.add(mask1, mask2)
print("Created fire masks.")

# --- Step 5: Clean Up the Mask (Noise Reduction) ---
# We use 'morphology' to remove small white dots (false positives)
# This makes our detection much more stable.
kernel = np.ones((5, 5), np.uint8)
final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)
final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_DILATE, kernel)
print("Cleaned up mask noise.")


# --- Step 6: Find Fire Contours (Shapes) ---
# This finds all continuous white shapes in our mask [cite: 85]
contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Found {len(contours)} potential fire contours.")

# --- Step 7: Filter Contours and Draw Boxes ---
# This is the 'Size/Location Filtering' step [cite: 85]
fire_detected = False
for contour in contours:
    # We filter by 'area'. This is the *most important* tuning step.
    # It rejects small, random white dots that aren't big enough to be a fire.
    area = cv2.contourArea(contour)
    
    if area > 1000:  # <--- TUNE THIS VALUE!
        print(f"Detected a significant contour with area: {area}")
        fire_detected = True
        
        # Get the (x, y) coordinates and width/height of the fire
        x, y, w, h = cv2.boundingRect(contour)
        
        # Draw the green rectangle on the ORIGINAL frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, "FIRE", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

if not fire_detected:
    print("No significant fire contours found.")

# --- Step 8: Show The Results ---
# We display the final image with the boxes
cv2.imshow("Original Image with Fire Detection", frame)

# We also show the black-and-white mask for debugging
cv2.imshow("Fire Mask (What the AI Sees)", final_mask)

print("\nShowing results. Press any key to exit.")
cv2.waitKey(0)  # Wait until the user presses a key
cv2.destroyAllWindows() # Close all windows