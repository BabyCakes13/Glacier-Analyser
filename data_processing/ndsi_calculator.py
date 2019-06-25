"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy

from data_processing import scene as sc


class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Pass creation to only used it as a class variable."""
        pass

    # https://nsidc.org/support/faq/what-ndsi-snow-cover-and-how-does-it-compare-fsc
    # says that NDSI = (Band green - band SWIR) / (Band green + Band SWIR)
    @staticmethod
    def calculate_NDSI(satimage, math_dtype=numpy.float32):

        green_nan = satimage.green.astype(math_dtype)
        swir_nan = satimage.swir.astype(math_dtype)

        green_nan[green_nan == 0] = numpy.nan
        swir_nan[swir_nan == 0] = numpy.nan

        # change image bit depth to 32 bit to allow math without saturation
        img = sc.SatImage(green_nan, swir_nan)

        # ignore division by zero because image has borders with 0 values
        numpy.seterr(divide='ignore', invalid='ignore')

        numerator = numpy.subtract(img.green, img.swir)
        if math_dtype == numpy.int32:
            numerator = numpy.multiply(numerator, 0x7FFF)
        denominator = numpy.add(img.green, img.swir)
        ndsi = numpy.divide(numerator, denominator)

        # interpret each NaN value as 0
        ndsi[ndsi != ndsi] = -1

        if math_dtype == numpy.int32:
            ndsi = numpy.add(ndsi, 0x7FFF)

        # print("ndsi data range is ", ndsi.min(), " ", ndsi.max())

        return ndsi

    @staticmethod
    def get_snow_image(ndsi, threshold=0.5):
        """
        Returns the image with maximum contrast in order to have everything which is not snow, black, and everything
        which is, shite. Aimed for visual interpretation.
        :param ndsi: The ndsi numpy image.
        :param threshold: The threshold for computing the contrast.
        :return:
        """
        snow = ndsi.copy()
        snow[snow <= threshold] = -1
        return snow

    @staticmethod
    def get_snow_pixels(snow_image, threshold=0.5):
        """
        Returns the number of snow pixels from the image, based on the threshold.
        :param snow_image: The contrast snow image.
        :param threshold: The threshold for extracting the snow pixels.
        :return:
        """
        snow_pixels = len(snow_image[snow_image > threshold])
        return snow_pixels

    @staticmethod
    def get_snow_pixels_ratio(snow_image, threshold=0.5):
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
