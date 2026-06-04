import cv2
import numpy as np

print("Starting fire detection...")

# Load  test image
frame = cv2.imread("test_fire.jpg.png")

# Making sure the image is loaded
if frame is None:
    print("Error! Could not load 'test_fire.jpg'")
    print("Make sure the image is in the same folder as the script.")
    exit()

# Step 2: Convert to HSV Color Space 
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
print("Converted image to HSV.")

#Define high and low threshold values
lower_fire = np.array([8, 0, 192]) 
upper_fire = np.array([32, 252, 255]) 

# Create the Mask 
final_mask = cv2.inRange(hsv, lower_fire, upper_fire)
print("Created fire masks.")

# Clean Up the Mask 
# We use 'morphology' to remove small white dots (false positives)
kernel = np.ones((5, 5), np.uint8)
final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)
final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_DILATE, kernel)
print("Cleaned up mask noise.")


# Find Fire Contours
contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Found {len(contours)} potential fire contours.")

# Filter Contours and Draw Boxes 
fire_detected = False
for contour in contours:
    # We filter by 'area'. 
    # It rejects small, random white dots that aren't big enough to be a fire.
    area = cv2.contourArea(contour)
    
    if area > 1000:  
        print(f"Detected a significant contour with area: {area}")
        fire_detected = True
        
        # Get the (x, y) coordinates and width/height of the fire
        x, y, w, h = cv2.boundingRect(contour)
        
        # Draw the green rectangle on the ORIGINAL frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, "FIRE", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

if not fire_detected:
    print("No significant fire contours found.")

# We display the final image with the boxes
cv2.imshow("Original Image with Fire Detection", frame)

# We also show the black-and-white mask for debugging
cv2.imshow("Fire Mask (What the AI Sees)", final_mask)

print("\nShowing results. Press any key to exit.")
cv2.waitKey(0)  # Wait until the user presses a key
cv2.destroyAllWindows() # Close all windows