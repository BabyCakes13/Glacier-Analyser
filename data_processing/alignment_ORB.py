from __future__ import print_function
import cv2
import numpy as np
import os
import sys

DISPLAY = False
DEBUG_OUTLIERS = False
DEBUG_TRANSFORM_MATRIX = True

MAX_FEATURES = 5000  # number of feature points taken
GOOD_MATCH_PERCENT = 0.50
ALLOWED_ERROR = 0.01  # the allowed rotation
ALLOWED_INTEGRAL = 100  # the allowed translation
EUCLIDIAN_DISTANCE = 200  # the allowed distance between two points so that the match line is as straight as possible

# the number of boxes the image will be split into
ROWS_NUMBER = 8  # the number of rows the full image will be split into for box matching
COLUMNS_NUMBER = 8  # the number of columns the full image will be split into for box matching


class AlignORB:
    """Class which handles ORB alignment of two images."""
    def __init__(self, reference_8bit, current_8bit):
        """
        Prepares the pictures for alignment by normalising the current image and initialising the result
        and matches.
        :param reference_8bit: The reference image in gray scale.
        :param current_8bit: The current comparison image in gray scale.
        """
        self.reference_8bit = reference_8bit
        self.current_8bit = cv2.normalize(current_8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

        self.result_8bit = None
        self.matches = None

    @staticmethod
    def boxedDetectAndCompute(image, rows, columns):
        """
        Splits the image in n boxes and applies feature finding in each, so that the points are evenly distributed,
        avoiding image distortion in the case there are feature points only in one part of the image.
        :param image: The image which will be split.
        :param rows: Number of rows in which the image will be split
        :param columns: Number of columns in which the image will be split
        :return: The keypoints and descriptors of the whole image
        """
        orb = cv2.ORB_create(nfeatures=MAX_FEATURES // rows // columns, scaleFactor=2, patchSize=100)

        # list of keypoints of the whole image
        keypoints = []

        # create the box
        for x in range(0, columns):
            for y in range(0, rows):
                x0 = x * image.shape[1] // columns
                x1 = (x+1) * image.shape[1] // columns
                y0 = y * image.shape[0] // rows
                y1 = (y+1) * image.shape[0] // rows

                image_box = image[y0:y1, x0:x1]

                # detect keypoints in the boxed image
                box_keypoints = orb.detect(image_box)

                # append the box keypoints to the whole image keypoints
                for keypoint in box_keypoints:
                    keypoint.pt = (keypoint.pt[0] + x0, keypoint.pt[1] + y0)
                    keypoints.append(keypoint)

        # compute the descriptors with the found keypoints
        keypoints, descriptors = orb.compute(image, keypoints)

        return keypoints, descriptors

    def align(self):
        """
        The main aligning method. Find the feature key points in each image by splitting the image in boxes, so that the
        features are evenly distributed across the whole image, avoiding clusters of points in just one region, which
        would create a bad affine matrix. Sorts the matches based on their score, and prunes the ones which are not
        euclidean distance valid, which indicates that the feature is not correct. Creates the affine matrix and inliers
        based on the pruned key points from the reference image and current comparison matrix, and validates the
        transformation matrix. With the valid affine matrix, it warps it to the current image.
        :return: Returns the result of validating the affine matrix and the pruned matches image for writing it to the
        disk.
        """
        # transform from scientific notation to decimal for easy check
        np.set_printoptions(suppress=True, precision=4)

        # detect and compute the feature points by splitting the image in boxes for good feature spread
        reference_keypoints, descriptors_ref = \
            self.boxedDetectAndCompute(self.reference_8bit, ROWS_NUMBER, COLUMNS_NUMBER)
        image_keypoints, descriptors_img = \
            self.boxedDetectAndCompute(self.current_8bit, ROWS_NUMBER, COLUMNS_NUMBER)

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors_ref, descriptors_img)

        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove matches with low score
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        reference_points, image_points, pruned_matches_image = self.prune_matches(matches,
                                                                                  reference_keypoints,
                                                                                  image_keypoints)
        # create the affine transformation matrix and inliers
        height, width = self.reference_8bit.shape
        inliers = None
        affine, inliers = cv2.estimateAffine2D(image_points, reference_points, inliers, cv2.LMEDS, confidence=0.99)

        # warp the affine matrix to the current image
        self.result_8bit = cv2.warpAffine(self.current_8bit, affine, (width, height))
        VALID = self.validate_transform(affine)

        # check application mode
        if DEBUG_OUTLIERS:
            self.affine_creation_debug_on(inliers, reference_points, image_points)
        if DISPLAY:
            self.display_on(pruned_matches_image)

        return VALID, pruned_matches_image

    @staticmethod
    def affine_creation_debug_on(inliers, image_points, reference_points):
        """
        Prints information which points are outliers and inliers, if debug mode is on.
        :param inliers: The inliers from the affine transformation
        :param reference_points: The feature points from the reference
        :param image_points: The feature points from the image
        :return: Returns nothing
        """
        for inlier, reference_point, image_point in zip(inliers, reference_points, image_points):
            if inlier == 1:
                status = "inlier"
            else:
                status = "outlier"
            print(status, reference_point[0],
                  "  x  ", reference_point[0] - image_point[0],
                  "  y  ", reference_point[1] - image_point[1])

    def display_on(self, pruned_matches_image):
        """
        If the display mode is on, draw the best matches on the screen.
        :param pruned_matches_image: The image which contains the pruned matches
        :return: Nothing
        """
        # draw the best matches
        self.display_image('PRUNED MATCHES', pruned_matches_image)

    def prune_matches(self, matches, reference_keypoints, image_keypoints):
        """
        Method which prunes the feature points pairs which are not valid (too far away from each other in the euclidean
        distance. This ensures that the remaining feature points are valid matches and the match line as straight as
        possible, which would be a 1 to 1 match.
        :param matches: The matches pairs
        :param reference_keypoints: Total keypoints from the reference image
        :param image_keypoints: Total keypoints from the current comparison image
        :return: Returns the reference and current image keypoint pairs which were left after the pruning, as well as
        the pruned matches cv2 image.
        """
        # go through point matches and prune the bad results
        matches_pruned = []
        reference_points = []
        image_points = []

        for match in matches:
            reference_point = reference_keypoints[match.queryIdx].pt
            image_point = image_keypoints[match.trainIdx].pt

            valid_euclidean_distance = self.validate_euclidean_distance(reference_point=reference_point,
                                                                        image_point=image_point)
            if valid_euclidean_distance:
                reference_points.append(reference_point)
                image_points.append(image_point)
                matches_pruned.append(match)

        # convert them into numpy arrays for creating the alignment
        reference_points = np.array(reference_points)
        image_points = np.array(image_points)

        # draw the match image
        pruned_matches_image = cv2.drawMatches(self.reference_8bit, reference_keypoints,
                                               self.current_8bit, image_keypoints,
                                               matches_pruned,
                                               None, matchColor=(0, 255, 255), singlePointColor=(100, 0, 0),
                                               flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        return reference_points, image_points, pruned_matches_image

    @staticmethod
    def validate_euclidean_distance(reference_point, image_point) -> bool:
        """
        Calculates the difference between the reference and image coordinates. If the euclidean difference is too big,
        that means that the feature points are not correctly matched. If correctly matched, the distance should be as
        small as possible, and the match should be a straight line. The euclidean distance comparison allows the degree
        of match misalignment.
        :param reference_point: A 2D point with the coordinates of a feature point from the reference
        :param image_point: A 2D point with the coordinates of a feature point from the current image
        :return: If the distance is smaller than the allowed euclidean distance, returns True, else, the match is not
        valid and returns False
        """
        # coordinates of the keypoints for calculating the euclidean distance
        reference_x = reference_point[0]
        reference_y = reference_point[1]
        image_x = image_point[0]
        image_y = image_point[1]

        # check if the distance between the points is valid to ensure that the match line is as straight as possible
        if (abs(reference_x - image_x) < EUCLIDIAN_DISTANCE) and (abs(reference_y - image_y) < EUCLIDIAN_DISTANCE):
            return True
        else:
            return False

    def validate_transform(self, transform):
        """
        Validate the transformation matrix.
        :param transform: The transformation matrix which will be wrapped around the current image.
        :return: The result of the validation.
        """
        # convert from scientific notation to decimal notation for better data interpretation
        np.set_printoptions(suppress=True, precision=4)

        width = transform.shape[1]
        height = transform.shape[0]

        identity = np.identity(3)
        identity = identity[0:height, 0:width]
        difference = np.absolute(np.subtract(identity, transform))
        compare = self.create_comparison_matrix(height, width)

        if DEBUG_TRANSFORM_MATRIX:
            print("Transform \n", transform)
            print("Difference \n", difference)
            print("Comparison \n", compare)

        if np.less_equal(difference, compare).all():
            print("Transform is good.")
            return True
        else:
            print("Transform is bad.")
            return False

    @staticmethod
    def create_comparison_matrix(width=3, height=3):
        """
        Creates the comparison matrix for transform matrix validation.
        :param width: Width of the transform matrix.
        :param height: Height of the transform matrix.
        :return: The comparison numpy matrix.
        """
        comparison = np.full((width, height), ALLOWED_ERROR)
        comparison[0, 2] = ALLOWED_INTEGRAL
        comparison[1, 2] = ALLOWED_INTEGRAL

        return comparison

    @staticmethod
    def display_image(window_name, image):
        """
        Displays an image in a cv2 window.
        :param window_name: Name of the cv2 window.
        :param image: cv2 image.
        :return: Nothing.
        """
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.moveWindow(window_name, 10, 10)
        cv2.imshow(window_name, image)

    @staticmethod
    def display_image_flush():
        """
        Flushes the display image after pressing exit key.
        :return: Nothing.
        """
        while cv2.waitKey() != 27:
            pass


def start_alignment(reference_path, image_path, result_filename, output_directory):
    """
    Starts the alignment process.
    :param reference_path: Path to the reference image.
    :param image_path: Path to the current image.
    :param result_filename: Result name.
    :param output_directory: Path to the output directory to write the images.
    :return: The status of the alignment.
    """
    result_path = os.path.join(output_directory, result_filename)
    pruned_matches_path = os.path.join(output_directory, "matched_" + result_filename)

    print_current_images(reference_path, image_path, result_path)

    # prepare the images for alignment
    normalised_reference_8bit, current_image_8bit = resize_depth(reference_path, image_path)

    # align
    aligner = AlignORB(normalised_reference_8bit, current_image_8bit)
    VALID, pruned_matches_image = aligner.align()

    # write the valid images and all matches
    if VALID:
        cv2.imwrite(result_path, aligner.result_8bit)
    cv2.imwrite(pruned_matches_path, pruned_matches_image)

    if DISPLAY:
        aligner.display_image("Reference", aligner.reference_8bit)
        aligner.display_image("Current Image", aligner.current_8bit)
        aligner.display_image("Result", aligner.result_8bit)
        aligner.display_image_flush()

    cv2.destroyAllWindows()

    return VALID


def print_current_images(reference_path, image_path, aligned_path):
    """
    Prints the current images which are being processed.
    :param reference_path: The path to the reference image.
    :param image_path: The path to the current image.
    :param aligned_path: The path to the aligned image.
    :return: Nothing.
    """
    print("\n...")
    print("Reference filename: ", reference_path)
    print("Image filename ", image_path)
    print("Aligned filename  ", aligned_path)


def resize_depth(reference_path, image_path):
    """
    Resize the image depth and normalise the reference just one time rather than each time.
    :param reference_path: The path to the reference image
    :param image_path: The path to the current image
    :return: Returns the normalised reference and the current image in 8 bits.
    """
    reference_16bit = cv2.imread(reference_path, cv2.IMREAD_LOAD_GDAL)
    current_image_16bit = cv2.imread(image_path, cv2.IMREAD_LOAD_GDAL)

    reference_8bit = (reference_16bit >> 8).astype(np.uint8)
    current_image_8bit = (current_image_16bit >> 8).astype(np.uint8)

    # normalise the reference just once at the beginning since it will be used in each alignment
    normalised_reference_8bit = cv2.normalize(reference_8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

    return normalised_reference_8bit, current_image_8bit


if __name__ == "__main__":
    """
    Handle multi process.
    """
    try:
        VALID = start_alignment(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    except KeyboardInterrupt:
        sys.exit(3)

    if VALID:
        sys.exit(0)
    else:
        sys.exit(1)
