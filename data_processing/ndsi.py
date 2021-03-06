"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy as np

from data_processing import scenes as sc
import cv2

class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Pass creation to only used it as a class variable."""
        pass

    # https://nsidc.org/support/faq/what-ndsi-snow-cover-and-how-does-it-compare-fsc
    # says that NDSI = (Band green - band SWIR) / (Band green + Band SWIR)
    @staticmethod
    def calculate_NDSI(numpy_scene, math_dtype=np.float32) -> np.ndarray:
        """
        Calculates the NDSI image as a np array, by converting to float32 for easy computation, treating the borders
        as NaN in order to ignore those values, since after the alignment, the borders are 0 valued. The interval of
        calculation is normalized in order to make 16bit fit float32.
        :param numpy_scene: Satellite image containing green and swir1 np images.
        :param math_dtype: Data type for mathematical calculations.
        :return: Returns the np array containing the result of the division.
        """

        green_nan = numpy_scene.green_numpy.astype(math_dtype)
        swir_nan = numpy_scene.swir1_numpy.astype(math_dtype)

        green_nan[green_nan == 0] = np.nan
        swir_nan[swir_nan == 0] = np.nan

        # change image bit depth to 32 bit to allow math without saturation
        img = sc.NumpyScene(green_nan, swir_nan)

        # ignore division by zero because image has borders with 0 values
        np.seterr(divide='ignore', invalid='ignore')

        numerator = np.subtract(img.green_numpy, img.swir1_numpy)
        if math_dtype == np.int32:
            numerator = np.multiply(numerator, 0x7FFF)
        denominator = np.add(img.green_numpy, img.swir1_numpy)
        ndsi = np.divide(numerator, denominator)

        # interpret each NaN value as 0
        ndsi[ndsi != ndsi] = -1

        if math_dtype == np.int32:
            ndsi = np.add(ndsi, 0x7FFF)

        return ndsi

    @staticmethod
    def get_snow_image(ndsi, threshold=0.5) -> np.ndarray:
        """
        Returns the image with maximum contrast in order to have everything which is not snow, black, and everything
        which is, shite. Aimed for visual interpretation.
        :param ndsi: The ndsi np image.
        :param threshold: The threshold for computing the contrast.
        :return:
        """
        snow = ndsi.copy()
        snow[snow <= threshold] = -1
        return snow

    @staticmethod
    def get_snow_pixels(snow_image, threshold=0.5) -> int:
        """
        Returns the number of snow pixels from the image, based on the threshold.
        :param snow_image: The contrast snow image.
        :param threshold: The threshold for extracting the snow pixels.
        :return:
        """
        snow_pixels = len(snow_image[snow_image > threshold])
        return snow_pixels

    @staticmethod
    def get_snow_pixels_ratio(snow_image, threshold=0.5) -> float:
        """
        Returns the snow pixel ratio for the ndsi image, as number of snow pixels divided to total number of pixels.
        :param snow_image: The image representing the contrasted ndsi.
        :param threshold: The threshold for calculating the number of snow pixels.
        :return:
        """
        snow_pixels = snow_image[snow_image > threshold].size
        all_pixels = snow_image.size
        ratio = snow_pixels / all_pixels

        return ratio


def image(window_name, image, normalize=True) -> None:
    """
    Displays an image in a cv2 window.
    :param normalize: Check if wanting it in 8bit.
    :param window_name: Name of the cv2 window.
    :param image: cv2 image.
    :return: Nothing.
    """
    if normalize:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1000, 1000)
    cv2.imshow(window_name, image)


if __name__ == "__main__":
    scene = sc.PathScene("/storage/maria/D/Programming/Facultate/test_27_06/232_083/LC82320832013319LGN01_B3.TIF",
                         "/storage/maria/D/Programming/Facultate/test_27_06/232_083/LC82320832013319LGN01_B6.TIF")
    image_16bit = sc.NumpyScene.read(scene)
    nd = NDSI()
    ndsi = nd.calculate_NDSI(image_16bit)
    snow = nd.get_snow_image(ndsi)

    print(nd.get_snow_pixels_ratio(snow))

    image('contrast', snow)
    while cv2.waitKey() != 27:
        pass

    image('ndsi', ndsi)
    while cv2.waitKey() != 27:
        pass