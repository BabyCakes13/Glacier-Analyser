import sys

import cv2
import numpy as np


class DifferenceMovement:
    """
    Set the values for the numpy array images.
    """

    def __init__(self, image1, image2):
        self.image1 = cv2.imread(image1, cv2.IMREAD_GRAYSCALE)
        self.image2 = cv2.imread(image2, cv2.IMREAD_GRAYSCALE)

        self.image1, self.image2 = self.remove_bad_borders()

    def remove_bad_borders(self):
        ret1, thresh1 = cv2.threshold(self.image1, 1, 255, cv2.THRESH_BINARY)
        ret2, thresh2 = cv2.threshold(self.image2, 1, 255, cv2.THRESH_BINARY)
        image1 = cv2.bitwise_and(self.image1, thresh2)
        image2 = cv2.bitwise_and(self.image2, thresh1)

        return image1, image2

    def differenciate(self) -> np.ndarray:
        """
        Make a difference between two images, and apply a colormap the result.
        :return: np.ndarray
        """
        image1_16bit = np.int16(self.image1)
        image2_16bit = np.int16(self.image2)

        difference = image1_16bit - image2_16bit

        difference_normalized = cv2.normalize(difference, None, 0, 255, cv2.NORM_MINMAX)
        difference_8bit = np.uint8(difference_normalized)

        cm_difference = cv2.applyColorMap(difference_8bit, cv2.COLORMAP_JET);

        return cm_difference

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
difference = diff.differenciate()
image('difference', difference)
movement = diff.movement()
image('movement', movement)
