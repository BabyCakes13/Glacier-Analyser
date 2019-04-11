from osgeo import gdal, gdalnumeric, gdalconst, gdal_array, osr
from util import strings
from data_gathering import configuration
import numpy

COMPOSITE_NAME = "composite.vrt"
NDSI_BAND_1 = "_B3.TIF"
NDSI_BAND_2 = "_B6.TIF"
OUT_TIFF_INT16 = "NDVI_INT16.tif"
OUT_TIFF_FLOAT32 = "NDVI_FLOAT32.tif"


class RasterHandler:

    def __init__(self, bands):

        gdal.UseExceptions()

        self.all_bands = bands
        self.tiffs, self.NDSI_bands = self.setup_NDSI_bands()
        self.rows, self.columns, self.geotransform = self.setup_NDSI_charachteristics()

        self.create_NDSI('output1.TIF')

    def create_NDSI(self, output_name, data_type=gdal.GDT_Float32):

        gdal.UseExceptions()

        # create the numpy arrays and dump the bands in them
        numpy_arrays = []
        numpy_arrays_as32 = []
        for count, band in enumerate(self.NDSI_bands, start=0):
            numpy_arrays.insert(count, band.ReadAsArray(0, 0, self.columns, self.rows))
            numpy_arrays_as32.insert(count, numpy_arrays[count].astype(numpy.float32))

        # NDVI formula
        numpy.seterr(divide='ignore', invalid='ignore')

        numerator = numpy.subtract(numpy_arrays_as32[0], numpy_arrays_as32[1])
        denominator = numpy.add(numpy_arrays_as32[0], numpy_arrays_as32[1])
        result = numpy.divide(numerator, denominator)

        result[result == -0] = -99

        geotiff = gdal.GetDriverByName('GTiff')
        parser = configuration.ReadConfig()
        output_fullpath = parser.get_output_path().joinpath(output_name)

        if data_type == gdal.GDT_UInt16:
            ndvi_int8 = numpy.multiply((result + 1), (2 ** 7 - 1))
            output = geotiff.Create(output_fullpath, self.columns, self.rows, 1, gdal.GDT_Byte)
            output_band = output.GetRasterBand(1)
            output_band.SetNoDataValue(-99)
            output_band.WriteArray(ndvi_int8)
        elif data_type == gdal.GDT_Float32:
            output = geotiff.Create(str(output_fullpath), self.columns, self.rows, 1, gdal.GDT_Float32)
            output_band = output.GetRasterBand(1)
            output_band.SetNoDataValue(-99)
            output_band.WriteArray(result)
        else:
            raise ValueError('Invalid output data type.  Valid types are gdal.UInt16 or gdal.Float32.')

            # Set the geographic transformation as the input.
        output.SetGeoTransform(self.geotransform)

        return None

    def setup_NDSI_bands(self) -> tuple:
        """Returns two lists formed of the opened NDSI tiffs (gdal.Dataset) and NDSI bands (gdal.Band)."""
        NDSI_band_paths = self.get_NDSI_band_paths()
        tiffs = []
        NDSI_bands = []

        # populate the tiffs list with the opened tiff images and extract the bands from the tiffs into the bands list
        for count, band in enumerate(NDSI_band_paths, start=0):
            tiffs.insert(count, gdal.Open(band))
            NDSI_bands.insert(count, tiffs[count].GetRasterBand(1))

        return tiffs, NDSI_bands

    def setup_NDSI_charachteristics(self) -> tuple:
        """Returns the number of rows, number of columns and the geographic data for transforming the output image."""
        rows = self.tiffs[0].RasterYSize
        columns = self.tiffs[0].RasterXSize
        geotransform = self.tiffs[0].GetGeoTransform()

        return rows, columns, geotransform

    def get_NDSI_band_paths(self) -> list:
        """Returns the full paths to the needed bands for calculating the NDSI."""
        NDSI_band_paths = []
        for band in self.all_bands:
            if NDSI_BAND_1 in band or NDSI_BAND_2 in band:
                NDSI_band_paths.append(band)

        return NDSI_band_paths



