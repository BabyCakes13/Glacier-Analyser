import sys

import cv2
import numpy as np


class DifferenceMovement:
    """
    Set the values for the numpy array images.
    """

    def __init__(self, image1, image2):
        np.seterr(divide='ignore', invalid='ignore')

        self.image1 = cv2.imread(image1, cv2.IMREAD_GRAYSCALE)
        self.image2 = cv2.imread(image2, cv2.IMREAD_GRAYSCALE)

        mask1, mask2 = self.create_mask()

        self.img_diff = self.differentiate()
        self.img_diff = self.remove_background_color(self.img_diff,
                                                     threshold1=mask1,
                                                     threshold2=mask2)
        self.img_move = self.movement()
        self.img_move = self.remove_background_color(self.img_move,
                                                     threshold1=mask1,
                                                     threshold2=mask2)

        image('different', self.img_diff)
        image('move', self.img_move)

    def create_mask(self):
        """
        Creates two masks which represent the black background of the satellite images.
        :return: A tuple of two numpy arrays.
        """
        ret1, threshold1 = cv2.threshold(self.image1, 1, 255, cv2.THRESH_BINARY)
        ret2, threshold2 = cv2.threshold(self.image2, 1, 255, cv2.THRESH_BINARY)

        return threshold1, threshold2

    def differentiate(self) -> np.ndarray:
        """
        Make a difference between the pixels of two images, and apply a colormap the result for nicer view.
        :return: np.ndarray
        """
        image1_16bit = np.int16(self.image1)
        image2_16bit = np.int16(self.image2)

        difference = image1_16bit - image2_16bit

        difference_normalized = cv2.normalize(difference, None, 0, 255, cv2.NORM_MINMAX)
        difference_8bit = np.uint8(difference_normalized)

        cm_difference = cv2.applyColorMap(difference_8bit, cv2.COLORMAP_JET)

        return cm_difference

    @staticmethod
    def remove_background_color(image, threshold1, threshold2) -> np.ndarray:
        """
        Removes green background color by applying a mask on each layer of the RGB image.
        :param image: The numpy image to be enhanced.
        :param threshold1: Threshold mask 1.
        :param threshold2: Threshold mask 2.
        :return: np.ndarray
        """
        image[..., 0] = cv2.bitwise_and(image[..., 0], threshold1)
        image[..., 1] = cv2.bitwise_and(image[..., 1], threshold1)
        image[..., 2] = cv2.bitwise_and(image[..., 2], threshold1)

        image[..., 0] = cv2.bitwise_and(image[..., 0], threshold2)
        image[..., 1] = cv2.bitwise_and(image[..., 1], threshold2)
        image[..., 2] = cv2.bitwise_and(image[..., 2], threshold2)

        return image

    def movement(self) -> np.ndarray:
        """
        Apply Optical Flow algorithm in order to detect movement between two images.
        :return: np.ndarray
        """
        image1_c = cv2.cvtColor(self.image1, cv2.COLOR_GRAY2BGR)
        hsv = np.zeros_like(image1_c)

        flow = cv2.calcOpticalFlowFarneback(self.image1, self.image2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # color map
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 1] = 255
        hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        hsv[..., 2] = self.scale(hsv[..., 2], 3)

        # brighten up
        hsv[..., 2] = hsv[..., 2] * 2
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return bgr

    @staticmethod
    def scale(image, value):
        image32 = image.astype(np.int32)
        image32 = image32 * value
        np.clip(image32, 0, 255, out=image32)
        return image32.astype(np.uint8)


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


diff = DifferenceMovement(sys.argv[1], sys.argv[2])
