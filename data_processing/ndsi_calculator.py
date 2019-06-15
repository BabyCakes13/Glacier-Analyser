"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy

from data_processing import scene as sc


class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Set the variables needed for computing the ndsi band and actually compute the ndsi band."""
        pass

    # https://nsidc.org/support/faq/what-ndsi-snow-cover-and-how-does-it-compare-fsc
    # says that NDSI = (Band green - band SWIR) / (Band green + Band SWIR)
    @staticmethod
    def calculate_NDSI(satimage, math_dtype=numpy.float32):
        print("calculate_NDSI")
        # change image bit depth to 32 bit to allow math without saturation
        green_nan = satimage.green.astype(math_dtype)
        swir_nan = satimage.swir.astype(math_dtype)

        green_nan[green_nan == 0] = numpy.nan
        swir_nan[swir_nan == 0] = numpy.nan

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

        return ndsi

    @staticmethod
    def get_snow_image(ndsi, threshold=0.5):
        print("get_snow_image")

        snow = ndsi.copy()
        snow[snow <= threshold] = -1
        return snow

    @staticmethod
    def get_snow_pixels(snowImage, threshold=0.5):
        print("get_snow_pixels")

        snow_pixels = len(snowImage[snowImage > threshold])
        return snow_pixels

    @staticmethod
    def get_snow_pixels_ratio(snow_image, threshold=0.5):
        print("get_snow_pixels_ratio")

        snow_pixels = snow_image[snow_image > threshold].size
        all_pixels = snow_image.size
        ratio = snow_pixels / all_pixels

        return ratio

