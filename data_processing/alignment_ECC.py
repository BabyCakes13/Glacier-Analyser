from __future__ import print_function
import cv2
import numpy as np
import os
import definitions

VALID_HOMOGRAPHIES = 0
TOTAL_PROCESSED = 0


class Align:
    def __init__(self, im_reference_16bit, im_tobe_aligned_16bit, im_reference, im_tobe_aligned):
        self.im1_16bit = im_tobe_aligned_16bit
        self.im2_16bit = im_reference_16bit

        self.im1_8bit = (self.im1_16bit >> 8).astype(np.uint8)
        self.im2_8bit = (self.im2_16bit >> 8).astype(np.uint8)

        self.big_im_reference_8bit = self.im2_16bit >> 8
        self.big_im_tobe_aligned_8bit = self.im1_16bit >> 8

        self.im_matches = None
        self.im_result = None
        self.homography = None

    def find_matches(self):
        """Returns whether the homography finding was succesfull or not."""
        # detect ORB features and descriptors
        # Read the images to be aligned

        # Find size of image1
        sz = self.im1_8bit.shape

        # Define the motion model
        print("Define motion model...")
        warp_mode = cv2.MOTION_TRANSLATION

        # Define 2x3 or 3x3 matrices and initialize the matrix to identity
        print("Define motion homography")
        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            warp_matrix = np.eye(3, 3, dtype=np.float32)
        else:
            warp_matrix = np.eye(2, 3, dtype=np.float32)

        # Specify the number of iterations.
        number_of_iterations = 1000

        # Specify the threshold of the increment
        # in the correlation coefficient between two iterations
        termination_eps = 1e-10

        # Define termination criteria
        print("Define criteria")
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

        print("Run algorithm")
        # Run the ECC algorithm. The results are stored in warp_matrix.
        (cc, warp_matrix) = cv2.findTransformECC(self.im1_8bit, self.im2_8bit, warp_matrix, warp_mode, criteria)

        print("Wrap matrix ", warp_matrix)

        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            # Use warpPerspective for homography
            print("Wrap perspective 1")
            self.im_result = cv2.warpPerspective(self.im2_8bit, warp_matrix, (sz[1], sz[0]),
                                              flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        else:
            print("Wrap perspective 2")
            # Use warpAffine for Translation, Euclidean and Affine
            self.im_result = cv2.warpAffine(self.im2_8bit, warp_matrix, (sz[1], sz[0]),
                                         flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);

        # Show final results
        self.setup_windows()

    def setup_windows(self):
        cv2.namedWindow('Reference', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference', 1000, 1000)
        cv2.moveWindow('Reference', 10, 10)
        cv2.imshow('Reference', self.im2_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('imp', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('imp', 1000, 1000)
        cv2.moveWindow('imp', 10, 10)
        cv2.imshow('imp', self.im1_8bit)

        while cv2.waitKey() != 27:
            pass

        """cv2.namedWindow('Differences', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Differences', 1000, 2000)
        cv2.moveWindow('Differences', 10, 10)
        cv2.imshow('Differences', self.im_matches)

        while cv2.waitKey() != 27:
            pass"""

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


def percentage(percent, image):
    """Find what is percent from whole."""
    height, width = image.shape
    height = (percent * height) // 100
    width = (percent * width) // 100

    print("Height ", height)
    print("Width ", width)

    return (width, height)


def setup_alignment(reference_filename, image_filename, result_filename, processed_output_dir):
    print("Rreference image is: \n", reference_filename)
    print("To be aligned image is: \n", image_filename)

    """
    im_reference = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)
    im_tobe_aligned = cv2.imread(image_filename, cv2.IMREAD_LOAD_GDAL)

    scaled_im_reference = cv2.resize(im_reference, percentage(20, im_reference))
    scaled_im_tobe_aligned = cv2.resize(im_tobe_aligned, percentage(20, im_tobe_aligned))

    aligned_path = os.path.join(processed_output_dir, result_filename)

    aligner = Align(scaled_im_reference, scaled_im_tobe_aligned, im_reference, im_tobe_aligned)
    found = aligner.find_matches()
    valid = aligner.validate_homography()
#    aligner.setup_windows()

    print(VALID_HOMOGRAPHIES, "/", TOTAL_PROCESSED, "\n")
    if found and valid:
        cv2.imwrite(aligned_path, aligner.im_result)
        """

# scale image up, wrap matrix elements by x percent sko it fist.



