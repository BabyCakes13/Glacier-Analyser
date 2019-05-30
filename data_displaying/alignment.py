from __future__ import print_function
import cv2
import numpy as np
import os

MAX_FEATURES = 5000
GOOD_MATCH_PERCENT = 0.1
VALID_HOMOGRAPHIES = 0
TOTAL_PROCESSED = 0


class Align:
    def __init__(self, im1_16bit, im2_16bit):
        self.im1_16bit = im1_16bit
        self.im2_16bit = im2_16bit
        self.im1_8bit = (im1_16bit >> 8).astype(np.uint8)
        self.im2_8bit = (im2_16bit >> 8).astype(np.uint8)

        self.im_matches = None
        self.im_result = None
        self.homography = None

    def find_matches(self, matches_path) -> bool:
        """Returns whether the homography finding was succesfull or not."""
        # detect ORB features and descriptors
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(self.im1_8bit, None)
        keypoints2, descriptors2 = orb.detectAndCompute(self.im2_8bit, None)

        if (descriptors1 is None) or (descriptors2 is None):
            print("Descriptor is None. Aborting this image.")
            return False

        # match features
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove not good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # draw the best matches
        self.im_matches = cv2.drawMatches(self.im1_8bit, keypoints1, self.im2_8bit, keypoints2, matches, None)
        cv2.imwrite(matches_path, self.im_matches)

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
        height, width = self.im1_8bit.shape

        if self.homography is None:
            print("Homography is none. Aborting this image.")
            return False

        print(self.homography)
        self.im_result = cv2.warpPerspective(self.im1_8bit, self.homography, (width, height))
        return True

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

    def validate_homography(self):
        np.set_printoptions(suppress=True, precision=4)
        global TOTAL_PROCESSED
        global VALID_HOMOGRAPHIES
        TOTAL_PROCESSED += 1

        identity = np.identity(3)
        comparison = np.full((3, 3), 0.1)
        comparison[0, 2] = 3000
        comparison[1, 2] = 3000

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


def setup_alignment(reference_filename, tobe_aligned_filename, result_filename, matches_filename, output_dir):
#    print("Started alignment...")
    reference_filename = reference_filename
#    print("Reading reference image : ", reference_filename)
    im_reference = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)

    tobe_aligned_filename = tobe_aligned_filename
#    print("Reading image to align : ", tobe_aligned_filename)
    im_tobe_aligned = cv2.imread(tobe_aligned_filename, cv2.IMREAD_LOAD_GDAL)

#    print("Aligning images ...")
    matches_path = os.path.join(output_dir, matches_filename)
    aligner = Align(im_tobe_aligned, im_reference)
    found = aligner.find_matches(matches_path)
    valid = aligner.validate_homography()
#    aligner.setup_windows()

    # Write aligned image to disk.
#    print("Saving aligned image : ", result_filename)
    print("valid ", VALID_HOMOGRAPHIES, " from ", TOTAL_PROCESSED)
    print("\n")
    if found and valid:
        cv2.imwrite(os.path.join(output_dir, result_filename), aligner.im_result)

