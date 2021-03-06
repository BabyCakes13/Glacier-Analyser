from __future__ import print_function

import cProfile
import io
import pstats
import signal
import sys


def interrupt_handler(signum, frame):
    """
    Signal handler for GUI.
    :param signum: Signal.
    :param frame: Frame for signal.
    :return:
    """
    sys.exit(2)


signal.signal(signal.SIGTERM, interrupt_handler)

try:
    import cv2
    import os
    import pathlib
    from colors import *
    import numpy as np
except ImportError:
    sys.exit(21)

# This is a workaround to allow importing scene both if imported from main and if called directly
import sys

sys.path.append(sys.path[0] + '/..')
from data_processing import scenes as sc
from data_processing import ndsi as nc
from data_preparing import csv_writer
from data_gathering import scene_information as sd

DEBUG_OUTLIERS = False
DEBUG_TRANSFORM_MATRIX = False

MAX_FEATURES = 5000  # number of feature points taken
GOOD_MATCH_PERCENT = 0.25
ALLOWED_ROTATION = 0.01  # the allowed rotation
ALLOWED_TRANSLATION = 100  # the allowed translation
EUCLIDIAN_DISTANCE = 200  # the allowed distance between two points so that the match line is as straight as possible

# the number of boxes the image will be split into
ROWS_NUMBER = 8  # the number of rows the full image will be split into for box matching
COLUMNS_NUMBER = 8  # the number of columns the full image will be split into for box matching

NDSI_CSV = 'ndsi'


class ProcessImage:
    """Class which handles ORB alignment of two images."""

    def __init__(self, scene: sc.PathScene, reference_scene: sc.PathScene, aligned_scene: sc.PathScene):
        self.image_16bit = sc.NumpyScene.read(scene)
        self.reference_16bit = sc.NumpyScene.read(reference_scene)
        self.aligned_16bit = None

        self.scene = scene
        self.reference_scene = reference_scene
        self.aligned_scene = aligned_scene

    def ndsi(self):
        """
        NDSI first. Then align scene with reference, then align aligned with ndsi.
        :return: sc.SatImage
        """
        if self.aligned_16bit is not None:
            self.aligned_16bit = sc.NumpySceneWithNDSI(self.aligned_16bit.green_numpy,
                                                       self.aligned_16bit.swir1_numpy,
                                                       nc.NDSI.calculate_NDSI(self.aligned_16bit))
            image_with_ndsi_16bit = self.aligned_16bit
        else:
            self.image_16bit = sc.NumpySceneWithNDSI(self.image_16bit.green_numpy,
                                                     self.image_16bit.swir1_numpy,
                                                     nc.NDSI.calculate_NDSI(self.image_16bit))
            h = nc.NDSI()
            ndsi = nc.NDSI.calculate_NDSI(self.image_16bit)
            snow_image = h.get_snow_image(ndsi=ndsi)

            snow_pixels_ratio = h.get_snow_pixels_ratio(snow_image=snow_image, threshold=0.5)

            image_with_ndsi_16bit = self.image_16bit
            self.write_ndsi_csv(path=aligned_scene.green_path,
                                scene=aligned_scene.get_scene_name(),
                                snow_ratio=snow_pixels_ratio)

        return image_with_ndsi_16bit

    @staticmethod
    def write_ndsi_csv(path, scene, snow_ratio):
        print(yellow("[ INFO  ]: ") + yellow("Writing NDSI item..."))
        path_row_dir = pathlib.Path(path).parents[0]
        glacier_dir, path_row = os.path.split(path_row_dir)
        glacier_dir = pathlib.Path(path).parents[1]
        parent_dir, glacier_id = os.path.split(glacier_dir)

        h = sd.SceneInformation(scene=scene)
        year = h.get_year()
        month = h.get_month()
        day = h.get_day()

        path_row = path_row.split("_")
        path = path_row[0]
        row = path_row[1]

        arguments = [
            glacier_id,
            scene,
            year,
            month,
            day,
            path,
            row,
            snow_ratio,
        ]

        h = csv_writer.CSVWriter(output_dir=path_row_dir,
                                 arguments=arguments,
                                 path=path,
                                 row=row)
        h.start()

    def align(self):
        """
        Align scene with reference, then ndsi with aligned (the new reference )
        :return:
        """
        align = AlignORB(self.image_16bit, self.reference_16bit)
        self.aligned_16bit = align.align()
        if self.aligned_16bit is None:
            return None

        return self.aligned_16bit

    def write(self):
        """
        Write images to disk and to the csv
        :return:
        """
        if self.aligned_16bit:
            self.aligned_16bit.write(self.aligned_scene)
        else:
            print(red("Aligned 16 bit is none. Not writing."))


class AlignORB:
    """
    Class which gets two images as input and alignes the image based on the reference.
    """

    def __init__(self, input_img: sc.NumpyScene, reference_img: sc.NumpyScene):
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

        sc.DISPLAY.numpy_scene("INPUT", self.input_img)
        sc.DISPLAY.numpy_scene("REFERENCE", self.reference_img)

        sc.DISPLAY.numpy_scene("ALIGN_INPUT", self.align_input)
        sc.DISPLAY.numpy_scene("ALIGN_REFERENCE", self.align_reference)

    def downsample(self, image_16bit):
        """
        Chanfes the depth of the inputted image to 8 bit.
        :param image_16bit:
        :return:
        """
        image_8bit_green = (image_16bit.green_numpy >> 8).astype(np.uint8)
        image_8bit_swir = (image_16bit.swir1_numpy >> 8).astype(np.uint8)

        return sc.NumpyScene(image_8bit_green, image_8bit_swir)

    def normalize(self, image, bits=16):
        """
        Normalizes the input image to be between 0 and the inputted bit range.
        :param image:
        :param bits:
        :return:
        """
        normalized_image_8bit_green = cv2.normalize(image.green_numpy, None, 0, (1 << bits) - 1, cv2.NORM_MINMAX)
        normalized_image_8bit_swir = cv2.normalize(image.swir1_numpy, None, 0, (1 << bits) - 1, cv2.NORM_MINMAX)

        return sc.NumpyScene(normalized_image_8bit_green, normalized_image_8bit_swir)

    @staticmethod
    def box_detect_and_compute(image, rows=ROWS_NUMBER, columns=COLUMNS_NUMBER) -> tuple:
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
                x1 = (x + 1) * image.shape[1] // columns
                y0 = y * image.shape[0] // rows
                y1 = (y + 1) * image.shape[0] // rows

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

    @staticmethod
    def prune_low_score_matches(matches):
        """
        Prune low score matches in order to get feature which were as close to straight lines as possible.
        :param matches:
        :return:
        """
        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove matches with low score
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        return matches

    def get_align_affine_transformation(self):
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
        keypoints_img_green, descriptors_img_green = self.box_detect_and_compute(self.align_input.green_numpy)
        keypoints_img_swir, descriptors_img_swir = self.box_detect_and_compute(self.align_input.swir1_numpy)
        keypoints_ref_green, descriptors_ref_green = self.box_detect_and_compute(self.align_reference.green_numpy)
        keypoints_ref_swir, descriptors_ref_swir = self.box_detect_and_compute(self.align_reference.swir1_numpy)

        keypoints_img_all = keypoints_img_green + keypoints_img_swir
        keypoints_ref_all = keypoints_ref_green + keypoints_ref_swir

        if len(keypoints_img_all) == 0 or len(keypoints_ref_all) == 0:
            print(red("There are no keypoints found."))
            return None

        try:
            descriptors_img_all = np.concatenate((descriptors_img_green, descriptors_img_swir), axis=0)
            descriptors_ref_all = np.concatenate((descriptors_ref_green, descriptors_ref_swir), axis=0)
        except ValueError:
            print(red("The imaged are zero valued."))
            return None

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors_ref_all, descriptors_img_all)

        matches = self.prune_low_score_matches(matches)

        reference_points, image_points, pruned_matches_image = \
            self.prune_matches_by_distance(matches, keypoints_ref_all, keypoints_img_all)

        sc.DISPLAY.image("MATCHES", pruned_matches_image)

        # create the affine transformation matrix and inliers
        try:
            affine, inliers = cv2.estimateAffine2D(image_points, reference_points, None, cv2.RANSAC)
        except Exception as e:
            print(red("Image is corrupt. Not writing."))
            return None

        # check application mode
        if DEBUG_OUTLIERS:
            self.affine_creation_debug_on(inliers, reference_points, image_points)
        if affine is None:
            return None

        if not self.validate_transform(affine):
            return None

        return affine

    def align(self):

        affine = self.get_align_affine_transformation()
        if affine is None:
            return None

        # warp the affine matrix to the current image
        height, width = self.reference_img.green_numpy.shape
        aligned_result_green = cv2.warpAffine(self.input_img.green_numpy, affine, (width, height))
        aligned_result_swir = cv2.warpAffine(self.input_img.swir1_numpy, affine, (width, height))

        if isinstance(self.input_img, sc.NumpySceneWithNDSI):
            aligned_result_ndsi = cv2.warpAffine(self.input_img.ndsi, affine, (width, height))
            aligned = sc.NumpySceneWithNDSI(aligned_result_green, aligned_result_swir, aligned_result_ndsi)
        else:
            aligned = sc.NumpyScene(aligned_result_green, aligned_result_swir)

        sc.DISPLAY.numpy_scene("OUTPUT", aligned)

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

    def prune_matches_by_distance(self, matches, reference_keypoints, image_keypoints):
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
        pruned_matches_image = cv2.drawMatches(self.align_reference.green_numpy, reference_keypoints,
                                               self.align_input.green_numpy, image_keypoints,
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
            # print("Transform is good.")
            return True
        else:
            # print("Transform is bad.")
            return False

    @staticmethod
    def create_comparison_matrix(width=3, height=3):
        """
        Creates the comparison matrix for transform matrix validation.
        :param width: Width of the transform matrix.
        :param height: Height of the transform matrix.
        :return: The comparison numpy matrix.
        """
        comparison = np.full((width, height), ALLOWED_ROTATION)
        comparison[0, 2] = ALLOWED_TRANSLATION
        comparison[1, 2] = ALLOWED_TRANSLATION

        return comparison


if __name__ == "__main__":
    """
    Handle multi process.
    """

    # profiler for execution data gathering
    pr = cProfile.Profile()
    pr.enable()

    VALID = True

    scene = sc.PathScene(sys.argv[1], sys.argv[2])
    reference_scene = sc.PathScene(sys.argv[3], sys.argv[4])
    aligned_scene = sc.PathScene(sys.argv[5], sys.argv[6])

    print(yellow("[ INFO ] ") + magenta("Aligning scene: ") + magenta(scene.get_scene_name()))
    process = ProcessImage(scene=scene,
                           reference_scene=reference_scene,
                           aligned_scene=aligned_scene)

    ndsi_image = process.ndsi()
    aligned_image = process.align()

    if aligned_image is None:
        VALID = False
    else:
        process.write()

    #  stop profiler
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    output_dir, file_name = os.path.split(scene.green_path)
    ps.dump_stats(os.path.join(output_dir, scene.get_scene_name() + ".prof"))
    print(s.getvalue())
    sc.DISPLAY.wait()

    if VALID:
        sys.exit(0)
    else:
        sys.exit(1)
