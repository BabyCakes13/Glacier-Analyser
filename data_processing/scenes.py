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

    def __init__(self, green_path, swir1_path):
        """
        Class holding the pair of B3 and B6 bands.
        :param green_path: Full path to the green band.
        :param swir1_path: Full path to the swir1 band.
        """
        self.green_path = green_path
        self.swir1_path = swir1_path

    def get_scene_name(self) -> str:
        """
        Returns the scene name based on the green band.
        :return: Name of the scene
        """
        input_dir, band = os.path.split(self.green_path)
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

    def __init__(self, green_numpy, swir1_numpy) -> None:
        """
        Initializes the green and swir1 images.
        :param green_numpy: Green band.
        :param swir1_numpy: Swir1 band.
        """
        self.green_numpy = green_numpy
        self.swir1_numpy = swir1_numpy

    @staticmethod
    def read(path_scene):
        """
        Reads a simple path scene and opens the images found in the path as GDAL images.
        :param path_scene: The input scene.
        :return: Returns the created NumpyScene image.
        """
        img = NumpyScene(cv2.imread(path_scene.green_path, cv2.IMREAD_LOAD_GDAL),
                         cv2.imread(path_scene.swir1_path, cv2.IMREAD_LOAD_GDAL))
        return img

    def write(self, file_path) -> None:
        """
        Write numpy scene to the disk using the file's path.
        :param file_path: Path from the PathScene scene.
        :return: Nothing.
        """
        cv2.imwrite(file_path.green_path, self.green_numpy)
        cv2.imwrite(file_path.swir1_path, self.swir1_numpy)


class NumpySceneWithNDSI(NumpyScene):
    """
    Class which holds the numpy images with the NDSI image as well.
    """

    def __init__(self, green_numpy, swir1_numpy, ndsi_numpy):
        """
        Initialize the green, swir1 and ndsi images for the scene.
        :param green_numpy: Green image.
        :param swir1_numpy: Swir1 image.
        :param ndsi_numpy: NDSI image.
        """
        NumpyScene.__init__(self, green_numpy, swir1_numpy)
        self.ndsi = ndsi_numpy

    def write(self, file_path) -> None:
        """
        Write the images to the disk using the path specified in the PathScene image.
        :param file_path: Path to the scene.
        :return: Nothing.
        """
        NumpyScene.write(self, file_path)

        path = os.path.split(file_path.green_path)[0]
        ndsi_path = os.path.join(path, file_path.get_scene_name() + "_NDSI.TIF")
        normalized = cv2.normalize(self.ndsi, None, 0, (1 << 16) - 1, cv2.NORM_MINMAX, cv2.CV_16UC1)

        cv2.imwrite(ndsi_path, normalized)


class DISPLAY:
    """
    Class which enables image viewing by cv2 only if the do_it attribute is set.
    """
    do_it = False

    @staticmethod
    def numpy_scene(window_prefix, numpy_scene) -> None:
        """
        Displays the green and swir1 bands from the NumpyScene.
        :param window_prefix: The prefix name of the window to be displayed.
        :param numpy_scene: NumpyScene object.
        :return: None.
        """
        if not DISPLAY.do_it:
            return
        DISPLAY.image(window_prefix + "_green", numpy_scene.green)
        DISPLAY.image(window_prefix + "_swir", numpy_scene.swir)

    @staticmethod
    def numpy_scene_with_ndsi(window_prefix, numpy_scene_with_ndsi) -> None:
        """
        Displays the green and swir1 bands from the NumpySceneWithNDSI.
        :param window_prefix: The name of the window to be displayed.
        :param numpy_scene_with_ndsi: NumpyScene object.
        :return: 
        """
        if not DISPLAY.do_it:
            return
        DISPLAY.image(window_prefix + "_green", numpy_scene_with_ndsi.green)
        DISPLAY.image(window_prefix + "_swir", numpy_scene_with_ndsi.swir)
        DISPLAY.image(window_prefix + "_ndsi", numpy_scene_with_ndsi.ndsi)

    @staticmethod
    def image(window_name, image, normalize=True) -> None:
        """
        Displays an image in a cv2 window.
        :param normalize: Check if wanting it in 8bit.
        :param window_name: Name of the cv2 window.
        :param image: cv2 image.
        :return: Nothing.
        """
        if not DISPLAY.do_it:
            return

        if normalize:
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.imshow(window_name, image)

    @staticmethod
    def wait() -> None:
        """
        Flushes the display image after pressing exit key.
        :return: Nothing.
        """
        if not DISPLAY.do_it:
            return
        while cv2.waitKey() != 27:
            pass
