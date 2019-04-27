"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy
import os
from osgeo import gdal
import pathlib
import definitions
from data_gathering import IO


class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Set the needed parameters for calculating the NDSI file."""
        gdal.UseExceptions()
        self.IO_parser = IO.InputOutput()

        self.green_tiff, self.swir1_tiff = self.setup_NDSI_tiffs()
        self.green_band, self.swir1_band = self.setup_NDSI_bands()
        self.rows, self.columns, self.geotransform = self.setup_NDSI_characteristics()

        self.create_NDSI(definitions.OUT_TIFF_UINT8, gdal.GDT_Byte)

    def calculate_ndsi(self, data_type) -> numpy.ndarray:
        """Calculates the NDSI as numpy array, based on the specified data type.
        @:return numpy array representing the resulted NDSI numpy array."""
        numpy_array_green_asFloat32 = self.green_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)
        numpy_array_swir1_asFloat32 = self.swir1_band.ReadAsArray(0, 0, self.columns, self.rows).astype(numpy.int32)

        # NDSI formula
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

        division[division != division] = 0

        if data_type == gdal.GDT_UInt16:
            division = numpy.add(division, 0x7FFF)
        if data_type == gdal.GDT_Byte:
            division[division <= definitions.THRESHOLD] = 0

        return division

    def create_NDSI(self, output_name, data_type) -> pathlib.Path:
        """Create the NDSI tiff image from the result of the NDSI formula.
        @:return Path to the NDSI tiff image."""
        division = self.calculate_ndsi(data_type)

        geotiff = gdal.GetDriverByName('GTiff')

        output_path = os.path.join(definitions.OUTPUT_DIR, output_name)
        output_tiff = geotiff.Create(str(output_path), self.columns, self.rows, 1, data_type)
        output_band = output_tiff.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(division)

        return output_path

    def setup_NDSI_bands(self) -> tuple:
        """Returns the opened bands necessary for the NDSI formula.
        @:return Tuple with objects of the type gdal.Band."""
        green_band = self.green_tiff.GetRasterBand(1)
        swir1_band = self.swir1_tiff.GetRasterBand(1)

        return green_band, swir1_band

    def setup_NDSI_tiffs(self) -> tuple:
        """Returns the opened tiff bands for the NDSI calculator.
        @:return Tuple with objects of the type gdal.Dataset."""
        green_path, swir1_path = self.IO_parser.get_NDSI_band_paths()

        green_tiff = gdal.Open(str(green_path))
        swir1_tiff = gdal.Open(str(swir1_path))

        return green_tiff, swir1_tiff

    def setup_NDSI_characteristics(self) -> tuple:
        """Returns the number of rows, number of columns and the geographic data for transforming the output image."""
        rows = self.green_tiff.RasterYSize
        columns = self.green_tiff.RasterXSize
        geotransform = self.green_tiff.GetGeoTransform()

        return rows, columns, geotransform

