"""
Module which handles calculation of difference for object state and optical flow for image movement.
"""
import os
import sys

import cv2
import numpy as np


class DifferenceMovement:
    """
    Class which handles creating the difference and movement images for an NDSI image.
    """

    def __init__(self, image1_path: str, image2_path: str, output_path: str):
        """
        The constructor handles the reading, creation of mask, calculation of difference and movement images and mask
        applying on them.
        :param image1_path: First image.
        :param image2_path: Second image.
        :param output_path: Path for image output writing.
        """
        np.seterr(divide='ignore', invalid='ignore')

        image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

        mask1, mask2 = self.create_mask(image1=image1,
                                        image2=image2)

        self.image_diff = self.differentiate(image1=image1,
                                             image2=image2)
        self.image_diff = self.remove_background_color(self.image_diff,
                                                       mask1=mask1,
                                                       mask2=mask2)
        self.image_move = self.movement(image1=image1,
                                        image2=image2)
        self.image_move = self.remove_background_color(self.image_move,
                                                       mask1=mask1,
                                                       mask2=mask2)

        image('different', self.image_diff)
        image('move', self.image_move)

        self.write(output_path)

    @staticmethod
    def create_mask(image1, image2) -> tuple:
        """
        Creates two masks which represent the black background of the satellite images.
        :return: A tuple of two numpy arrays.
        """
        ret1, threshold1 = cv2.threshold(image1, 1, 255, cv2.THRESH_BINARY)
        ret2, threshold2 = cv2.threshold(image2, 1, 255, cv2.THRESH_BINARY)

        return threshold1, threshold2

    @staticmethod
    def differentiate(image1, image2) -> np.ndarray:
        """
        Make a difference between the pixels of two images, and apply a colormap the result for nicer view.
        :return: np.ndarray
        """
        image1_16bit = np.int16(image1)
        image2_16bit = np.int16(image2)

        difference = image1_16bit - image2_16bit

        difference_normalized = cv2.normalize(difference, None, 0, 255, cv2.NORM_MINMAX)
        difference_8bit = np.uint8(difference_normalized)

        cm_difference = cv2.applyColorMap(difference_8bit, cv2.COLORMAP_JET)

        return cm_difference

    def movement(self, image1, image2) -> np.ndarray:
        """
        Apply Optical Flow algorithm in order to detect movement between two images.
        :return: np.ndarray
        """
        image1_c = cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR)
        hsv = np.zeros_like(image1_c)

        flow = cv2.calcOpticalFlowFarneback(image1, image2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # color map
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 1] = 255
        hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        hsv[..., 2] = self.scale(hsv[..., 2], 3)

        # brighten up
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return bgr

    @staticmethod
    def remove_background_color(image, mask1, mask2) -> np.ndarray:
        """
        Removes green background color by applying a mask on each layer of the RGB image.
        :param image: The numpy image to be enhanced.
        :param mask1: Threshold mask 1.
        :param mask2: Threshold mask 2.
        :return: np.ndarray
        """
        image[..., 0] = cv2.bitwise_and(image[..., 0], mask1)
        image[..., 1] = cv2.bitwise_and(image[..., 1], mask1)
        image[..., 2] = cv2.bitwise_and(image[..., 2], mask1)

        image[..., 0] = cv2.bitwise_and(image[..., 0], mask2)
        image[..., 1] = cv2.bitwise_and(image[..., 1], mask2)
        image[..., 2] = cv2.bitwise_and(image[..., 2], mask2)

        return image

    @staticmethod
    def scale(image, value) -> np.ndarray:
        """
        Brighten and contrast up the optical flow image for visual interpretation;
        Remove overflow brightness form the image resulting after optical flow computation.
        Since the values are maximum 255, an overflow would turn those pixels black, aka the lowest level of brightness.
        :param image: The overflowed image.
        :param value: The value of brighten up.
        :return: The improved image.
        """
        image32 = image.astype(np.int32)
        image32 = image32 * value
        np.clip(image32, 0, 255, out=image32)

        return image32.astype(np.uint8)

    def write(self, path) -> None:
        """
        Write the two difference and movement images to disk, with the specified path.
        :param path: Path to the output folder for writing.
        :return: Nothing.
        """
        image2_path = os.path.join(path, 'diff.TIF')
        image1_path = os.path.join(path, 'move.TIF')

        cv2.imwrite(image1_path, self.image_diff)
        cv2.imwrite(image2_path, self.image_move)


def image(window_name, image) -> None:
    """
    Display a numpy image.
    :param window_name: Name of the window.
    :param image: cv2 image.
    :return: None
    """
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1000, 1000)
    cv2.imshow(window_name, image)

    while cv2.waitKey(0) & 0xff != 27:
        pass
    cv2.destroyAllWindows()


class ProcessResults:
    def __init__(self, input_dir):
        self.input_dir = input_dir

    # TODO


diff = DifferenceMovement(sys.argv[1], sys.argv[2], sys.argv[3])
