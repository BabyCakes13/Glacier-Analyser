from __future__ import print_function
import cv2
import numpy as np
import os
import definitions

VALID_HOMOGRAPHIES = 0
TOTAL_PROCESSED = 0


class Align:
    def __init__(self, reference_8bit, current_image8bit):

        self.reference_8bit = reference_8bit
        self.current_image_8bit = cv2.normalize(current_image8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

        self.result_8bit = None
        self.matches = None

    def find_matches(self):
        """Returns whether the homography finding was succesfull or not."""
        # transform from scientific notation to decimal for easy check
        np.set_printoptions(suppress=True, precision=4)

        orb = cv2.ORB_create(definitions.MAX_FEATURES)

        keypoints1, descriptors1 = orb.detectAndCompute(self.reference_8bit, None)
        keypoints2, descriptors2 = orb.detectAndCompute(self.current_image_8bit, None)

#        print("Keypoints 1 length ", len(keypoints1))
#        print("Keypoints 2 length ", len(keypoints2))
#        print("Descriptor 1 ", descriptors1)
#        print("Descriptor 2 ", descriptors2)

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)
        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)
        # remove matches with low score
        numGoodMatches = int(len(matches) * definitions.GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]
        # draw the best matches
        self.matches = cv2.drawMatches(self.reference_8bit, keypoints1, self.current_image_8bit,
                                       keypoints2, matches, None)
#        self.display_image('MATCHES', self.matches)

        # prepare the arras which hold the matches location
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)
        # fill points from the matcher
        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # find homography
        homography, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

        print("Homography \n", homography)

        # generate result
        height, width = self.reference_8bit.shape
        self.result_8bit = cv2.warpPerspective(self.reference_8bit, homography, (width, height))

    @staticmethod
    def display_image(window_name, image):
        """Display the image in a window."""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.moveWindow(window_name, 10, 10)
        cv2.imshow(window_name, image)

        while cv2.waitKey() != 27:
            pass


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

    aligner.display_image("Rerefence", aligner.reference_8bit)
    aligner.display_image("Current Image", aligner.current_image_8bit)
    aligner.display_image("Result", aligner.result_8bit)

    cv2.destroyAllWindows()


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

