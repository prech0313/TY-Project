import cv2
import numpy as np

# Read the image.
#image_path = 'C://Vs Code//images//img.jpg'
image = cv2.imread('C://Vs Code//images//img.jpg')

# Define the centers of the two circles.
center1 = (100, 100)
center2 = (200, 200)

# Calculate the Euclidean distance between the centers of the two circles.
calculated_distance = np.linalg.norm(np.array(center1) - np.array(center2))

# Define the reference distance with the desired accuracy.
reference_distance = 100  # In the same unit as the calculated distance (e.g., millimeters)

# Calculate the absolute error (precision) and the relative error (accuracy).
absolute_error = abs(reference_distance - calculated_distance)
relative_error = (absolute_error / reference_distance) * 100

print("Calculated Distance:", calculated_distance)
print("Reference Distance:", reference_distance)
print("Absolute Error (Precision):", absolute_error)
print("Relative Error (Accuracy):", relative_error, "%")

# Display the image.
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
