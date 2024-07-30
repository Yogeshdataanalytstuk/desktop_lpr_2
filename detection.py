import cv2
import numpy as np

def detch(prev, current, threshold=25, min_contour_area=400):


    # Convert frames to grayscale and apply Gaussian blur
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    current_gray = cv2.GaussianBlur(current_gray, (21, 21), 0)

    # Compute the absolute difference between the previous and current frames
    frame_diff = cv2.absdiff(prev_gray, current_gray)

    # Threshold the difference to get the significant changes
    _, thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=2)
    
    # Find contours of the significant changes
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Check if any contour is significant
    for contour in contours:
        if cv2.contourArea(contour) >= min_contour_area:
            return 1
    
    return 0