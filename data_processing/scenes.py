"""
Module which holds the two scene formats for a Landsat 8 scene.
"""
import os

import cv2

import definitions


class PathScene:
    """
    Class which holds the paths to green and swir1 band of a scene.
    """

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
            split = band.split(definitions.GREEN_BAND_END)
            scene = split[0]
        else:
            print("The file is not the green band.")

        return str(scene)


class NumpyScene:
    """
    Class which holds the numpy arrays containing the images for the green and swir1 bands.
    """

    def __init__(self, green, swir) -> None:
        """
        Initializes the green and swir1 images.
        :param green: Green band.
        :param swir: Swir1 band.
        """
        self.green = green
        self.swir = swir

    @staticmethod
    def read(image_scene):
        """
        Reads a simple path scene and opens the images found in the path as GDAL images.
        :param image_scene: The input scene.
        :return: Returns the created NumpyScene image.
        """
        img = NumpyScene(cv2.imread(image_scene.green_band, cv2.IMREAD_LOAD_GDAL),
                         cv2.imread(image_scene.swir1_band, cv2.IMREAD_LOAD_GDAL))
        return img

    def write(self, filepath) -> None:
        """
        Write numpy scene to the disk using the file's path.
        :param filepath: Path from the PathScene scene.
        :return: Nothing.
        """
        cv2.imwrite(filepath.green_band, self.green)
        cv2.imwrite(filepath.swir1_band, self.swir)


class NumpySceneWithNDSI(NumpyScene):
    """
    Class which holds the numpy images with the NDSI image as well.
    """

    def __init__(self, green, swir, ndsi):
        """
        Initialize the green, swir1 and ndsi images for the scene.
        :param green: Green image.
        :param swir: Swir1 image.
        :param ndsi: NDSI image.
        """
        NumpyScene.__init__(self, green, swir)
        self.ndsi = ndsi

    def write(self, filepath) -> None:
        """
        Write the images to the disk using the path specified in the PathScene image.
        :param filepath: Path to the scene.
        :return: Nothing.
        """
        NumpyScene.write(self, filepath)

        path = os.path.split(filepath.green_band)[0]
        ndsi_path = os.path.join(path, filepath.get_scene_name() + "_NDSI.TIF")
        normalized = cv2.normalize(self.ndsi, None, 0, (1 << 16) - 1, cv2.NORM_MINMAX, cv2.CV_16UC1)

        cv2.imwrite(ndsi_path, normalized)


class DISPLAY:
    DOIT = False

    @staticmethod
    def satimage(window_prefix, satimage):
        if not DISPLAY.DOIT:
            return
        DISPLAY.image(window_prefix + "_green", satimage.green)
        DISPLAY.image(window_prefix + "_swir", satimage.swir)

    @staticmethod
    def satimage_with_ndsi(window_prefix, satimagewithndsi):
        if not DISPLAY.DOIT:
            return
        DISPLAY.image(window_prefix + "_green", satimagewithndsi.green)
        DISPLAY.image(window_prefix + "_swir", satimagewithndsi.swir)
        DISPLAY.image(window_prefix + "_ndsi", satimagewithndsi.ndsi)

    @staticmethod
    def image(window_name, image, normalize=True):
        """
        Displays an image in a cv2 window.
        :param normalize: Check if wanting it in 8bit.
        :param window_name: Name of the cv2 window.
        :param image: cv2 image.
        :return: Nothing.
        """
        if not DISPLAY.DOIT:
            return

        if normalize:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.imshow(window_name, image)

    @staticmethod
    def wait():
        """
        Flushes the display image after pressing exit key.
        :return: Nothing.
        """
        if not DISPLAY.DOIT:
            return
        while cv2.waitKey() != 27:
            pass
