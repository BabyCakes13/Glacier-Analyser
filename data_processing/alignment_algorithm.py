from __future__ import print_function
import numpy as np
import os
import cv2
import definitions

VALID_HOMOGRAPHIES = 0
TOTAL_PROCESSED = 0


class Align:
    def __init__(self, im1_16bit, im2_16bit):
        self.im1_16bit = im1_16bit
        self.im2_16bit = im2_16bit

        self.im1_8bit = (self.im1_16bit >> 8).astype(np.uint8)
        self.im2_8bit = (self.im2_16bit >> 8).astype(np.uint8)

        self.im_matches = None
        self.im_result = None
        self.homography = None

    def find_matches(self) -> bool:
        """Returns whether the homography finding was succesfull or not."""
        # detect ORB features and descriptors

        orb = cv2.ORB_create(definitions.MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(self.im1_8bit, None)
        keypoints2, descriptors2 = orb.detectAndCompute(self.im2_8bit, None)

        print("Keypoints 1 ", len(keypoints1))
        print("Keypoints 2 ", len(keypoints2))
        print("Descriptor 1 ", descriptors1)
        print("Descriptors 2 ", descriptors2)

        if (descriptors1 is None) or (descriptors2 is None):
            print("Descriptor is None. Aborting this image.")
            return False

        # match features
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove not good matches
        numGoodMatches = int(len(matches) * definitions.GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # draw the best matches
        self.im_matches = cv2.drawMatches(self.im1_8bit, keypoints1, self.im2_8bit, keypoints2, matches, None)

        # get good matches location
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

#        print("POINTS 1 ", len(points1))
#        print("POINTS 2 ", len(points2))
        if (len(points1) < 1) or (len(points2) < 1):
            print("Not enough feature points were found. Aborting this image.")
            return False

        # find and apply homography
        self.homography, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
        height, width = self.im2_8bit.shape

        if self.homography is None:
            print("Homography is none. Aborting this image.")
            return False

        self.im_result = cv2.warpPerspective(self.im2_8bit, self.homography, (width, height))
        return True

    def setup_windows(self):
        cv2.namedWindow('Reference', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference', 1000, 1000)
        cv2.moveWindow('Reference', 10, 10)
        cv2.imshow('Reference', self.im1_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('imp', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('imp', 1000, 1000)
        cv2.moveWindow('imp', 10, 10)
        cv2.imshow('imp', self.im2_8bit)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('Differences', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Differences', 1000, 2000)
        cv2.moveWindow('Differences', 10, 10)
        cv2.imshow('Differences', self.im_matches)

        while cv2.waitKey() != 27:
            pass

        cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Result', 1000, 1000)
        cv2.moveWindow('Result', 10, 10)
        cv2.imshow('Result', self.im_result)

        while cv2.waitKey() != 27:
            pass

        cv2.destroyAllWindows()

    def scale_down(self, image, percent):
        """Scales the image down."""
        height, width = image.shape
        scaled_height = self.percentage(percent, height)
        scaled_width = self.percentage(percent, width)

        result = cv2.resize(image, (scaled_width, scaled_height))
        return result
#        cv2.imshow("Show by CV2", result)
#        cv2.waitKey(0)

    @staticmethod
    def percentage(percent, whole):
        """Find what is percent from whole."""
        return (percent * whole) // 100

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


def setup_alignment(reference_filename, image_filename, result_filename, processed_output_dir):
    im_reference = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)
    im_tobe_aligned = cv2.imread(image_filename, cv2.IMREAD_LOAD_GDAL)

    aligned_path = os.path.join(processed_output_dir, result_filename)

    print("Aligned path: ", aligned_path)

    aligner = Align(im_reference, im_tobe_aligned)
    found = aligner.find_matches()
    valid = aligner.validate_homography()
    aligner.setup_windows()

    print(VALID_HOMOGRAPHIES, "/", TOTAL_PROCESSED, "\n")
    if found and valid:
        print(aligned_path)
        cv2.imwrite(aligned_path, aligner.im_result)

# FOR WHATEVER REASON, THE REFERENCE IMAGE IS 0, so it find nothing, all's black
# imread returns NULL if the filepath cannot be read - corruption or something
# it doesn't load it correctly, imread, size.width < 0 and size.height < 0
#os.environ['OPENCV_IO_MAX_IMAGE_PIXELS'] = str(2**64)
# https://stackoverflow.com/questions/24552590/opencv-sift-surf-orb-drawmatch-function-is-not-working-well
# am schimbat ordinea in self.im_matches = cv2.drawMatches(self.im1_8bit, keypoints1, self.im2_8bit, keypoints2, matches, None), si acum e iar ok
# PROBLEM 2 - unele imagini sunt corupte, si au height and width 0. like /net/deepthought/artefacts/satelite_download_68cce0f77a26eb7177a5ec47c40b3f6eaa54acb1/CA2N001CD044_-129.811_57.855/LC81392252018178LGN00_B3.TIF



