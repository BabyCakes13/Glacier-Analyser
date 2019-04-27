"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy
import os
from osgeo import gdal
from data_gathering import IO
import definitions


class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self, input_path, output_path):
        """Set the needed parameters for calculating the NDSI file."""
        gdal.UseExceptions()
        self.output = output_path
        self.input = input_path

        self.green_band, self.swir1_band, self.green_tiff, self.swir1_tiff = self.setup_NDSI_images()
        self.rows, self.columns, self.geotransform = self.setup_NDSI_characteristics()

        self.division = self.calculate_NDSI(gdal.GDT_Byte)
        self.create_NDSI(definitions.OUT_TIFF_UINT8, gdal.GDT_Byte)

    def calculate_NDSI(self, data_type) -> numpy.ndarray:
        """Calculates the NDSI as numpy array, based on the specified data type.
        @:return numpy array representing the resulted NDSI numpy array."""
        print("calculate NDSI")
        numpy_array_green_asFloat32 = self.green_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)
        numpy_array_swir1_asFloat32 = self.swir1_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)

        numpy.seterr(divide='ignore', invalid='ignore')

        numerator = numpy.subtract(
            numpy_array_green_asFloat32,
            numpy_array_swir1_asFloat32
        )
        numerator = numpy.multiply(numerator, 0x7FFF)

        denominator = numpy.add(
            numpy_array_green_asFloat32,
            numpy_array_swir1_asFloat32
        )

        division = numpy.floor_divide(
            numerator,
            denominator
        )

        print("after")
        division[division != division] = 0

        if data_type == gdal.GDT_UInt16:
            division = numpy.add(division, 0x7FFF)
        if data_type == gdal.GDT_Byte:
            division[division <= definitions.THRESHOLD] = 0

        return division

    def create_NDSI(self, output_name, data_type):
        """Create the NDSI tiff image from the result of the NDSI formula."""
        print("create_NDSI")

        geotiff = gdal.GetDriverByName('GTiff')

        output_path = str(os.path.join(self.output, output_name))
        output_tiff = geotiff.Create(output_path, self.columns, self.rows, 1, data_type)
        output_band = output_tiff.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(self.division)

    def setup_NDSI_images(self) -> tuple:
        """Returns the bands and tiffs for the NDSI calculator.
        @:return Tuple with objects of the type gdal.Band and gdal.Dataset."""
        ndsi_path_parser = IO.InputOutput(self.input)
        green_path, swir1_path = ndsi_path_parser.get_ndsi_bands_paths()

        green_tiff = gdal.Open(green_path)
        swir1_tiff = gdal.Open(swir1_path)

        green_band = green_tiff.GetRasterBand(1)
        swir1_band = swir1_tiff.GetRasterBand(1)

        return green_band, swir1_band, green_tiff, swir1_tiff

    def setup_NDSI_characteristics(self) -> tuple:
        """Returns the number of rows, number of columns and the geographic data for transforming the output image."""
        rows = self.green_tiff.RasterYSize
        columns = self.swir1_tiff.RasterXSize
        geotransform = self.green_tiff.GetGeoTransform()

        return rows, columns, geotransform
