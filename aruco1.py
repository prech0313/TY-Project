import cv2
import numpy as np

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Function to detect circles in an image and calculate distances from the ArUco marker
def detect_circles_with_distance(frame, aruco_corners, aruco_marker_size):
    if aruco_corners is not None:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (9, 9), 2)

        # Use the Hough Circle Transform to detect circles
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=10, maxRadius=50)

        if circles is not None:
            # Convert circle coordinates to integer
            circles = np.round(circles[0, :]).astype("int")

            for (x, y, r) in circles:
                # Draw the circle in the original frame
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

                # Calculate the distance from the ArUco marker to the center of the circle
                aruco_center = np.mean(aruco_corners[0], axis=0)
                circle_center = (x, y)
                distance = calculate_distance(aruco_center, circle_center)

                # Display the distance on the frame
                cv2.putText(frame, f"Distance: {distance:.2f}", (x - 30, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return frame

# Create an ArUco dictionary
aruco_dict = cv2.aruco.Dictionary_create(6, 250)

# Initialize the ArUco marker detector
aruco_params = cv2.aruco.DetectorParameters_create()

# Open a connection to the webcam (you may need to change the argument if you have multiple cameras)
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect ArUco markers in the frame
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    # Draw detected ArUco markers
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Assume the first detected ArUco marker as the reference marker
        if len(corners) > 0:
            aruco_corners = corners[0]
            aruco_marker_size = cv2.norm(aruco_corners[0] - aruco_corners[1])

            # Detect circles and calculate distances using the reference marker
            frame = detect_circles_with_distance(frame, aruco_corners, aruco_marker_size)

    # Display the result
    cv2.imshow("ArUco Marker and Circle Detection", frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
