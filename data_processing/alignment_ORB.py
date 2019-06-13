from __future__ import print_function
import cv2
from colors import *
import numpy as np

# This is a workaround to allow importing scene both if imported from main and if called directly
import sys
sys.path.append(sys.path[0] + '/..')
from data_processing import scene as sc
from data_processing.ndsi_calculator import NDSI

DEBUG_OUTLIERS = False
DEBUG_TRANSFORM_MATRIX = True

MAX_FEATURES = 5000  # number of feature points taken
GOOD_MATCH_PERCENT = 0.25
ALLOWED_ERROR = 0.01  # the allowed rotation
ALLOWED_INTEGRAL = 100  # the allowed translation
EUCLIDIAN_DISTANCE = 200  # the allowed distance between two points so that the match line is as straight as possible

# the number of boxes the image will be split into
ROWS_NUMBER = 8  # the number of rows the full image will be split into for box matching
COLUMNS_NUMBER = 8  # the number of columns the full image will be split into for box matching


class ProcessImage:
    """Class which handles ORB alignment of two images."""
    def __init__(self, scene:sc.Scene, reference_scene: sc.Scene, aligned_scene: sc.Scene):
        self.image_16bit = sc.SatImage.read(scene)
        self.reference_16bit = sc.SatImage.read(reference_scene)
        self.aligned_16bit = None

        self.scene = scene
        self.reference_scene = reference_scene
        self.aligned_scene = aligned_scene

    def ndsi(self):
        """
        NDSI first. Then align scene with reference, then align aligned with ndsi.
        :return:
        """
        ndsi_image = None
        if self.aligned_16bit is not None:
            self.aligned_16bit = sc.SatImageWithNDSI(self.aligned_16bit.green,
                                                     self.aligned_16bit.swir,
                                                     NDSI.calculate_NDSI(self.aligned_16bit))
            ndsi_image = self.aligned_16bit.ndsi
        else:
            self.image_16bit = sc.SatImageWithNDSI(self.image_16bit.green,
                                                     self.image_16bit.swir,
                                                     NDSI.calculate_NDSI(self.image_16bit))
            ndsi_image = self.image_16bit.ndsi

        DISPLAY.image("ndsi", ndsi_image)

        # snow image is for contrast
        snow_image = NDSI.get_snow_image(ndsi_image, 0.5)
        DISPLAY.image("snow", snow_image)

        print(blue("Snow pixels: "), blue(NDSI.get_snow_pixels(ndsi_image)))
        print(blue("Snow ratio: "), blue(NDSI.get_snow_pixels_ratio(ndsi_image)))

        return ndsi_image

    def align(self):
        """
        Align scene with reference, then ndsi with aligned (the new reference )
        :return:
        """
        first = AlignORB(self.image_16bit, self.reference_16bit)
        self.aligned_16bit = first.align()
        if self.aligned_16bit is None:
            return None

        self.aligned_16bit.write(self.aligned_scene)
        return self.aligned_16bit


class AlignORB:
    """
    Class which gets two images as input and alignes the image based on the reference.
    """
    def __init__(self, input_img: sc.SatImage, reference_img: sc.SatImage):
        # transform from scientific notation to decimal for easy check
        np.set_printoptions(suppress=True, precision=4)

        self.input_img = input_img
        self.reference_img = reference_img

        image_normalized = self.normalize(input_img)
        reference_normalized = self.normalize(reference_img)

        image_normnalized_8bit = self.downsample(image_normalized)
        reference_normnalized_8bit = self.downsample(reference_normalized)

        self.align_input = image_normnalized_8bit
        self.align_reference = reference_normnalized_8bit

        DISPLAY.satimage("INPUT", self.input_img)
        DISPLAY.satimage("REFERENCE", self.reference_img)

        DISPLAY.satimage("ALIGN_INPUT",     self.align_input)
        DISPLAY.satimage("ALIGN_REFERENCE", self.align_reference)

    def downsample(self, image_16bit):
        """
        Chanfes the depth of the inputted image to 8 bit.
        :param image_16bit:
        :return:
        """
        image_8bit_green = (image_16bit.green >> 8).astype(np.uint8)
        image_8bit_swir = (image_16bit.swir >> 8).astype(np.uint8)

        return sc.SatImage(image_8bit_green, image_8bit_swir)

    def normalize(self, image, bits=16):
        """
        Normalizes the input image to be between 0 and the inputted bit range.
        :param image:
        :param bits:
        :return:
        """
        normalized_image_8bit_green = cv2.normalize(image.green, None, 0, (1 << bits)-1, cv2.NORM_MINMAX)
        normalized_image_8bit_swir = cv2.normalize(image.swir,  None, 0, (1 << bits)-1, cv2.NORM_MINMAX)

        return sc.SatImage(normalized_image_8bit_green, normalized_image_8bit_swir)

    @staticmethod
    def boxedDetectAndCompute(image, rows=ROWS_NUMBER, columns=COLUMNS_NUMBER):
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

    def pruneLowScoreMatches(self, matches):
        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove matches with low score
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        return matches

    def getAlignAffineTransform(self):
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

        # detect and compute the feature points by splitting the image in boxes for good feature spread
        keypoints_img_green, descriptors_img_green = self.boxedDetectAndCompute(self.align_input.green)
        keypoints_img_swir,  descriptors_img_swir  = self.boxedDetectAndCompute(self.align_input.swir)
        keypoints_ref_green, descriptors_ref_green = self.boxedDetectAndCompute(self.align_reference.green)
        keypoints_ref_swir,  descriptors_ref_swir  = self.boxedDetectAndCompute(self.align_reference.swir)

        keypoints_img_all   = keypoints_img_green + keypoints_img_swir
        keypoints_ref_all   = keypoints_ref_green + keypoints_ref_swir
        descriptors_img_all = np.concatenate((descriptors_img_green, descriptors_img_swir), axis=0)
        descriptors_ref_all = np.concatenate((descriptors_ref_green, descriptors_ref_swir), axis=0)

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors_ref_all, descriptors_img_all)

        matches = self.pruneLowScoreMatches(matches)

        reference_points, image_points, pruned_matches_image = \
            self.pruneMatchesByDistance(matches, keypoints_ref_all, keypoints_img_all)

        DISPLAY.image("MATCHES", pruned_matches_image)

        # create the affine transformation matrix and inliers
        affine, inliers = cv2.estimateAffine2D(image_points, reference_points, None, cv2.RANSAC)

        # check application mode
        if DEBUG_OUTLIERS:
            self.affine_creation_debug_on(inliers, reference_points, image_points)

        if not self.validate_transform(affine):
            return None

        return affine

    def align(self):

        affine = self.getAlignAffineTransform()
        if affine is None:
            return None

        # warp the affine matrix to the current image
        height, width = self.reference_img.green.shape
        aligned_result_green = cv2.warpAffine(self.input_img.green, affine, (width, height))
        aligned_result_swir  = cv2.warpAffine(self.input_img.swir, affine, (width, height))

        if isinstance(self.input_img, sc.SatImageWithNDSI):
            aligned_result_ndsi  = cv2.warpAffine(self.input_img.ndsi, affine, (width, height))
            aligned = sc.SatImageWithNDSI(aligned_result_green, aligned_result_swir, aligned_result_ndsi)
        else:
            aligned = sc.SatImage(aligned_result_green, aligned_result_swir)

        DISPLAY.satimage("OUTPUT", aligned)

        return aligned

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

    def pruneMatchesByDistance(self, matches, reference_keypoints, image_keypoints):
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
        pruned_matches_image = cv2.drawMatches(self.align_reference.green, reference_keypoints,
                                               self.align_input.green, image_keypoints,
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


class DISPLAY:
    DOIT = True
    @staticmethod
    def satimage(window_prefix, satimage):
        if not DISPLAY.DOIT:
            return
        DISPLAY.image(window_prefix + "_green", satimage.green)
        DISPLAY.image(window_prefix + "_swir", satimage.swir)

    def satimagewithndsi(window_prefix, satimagewithndsi):
        if not DISPLAY.DOIT:
            return
        DISPLAY.image(window_prefix + "_green", satimagewithndsi.green)
        DISPLAY.image(window_prefix + "_swir", satimagewithndsi.swir)
        DISPLAY.image(window_prefix + "_ndsi", satimagewithndsi.ndsi)

    @staticmethod
    def image(window_name, image, normalize=True):
        """
        Displays an image in a cv2 window.
        :param window_name: Name of the cv2 window.
        :param image: cv2 image.
        :return: Nothing.
        """
        if not DISPLAY.DOIT:
            return

        if normalize:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.imshow(window_name, image)

    @staticmethod
    def wait():
        """
        Flushes the display image after pressing exit key.
        :return: Nothing.
        """
        if not DISPLAY.DOIT:
            return
        while cv2.waitKey() != 27:
            pass


if __name__ == "__main__":
    """
    Handle multi process.
    """
    scene           = sc.Scene(sys.argv[1], sys.argv[2])
    reference_scene = sc.Scene(sys.argv[3], sys.argv[4])
    aligned_scene   = sc.Scene(sys.argv[5], sys.argv[6])

    try:
        process = ProcessImage(scene=scene,
                               reference_scene=reference_scene,
                               aligned_scene=aligned_scene)

        ndsi_image = process.ndsi()
        aligned_image = process.align()

        DISPLAY.satimagewithndsi("OUTPUT SCENE", process.aligned_16bit)
        DISPLAY.satimage("REFERENCE SCENE", process.reference_16bit)

        if aligned_image is None:
            VALID = False
        else:
            VALID = True

    except KeyboardInterrupt:
        sys.exit(2)

    DISPLAY.wait()

    if VALID:
        sys.exit(0)
    else:
        sys.exit(1)
