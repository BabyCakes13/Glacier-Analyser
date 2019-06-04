from __future__ import print_function
import cv2
import numpy as np
import os


class Align:
    def __init__(self, reference_8bit, current_image8bit):

        self.reference_8bit = reference_8bit
        self.current_image_8bit = cv2.normalize(current_image8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

        self.result_8bit = None

    def find_matches(self):
        """Returns whether the homography finding was succesfull or not."""
        # transform from scientific notation to decimal for easy check
        np.set_printoptions(suppress=True, precision=4)

        height, width = self.reference_8bit.shape

        # Define the motion model
        warp_mode = cv2.MOTION_TRANSLATION

        # Define 2x3 or 3x3 matrices and initialize the matrix to identity
        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            warp_matrix = np.eye(3, 3, dtype=np.float32)
        else:
            warp_matrix = np.eye(2, 3, dtype=np.float32)

        number_of_iterations = 50
        termination_eps = 0.001

        # Define termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

        print("Run algorithm")
        # Run the ECC algorithm. The results are stored in warp_matrix.
        (cc, warp_matrix) = cv2.findTransformECC(self.reference_8bit, self.current_image_8bit,
                                                 warp_matrix, warp_mode, criteria)

        print("Wrap matrix \n", warp_matrix)

        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            print("Wrap perspective...")
            self.result_8bit = cv2.warpPerspective(self.current_image_8bit, warp_matrix, (width, height),
                                                   flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        else:
            print("Wrap perspective...")
            # Use warpAffine for Translation, Euclidean and Affine
            self.result_8bit = cv2.warpAffine(self.current_image_8bit, warp_matrix, (width, height),
                                              flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    def setup_windows(self):
        """Displays the images for processing."""
        cv2.namedWindow('Reference', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference', 1000, 1000)
        cv2.moveWindow('Reference', 10, 10)
        cv2.imshow('Reference', self.reference_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('Current Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Current Image', 1000, 1000)
        cv2.moveWindow('Current Image', 10, 10)
        cv2.imshow('Current Image', self.current_image_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Result', 1000, 1000)
        cv2.moveWindow('Result', 10, 10)
        cv2.imshow('Result', self.result_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.destroyAllWindows()


def percentage(percent, image) -> tuple:
    """Find what is percent from whole."""
    height, width = image.shape
    height = (percent * height) // 100
    width = (percent * width) // 100

    return width, height


def setup_alignment(reference_filename, image_filename, result_filename, processed_output_dir):

    # prepare the images for alignment
    normalised_reference_8bit, current_image_8bit, \
    scaled_normalised_reference_8bit, scaled_current_image_8bit = resize_depth(reference_filename, image_filename)

    aligned_path = os.path.join(processed_output_dir, result_filename)
    aligner = Align(scaled_normalised_reference_8bit, scaled_current_image_8bit)
    aligner.find_matches()
    aligner.setup_windows()


def resize_depth(reference_filename, image_filename):
    """Resize the depth of the images from 16 to 8 pixels.
    Normalise reference.
    Scale images."""
    reference_16bit = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)
    current_image_16bit = cv2.imread(image_filename, cv2.IMREAD_LOAD_GDAL)

    reference_8bit = (reference_16bit >> 8).astype(np.uint8)
    current_image_8bit = (current_image_16bit >> 8).astype(np.uint8)

    normalised_reference_8bit = cv2.normalize(reference_8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

    scaled_normalised_reference_8bit = cv2.resize(normalised_reference_8bit, percentage(20, normalised_reference_8bit))
    scaled_current_image_8bit = cv2.resize(current_image_8bit, percentage(20, current_image_8bit))

    return normalised_reference_8bit, current_image_8bit, scaled_normalised_reference_8bit, scaled_current_image_8bit

