import cv2
import numpy as np

def find_circles(image, dp=1.7, minDist=100, param1=50, param2=50, minRadius=0, maxRadius=0):
    # Same implementation of find_circles function as provided earlier
    # ...

# Initialize the video capture object
cap = cv2.VideoCapture(0)  # 0 for default camera, change the number if you have multiple cameras

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Preprocess the frame (e.g., thresholding, blurring, edge detection)
    # Here, you can apply any preprocessing steps before finding circles

    # Find circles in the preprocessed frame
    circles = find_circles(gray)

    if circles is not None:
        # Draw the detected circles on the frame
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # Draw the outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # Draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
