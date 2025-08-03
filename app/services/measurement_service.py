# In app/services/measurement_service.py

import cv2
import mediapipe as mp
import numpy as np
import base64
import math

# Initialize MediaPipe Pose solution
mp_pose = mp.solutions.pose

def estimate_measurements_from_photo(photo_base64: str, user_height_cm: float):
    """
    Estimates body measurements from a base64 encoded photo using the user's height as a scale reference.

    Args:
        photo_base64: The base64 encoded string of the user's photo (may include Data URI header).
        user_height_cm: The user's actual height in centimeters.

    Returns:
        A dictionary with estimated measurements or None if detection fails.
        An error message string or None if successful.
    """
    try:
        # --- FIX: Handle Data URI Headers ---
        # If the string is a Data URI, strip out the header before decoding.
        if "," in photo_base64:
            base64_data = photo_base64.split(',')[1]
        else:
            base64_data = photo_base64
        
        # 1. Decode the Base64 image
        img_data = base64.b64decode(base64_data)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Sanity check: Ensure image decoding was successful
        if image is None:
            return None, "Failed to decode image. The Base64 string may be corrupt."
        
        image_height, image_width, _ = image.shape

        # 2. Process the image with MediaPipe Pose
        with mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=True) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if not results.pose_landmarks:
                return None, "Could not detect a person in the photo. Please use a clear, full-body picture."

            landmarks = results.pose_landmarks.landmark

            # 3. The Scaling Logic: Convert pixels to real-world measurements
            # Find the highest and lowest detected points of the body to get pixel height
            
            # Using Nose and the average of Heels as top/bottom reference points
            # This is a simplification; a professional system would use a more robust reference.
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL]
            right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL]

            top_y_px = nose.y * image_height
            bottom_y_px = ((left_heel.y + right_heel.y) / 2) * image_height
            person_height_px = abs(bottom_y_px - top_y_px)

            if person_height_px == 0:
                return None, "Could not calculate the person's pixel height in the image."

            # Calculate the scaling factor
            cm_per_pixel = user_height_cm / person_height_px

            # 4. Estimate Measurements
            
            # Estimate Shoulder Width
            left_shoulder_px = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * image_width
            right_shoulder_px = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * image_width
            shoulder_width_cm = abs(left_shoulder_px - right_shoulder_px) * cm_per_pixel

            # Estimate Waist Width (using left and right hips as a reference)
            left_hip_px = landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * image_width
            right_hip_px = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * image_width
            waist_width_cm = abs(left_hip_px - right_hip_px) * cm_per_pixel

            # Heuristics for circumference from width (simplified)
            # A more sophisticated model would use 3D pose estimation.
            estimated_chest_circumference = shoulder_width_cm * math.pi
            estimated_waist_circumference = waist_width_cm * math.pi

            estimated_measurements = {
                "chest_circumference_cm": round(estimated_chest_circumference, 2),
                "waist_circumference_cm": round(estimated_waist_circumference, 2),
                "shoulder_width_cm": round(shoulder_width_cm, 2)
            }

            return estimated_measurements, None

    except Exception as e:
        # Catch any other unexpected errors during processing
        return None, f"An error occurred during image processing: {str(e)}"