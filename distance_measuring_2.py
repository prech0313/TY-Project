import cv2
import numpy as np

# Read the original image.
original_image = cv2.imread('F://Vs Code//images//img.jpg')

# Define the scaling factor for resizing (e.g., 2 for doubling the size).
scaling_factor = 2

# Resize the original image.
resized_image = cv2.resize(original_image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_LINEAR)

# Convert the resized image to grayscale.
gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise and improve circle detection.
gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)

# Use the Hough Circle Transform to detect the large circle.
circles = cv2.HoughCircles(
    gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=25, minRadius=10, maxRadius=50
)

if circles is not None:
    circles = np.uint16(np.around(circles))

    # Draw the large circle.
    for idx, circle in enumerate(circles[0]):
        center = (circle[0], circle[1])
        radius = circle[2]
        cv2.circle(resized_image, center, radius, (0, 255, 0), 2)

        # Extract the region of interest (ROI) within the large circle.
        x, y = circle[0] - radius, circle[1] - radius
        w, h = 2 * radius, 2 * radius
        roi = gray[y:y+h, x:x+w]

        # Perform circle detection within the ROI.
        smaller_circles = cv2.HoughCircles(
            roi, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=25, minRadius=5, maxRadius=radius // 2
        )

        if smaller_circles is not None:
            smaller_circles = np.uint16(np.around(smaller_circles))

            # Count and draw the smaller circles inside the large circle.
            for small_circle in smaller_circles[0]:
                small_center = (small_circle[0] + x, small_circle[1] + y)
                small_radius = small_circle[2]
                cv2.circle(resized_image, small_center, small_radius, (0, 0, 255), 2)

                # Calculate the distance, accuracy, and error for each smaller circle.
                reference_point = center  # Use the center of the large circle as the reference.
                actual_distance = np.linalg.norm(np.array(reference_point) - np.array(small_center))
                accuracy = (actual_distance / small_radius) * 100
                error = abs(small_radius - actual_distance)

                # Display distance, accuracy, and error.
                cv2.putText(
                    resized_image,
                    f"Distance: {actual_distance:.2f}",
                    (small_center[0], small_center[1] + small_radius + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    resized_image,
                    f"Accuracy: {accuracy:.2f}%",
                    (small_center[0], small_center[1] + small_radius + 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    resized_image,
                    f"Error: {error:.2f}",
                    (small_center[0], small_center[1] + small_radius + 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                # Label the circles with alphabets.
                label = chr(ord('A') + idx)
                cv2.putText(
                    resized_image,
                    f"Label: {label}",
                    (small_center[0], small_center[1] - small_radius - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

# Display the image with the detected circles, distances, accuracy, error, and labels.
cv2.imshow("Circles Detection", resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
