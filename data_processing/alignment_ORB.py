from __future__ import print_function
import cv2
import numpy as np
import os
import sys

DISPLAY=0

# align
MAX_FEATURES = 1500
GOOD_MATCH_PERCENT = 0.10
ALLOWED_ERROR = 0.05
ALLOWED_INTEGRAL = 100

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

        orb = cv2.ORB_create(MAX_FEATURES)

        keypoints_ref, descriptors_ref = orb.detectAndCompute(self.reference_8bit, None)
        keypoints_img, descriptors_img = orb.detectAndCompute(self.current_image_8bit, None)

#        print("Keypoints 1 length ", len(keypoints_ref))
#        print("Keypoints 2 length ", len(keypoints_img))
#        print("Descriptor 1 ", descriptors_ref)
#        print("Descriptor 2 ", descriptors_img)

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors_ref, descriptors_img, None)
        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)
        # remove matches with low score
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]
        # draw the best matches
        if (DISPLAY):
            self.matches = cv2.drawMatches(self.reference_8bit, keypoints_ref,
                                           self.current_image_8bit, keypoints_img, matches,
                                           None, matchColor=(0,255,0), singlePointColor=(100,0,0),
                                           flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            self.display_image('MATCHES', self.matches)

        # prepare the arras which hold the matches location
        points_ref = np.zeros((len(matches), 2), dtype=np.float32)
        points_img = np.zeros((len(matches), 2), dtype=np.float32)
        # fill points from the matcher
        for i, match in enumerate(matches):
            points_ref[i, :] = keypoints_ref[match.queryIdx].pt
            points_img[i, :] = keypoints_img[match.trainIdx].pt

        # find homography
        homography, mask = cv2.findHomography(points_img, points_ref, cv2.RANSAC)
        VALID = self.validate_homography(homography)

        # generate result
        height, width = self.reference_8bit.shape
        self.result_8bit = cv2.warpPerspective(self.current_image_8bit, homography, (width, height))

        return VALID

    def validate_homography(self, homography):
        # convert from scientific notation to decimal notation for better data interpretation
        np.set_printoptions(suppress=True, precision=4)


        identity = np.identity(3)
        difference = np.absolute(np.subtract(identity, homography))
        compare = self.create_comparison_matrix()

        print("Homography \n", homography)
        print("Difference \n", difference)
        print("Comparison \n", compare)

        if np.less_equal(difference, compare).all():
            print("Homography is good.")
            return True
        else:
            print("Homography is not good.")
            return False

    @staticmethod
    def create_comparison_matrix():
        """Creates the matrix for comparing."""
        comparison = np.full((3, 3), ALLOWED_ERROR)
        comparison[0, 2] = ALLOWED_INTEGRAL
        comparison[1, 2] = ALLOWED_INTEGRAL

        return comparison

    @staticmethod
    def display_image(window_name, image):
        """Display the image in a window."""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.moveWindow(window_name, 10, 10)
        cv2.imshow(window_name, image)

    @staticmethod
    def display_image_flush():
        while cv2.waitKey() != 27:
            pass

def percentage(percent, image) -> tuple:
    """Find what is percent from whole."""
    height, width = image.shape
    height = (percent * height) // 100
    width = (percent * width) // 100

    return width, height


def start_alignment(reference_filename, image_filename, result_filename, processed_output_dir):
    """Starts the alignment process."""
    result_path = os.path.join(processed_output_dir, result_filename)
    print_messages(reference_filename, image_filename, result_path)

    # prepare the images for alignment
    normalised_reference_8bit, current_image_8bit, \
    scaled_normalised_reference_8bit, scaled_current_image_8bit = resize_depth(reference_filename, image_filename)

    aligner = Align(normalised_reference_8bit, current_image_8bit)
    VALID = aligner.find_matches()

    if VALID:
        cv2.imwrite(result_path, aligner.result_8bit)

    if(DISPLAY):
        aligner.display_image("Rerefence", aligner.reference_8bit)
        aligner.display_image("Current Image", aligner.current_image_8bit)
        aligner.display_image("Result", aligner.result_8bit)
        aligner.display_image_flush()

    cv2.destroyAllWindows()

    return VALID

def print_messages(reference_filename, image_filename, aligned_filename):
    print("\n\n")
    print("Reference filename: ", reference_filename)
    print("Image filename ", image_filename)
    print("Aligned filename  ", aligned_filename)


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

if __name__ == "__main__":
    try:
        VALID = start_alignment(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    except KeyboardInterrupt:
        sys.exit(3)
    except:
        sys.exit(5)

    if(VALID):
        sys.exit(0)
    else:
        sys.exit(1)
