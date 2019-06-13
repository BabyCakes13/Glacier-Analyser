"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy
import os
from osgeo import gdal

from data_processing.numpyscene import SatImage

class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Set the variables needed for computing the ndsi band and actually compute the ndsi band."""
        #gdal.UseExceptions()

    # https://nsidc.org/support/faq/what-ndsi-snow-cover-and-how-does-it-compare-fsc
    # says that NDSI = (Band green - band SWIR) / (Band green + Band SWIR)
    def calculate_NDSI(satimage, math_dtype=numpy.float32):

        green_nan = satimage.green.astype(math_dtype)
        swir_nan = satimage.swir.astype(math_dtype)

        green_nan[green_nan == 0] = numpy.nan
        swir_nan[swir_nan == 0] = numpy.nan

        # change image bit depth to 32 bit to allow math without saturation
        img = SatImage(green_nan, swir_nan)

        #ignore division by zero because image has borders with 0 values
        numpy.seterr(divide='ignore', invalid='ignore')

        numerator = numpy.subtract(img.green, img.swir)
        if(math_dtype == numpy.int32):
            numerator = numpy.multiply(numerator, 0x7FFF) #TODO: why god why
        denominator = numpy.add(img.green, img.swir)
        ndsi = numpy.divide(numerator, denominator)

        # interpret each NaN value as 0
        ndsi[ndsi != ndsi] = -1

        if(math_dtype == numpy.int32):
            ndsi = numpy.add(ndsi, 0x7FFF)

        print("ndsi data range is ", ndsi.min(), " ", ndsi.max())

        return ndsi

    def getSnowImage(ndsi, threshold=0.5):
        snow = ndsi
        snow[snow <= threshold] = -1
        return snow

    def getGlacierPixels(snowImage, threashold=0.5):

        n = len(snowImage[snowImage > threashold])

        return n

#
#   def open_and_calculate_NDSI(self, data_type) -> numpy.ndarray:
#       """Calculates the NDSI as numpy array, based on the specified data type.
#       @:return numpy array representing the resulted NDSI numpy array."""
#
#       numpy_array_green_asFloat32 = self.green_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)
#       numpy_array_swir1_asFloat32 = self.swir1_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)
#
#       numpy.seterr(divide='ignore', invalid='ignore')
#
#       numerator = numpy.subtract(
#           numpy_array_green_asFloat32,
#           numpy_array_swir1_asFloat32
#       )
#       numerator = numpy.multiply(numerator, 0x7FFF)
#
#       denominator = numpy.add(
#           numpy_array_green_asFloat32,
#           numpy_array_swir1_asFloat32
#       )
#
#       division = numpy.floor_divide(
#           numerator,
#           denominator
#       )
#
#       division[division != division] = 0
#
#       if data_type == gdal.GDT_UInt16:
#           division = numpy.add(division, 0x7FFF)
#       if data_type == gdal.GDT_Byte:
#           division[division <= self.threshold] = 0
#
#       return division
#
#   def create_NDSI(self, output_name, data_type) -> gdal.Band:
#       """Create the NDSI tiff image from the result of the formula.
#       @return gdal.Band object which represents the resulting NDSI band."""
#       print("Create NDSI ", output_name)
#
#       geotiff = gdal.GetDriverByName('GTiff')
#       output_path = str(os.path.join(self.output_dir, output_name))
#       output_tiff = geotiff.Create(output_path, self.columns, self.rows, 1, data_type)
#
#       output_band = output_tiff.GetRasterBand(1)
#       output_band.SetNoDataValue(-99)
#       output_band.WriteArray(self.division)
#
#       print("Done NDSI ", output_path)
#
#       return output_band
#
#   def setup_NDSI_images(self) -> tuple:
#       """Returns the bands and tiffs for the NDSI calculator.
#       @:return Tuple with objects of the type gdal.Band and gdal.Dataset."""
#
#       green_tiff = gdal.Open(self.green_path)
#       swir1_tiff = gdal.Open(self.swir1_path)
#
#       green_band = green_tiff.GetRasterBand(1)
#       swir1_band = swir1_tiff.GetRasterBand(1)
#
#       return green_band, swir1_band, green_tiff, swir1_tiff
#
#   def setup_NDSI_characteristics(self) -> tuple:
#       """Returns the number of rows, number of columns and the geographic data for transforming the output image."""
#       rows = self.green_tiff.RasterYSize
#       columns = self.green_tiff.RasterXSize
#       geotransform = self.green_tiff.GetGeoTransform()
#
#       return rows, columns, geotransform
