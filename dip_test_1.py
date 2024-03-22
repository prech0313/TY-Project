import cv2
import numpy as np
import pandas as pd

def find_circles(image, dp=1.7, minDist=100, param1=50, param2=50, minRadius=0, maxRadius=0):
    # Function to find circles remains the same as before
    # ...

def find_od():
    cap = cv2.VideoCapture(0)  # Access the default camera (change the index if you have multiple cameras)
    result_df = pd.DataFrame(columns=["measured_dia_pixels", "center_in_pixels"])

    while True:
        ret, frame = cap.read()  # Capture frame-by-frame from the webcam

        if not ret:
            print("Error: Failed to capture frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh_img = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        thresh_img = cv2.bilateralFilter(thresh_img, 5, 91, 91)
        edges = cv2.Canny(thresh_img, 100, 200)

        circles = find_circles(edges, dp=1.7, minDist=100, param1=50, param2=30, minRadius=685, maxRadius=700)

        if circles is not None:
            circles = np.squeeze(circles)
            result_df.loc[len(result_df)] = circles[2] * 2, (circles[0], circles[1])

        cv2.imshow('Frame', frame)  # Display the frame with detected circles

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit the loop if 'q' is pressed
            break

    cap.release()  # Release the webcam
    cv2.destroyAllWindows()  # Close all OpenCV windows

    return result_df

df = find_od()
mean_d = df.measured_dia_pixels.mean()
std_deviation = np.sqrt(np.mean(np.square([abs(x - mean_d) for x in df.measured_dia_pixels])))

mm_per_pixel = 0.042
print(std_deviation * mm_per_pixel)
