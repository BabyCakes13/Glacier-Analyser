import cv2
import os
import definitions


class Scene:
    def __init__(self, green_band, swir1_band):
        """
        Class holding the pair of B3 and B6 bands.
        :param green_band: Full path to the green band.
        :param swir1_band: Full path to the swir1 band.
        """
        self.green_band = green_band
        self.swir1_band = swir1_band

    def get_scene_name(self) -> str:
        """
        Returns the scene name based on the green band.
        :return: Name of the scene
        """
        input_dir, band = os.path.split(self.green_band)
        scene = None

        if band.endswith(definitions.GREEN_BAND_END):
            split = band.split(definitions.SWIR1_BAND_END)
            scene = split[0]
        else:
            print("The file is not the green band.")

        return str(scene)


class SatImage:
    """
    Satellite image holding a scene.
    """
    def __init__(self, green, swir):
        self.green = green
        self.swir = swir

    @staticmethod
    def read(image_scene):
        img = SatImage(cv2.imread(image_scene.green_band, cv2.IMREAD_LOAD_GDAL),
                       cv2.imread(image_scene.swir1_band, cv2.IMREAD_LOAD_GDAL))
        return img

    def write(self, filename):
        cv2.imwrite(filename.green_band, self.green)
        cv2.imwrite(filename.swir1_band, self.swir)


class SatImageWithNDSI(SatImage):
    def __init__(self, green, swir, ndsi):
        SatImage.__init__(self, green, swir)
        self.ndsi = ndsi

    def write(self, filename):
        SatImage.write(self, filename)

        path = os.path.split(filename.green_band)[0]
        ndsipath = os.path.join(path, filename.get_scene_name() + "_NDSI.TIF")

        print("write this ", ndsipath)
        normalized = cv2.normalize(self.ndsi, None, 0, (1 << 16) - 1, cv2.NORM_MINMAX, cv2.CV_16UC1)

        cv2.imwrite(ndsipath, normalized)
