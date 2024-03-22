import cv2
import diplib

# Read the image. Make sure the path is properly formatted.
image_path = r'C:\Vs Code\images\CMM img.jpg'
image = cv2.imread(image_path)

# Define the coordinates of the two circles.
x1, y1 = 0, 0
x2, y2 = 1, 1

# Define the radii of the two circles.
r1 = 0.5
r2 = 0.5

# Calculate the distance between the two circles.
distance = diplib.distance_between_circles(x1, y1, r1, x2, y2, r2)

# Print the distance.
print("The distance between the two circles is:", distance)

# Display the image. Make sure to include this part if you want to show the image.
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
