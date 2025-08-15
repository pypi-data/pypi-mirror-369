import ast
import glob
import cv2
import numpy as np
import os

# Constants
CALIBRATION_FILE = r"D:\office\vision\backend\utils\saved_param\calibration_data.npz"

class CheccboardCalibration:
    def __init__(self):
        pass
    def calibrate_camera(self,SQUARE_SIZE=20,CHESSBOARD_SIZE=(7,7)):
        # SQUARE_SIZE = int(SQUARE_SIZE)
        CHESSBOARD_SIZE=  ast.literal_eval(CHESSBOARD_SIZE)
        """Calibrates the camera and calculates mm per pixel."""
        obj_points = []
        img_points = []
        objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2) * SQUARE_SIZE
        images_folder = r"D:\office\vision\backend\utils\calibration_images"
        images = glob.glob(os.path.join(images_folder, "*.jpg"))
        if not images:
            print(f"Error: No images found in {images_folder}.")
            return None, None, None

        for img_file in images:
            img = cv2.imread(img_file)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

            if ret:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                obj_points.append(objp)
                img_points.append(corners_refined)

        if not obj_points:
            print("Error: No valid chessboard patterns detected.")
            return None, None, None

        ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
            obj_points, img_points, gray.shape[::-1], None, None
        )

        np.savez(CALIBRATION_FILE, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
        var='saved'
        
        return var    
    
    def undistort_image(self,img):

        if os.path.exists(CALIBRATION_FILE):
            data = np.load(CALIBRATION_FILE)
            camera_matrix, dist_coeffs = data["camera_matrix"], data["dist_coeffs"]
        else:
            print("Calibration file not found....")
        h, w = img.shape[:2]
        tangential_only = np.array([0, 0, dist_coeffs[0, 2], dist_coeffs[0, 3], 0])
        new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, tangential_only, (w, h), 1, (w, h))
        undistorted_image=cv2.undistort(img, camera_matrix, tangential_only, None, new_camera_matrix)
        return undistorted_image
