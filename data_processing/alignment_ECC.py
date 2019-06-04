from __future__ import print_function
import cv2
import numpy as np
import os
import time
import definitions

VALID_HOMOGRAPHIES = 0
TOTAL_PROCESSED = 0


class Align:
    def __init__(self, scaled_reference_16bit, scaled_image_16bit, reference_16bit, image_16bit):
        scaled_reference_16bit = scaled_reference_16bit
        scaled_image_16bit = scaled_image_16bit

        print("16 bits scaled")
        print(scaled_image_16bit.shape)
        print(scaled_reference_16bit.shape)

        self.scaled_reference_8bit = (scaled_reference_16bit >> 8).astype(np.uint8)
        self.scaled_image_8bit = (scaled_image_16bit >> 8).astype(np.uint8)

        print("8 bits scaled")
        print(self.scaled_reference_8bit.shape)
        print(self.scaled_image_8bit.shape)

        self.normal_reference_8bit = (reference_16bit >> 8).astype(np.uint8)
        self.normal_image_8bit = (image_16bit >> 8).astype(np.uint8)

        print("8 bits normal")
        print(self.normal_reference_8bit.shape)
        print(self.normal_image_8bit.shape)

        self.im_result = None
        self.homography = None

    def find_matches(self):
        """Returns whether the homography finding was succesfull or not."""
        # detect ORB features and descriptors
        # Read the images to be aligned

        # Find size of image1
        sz = self.scaled_reference_8bit.shape

        # Define the motion model
        print("Define motion model...")
        warp_mode = cv2.MOTION_AFFINE

        # Define 2x3 or 3x3 matrices and initialize the matrix to identity
        print("Define motion homography")
        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            warp_matrix = np.eye(3, 3, dtype=np.float32)
        else:
            warp_matrix = np.eye(2, 3, dtype=np.float32)

        # Specify the number of iterations.
        number_of_iterations = 50

        # Specify the threshold of the increment
        # in the correlation coefficient between two iterations
        termination_eps = 0.001

        # Define termination criteria
        print("Define criteria")
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

        print("Run algorithm")
        # Run the ECC algorithm. The results are stored in warp_matrix.
        (cc, warp_matrix) = cv2.findTransformECC(self.scaled_reference_8bit, self.scaled_image_8bit, warp_matrix, warp_mode, criteria)

        print("Wrap matrix \n", warp_matrix)

        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            # Use warpPerspective for homography
            print("Wrap perspective 1")
            self.im_result = cv2.warpPerspective(self.scaled_image_8bit, warp_matrix, (sz[1], sz[0]),
                                                 flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        else:
            print("Wrap perspective 2")
            # Use warpAffine for Translation, Euclidean and Affine
            self.im_result = cv2.warpAffine(self.scaled_image_8bit, warp_matrix, (sz[1], sz[0]),
                                            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);

    def setup_windows(self):
        print("Reference shape ", self.scaled_reference_8bit.shape)
        cv2.namedWindow('Reference', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference', 1000, 1000)
        cv2.moveWindow('Reference', 10, 10)
        cv2.imshow('Reference', self.scaled_reference_8bit)

        while cv2.waitKey() != 27:
            pass

        print("Current image shape ", self.scaled_image_8bit.shape)
        cv2.namedWindow('Current Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Current Image', 1000, 1000)
        cv2.moveWindow('Current Image', 10, 10)
        cv2.imshow('Current Image', self.scaled_image_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Result', 1000, 1000)
        cv2.moveWindow('Result', 10, 10)
        cv2.imshow('Result', self.im_result)

        while cv2.waitKey() != 27:
            pass

        cv2.destroyAllWindows()

    def validate_homography(self):
        np.set_printoptions(suppress=True, precision=4)
        global TOTAL_PROCESSED
        global VALID_HOMOGRAPHIES
        TOTAL_PROCESSED += 1

        identity = np.identity(3)
        comparison = np.full((3, 3), definitions.ALLOWED_ERROR)
        comparison[0, 2] = definitions.ALLOWED_INTEGRAL
        comparison[1, 2] = definitions.ALLOWED_INTEGRAL

        if self.homography is None:
            return False

        difference = np.absolute(np.subtract(identity, self.homography))
        print(difference)

        if np.less_equal(difference, comparison).all():
            VALID_HOMOGRAPHIES += 1
            return True
        else:
            print("Homography is not good.")
            return False


def percentage(percent, image) -> tuple:
    """Find what is percent from whole."""
    height, width = image.shape
    height = (percent * height) // 100
    width = (percent * width) // 100

    return width, height


def setup_alignment(reference_filename, image_filename, result_filename, processed_output_dir):
    # print("Rreference image is: \n", reference_filename)
    # print("To be aligned image is: \n", image_filename)

    reference = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)
    current_image = cv2.imread(image_filename, cv2.IMREAD_LOAD_GDAL)

    scaled_reference = cv2.resize(reference, percentage(20, reference))
    scaled_current_image = cv2.resize(current_image, percentage(20, current_image))

    aligned_path = os.path.join(processed_output_dir, result_filename)

    aligner = Align(scaled_reference, scaled_current_image, reference, current_image)
    found = aligner.find_matches()
    aligner.setup_windows()
    valid = aligner.validate_homography()

    print(VALID_HOMOGRAPHIES, "/", TOTAL_PROCESSED, "\n")
    if found and valid:
        cv2.imwrite(aligned_path, aligner.im_result)
# normalise image up, wrap matrix elements by x percent sko it fist.
