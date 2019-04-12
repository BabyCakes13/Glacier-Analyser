"""Module which contains the class which creates the Normalised Difference Snow Index (NDSI) file."""
import numpy
from osgeo import gdal
import pathlib
from util import strings
from data_gathering import configuration, IO

OUT_TIFF_INT16 = "NDSI_INT16.tif"
OUT_TIFF_FLOAT32 = "NDSI_FLOAT32.tif"
VALID_DATA_TYPES = [gdal.GDT_UInt16, gdal.GDT_Float32]


class NDSI:
    """Class which handles the creation of the Normalised Difference Snow Index (NDSI) file."""

    def __init__(self):
        """Set the needed parameters for calculating the NDSI file."""
        self.IO_parser = IO.InputBands()

        self.tiffs, self.NDSI_bands = self.setup_NDSI_bands()
        self.rows, self.columns, self.geotransform = self.setup_NDSI_characteristics()

        self.create_NDSI(OUT_TIFF_INT16, gdal.GDT_Float32)

    def create_NDSI(self, output_name, data_type) -> pathlib.Path:
        """Returns the full path to the outputted NDSI image."""
        if data_type not in VALID_DATA_TYPES:
            print(strings.error_messages()[0])
            exit(-1)

        gdal.UseExceptions()

        # create the numpy arrays and dump the bands in them
        numpy_arrays = []
        numpy_arrays_as32 = []
        for count, band in enumerate(self.NDSI_bands, start=0):
            numpy_arrays.insert(count, band.ReadAsArray(0, 0, self.columns, self.rows))
            numpy_arrays_as32.insert(count, numpy_arrays[count].astype(numpy.float32))

        # NDsI formula
        numpy.seterr(divide='ignore', invalid='ignore')
        numerator = numpy.subtract(numpy_arrays_as32[0], numpy_arrays_as32[1])
        denominator = numpy.add(numpy_arrays_as32[0], numpy_arrays_as32[1])
        result = numpy.divide(numerator, denominator)

        # transform the -0's resulted from the 0 division in -99
        # transform the -0's resulted from the 0 division in -99
        result[result == -0] = -99

        geotiff = gdal.GetDriverByName('GTiff')
        config_parser = configuration.ReadConfig()
        output_fullpath = str(config_parser.get_output_path().joinpath(output_name))

        # In case the output is int6 ([-1,1]), convert values to [0,255] to create a int6 geotiff with one band
        if data_type == gdal.GDT_UInt16:
            result = numpy.multiply((result + 1), (2 ** 7 - 1))
            data_type = gdal.GDT_Byte

        # setup the output image
        output_tiff = geotiff.Create(output_fullpath, self.columns, self.rows, 1, data_type)
        output_band = output_tiff.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(result)

        return output_fullpath

    def setup_NDSI_bands(self) -> tuple:
        """Returns two lists formed of the opened NDSI tiffs (gdal.Dataset) and NDSI bands (gdal.Band)."""
        gdal.UseExceptions()

        # get the NDSI bands full paths for opening
        NDSI_band_paths = self.IO_parser.get_NDSI_band_paths()
        NDSI_tiffs = []
        NDSI_bands = []

        # populate the tiffs list with the opened tiff images and extract the bands from the tiffs into the bands list
        for count, band in enumerate(NDSI_band_paths, start=0):
            NDSI_tiffs.insert(count, gdal.Open(band))
            NDSI_bands.insert(count, NDSI_tiffs[count].GetRasterBand(1))

        return NDSI_tiffs, NDSI_bands

    def setup_NDSI_characteristics(self) -> tuple:
        """Returns the number of rows, number of columns and the geographic data for transforming the output image."""
        gdal.UseExceptions()

        rows = self.tiffs[0].RasterYSize
        columns = self.tiffs[0].RasterXSize
        geotransform = self.tiffs[0].GetGeoTransform()

        return rows, columns, geotransform
