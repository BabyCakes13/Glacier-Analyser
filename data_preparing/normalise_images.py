"""Module to normalise images based on sun elevation."""
import cv2
import numpy


class Brighten:
    def __init__(self, image, brightness):
        """Adjust the brightness to an image."""
        image = cv2.imread(image, cv2.IMREAD_LOAD_GDAL)

        self.image_8bit = (image >> 8).astype(numpy.uint8)
        self.brightness = brightness

    def brighten_up(self):
        """Brighten image up by brightness."""
        brightened = numpy.where((255 - self.image_8bit) < self.brightness, 255, self.image_8bit + self.brightness)
        return brightened

    @staticmethod
    def scale(array, min_value, max_value):
        """Scale image to an interval."""
        nominator = (array - array.min()) * (max_value - min_value)
        denominator = array.max() - array.min()
        denominator = denominator + (denominator is 0)
        return min_value + nominator // denominator

    @staticmethod
    def setup_image_window(image):
        """Setup the window to see the image."""
        cv2.namedWindow('Brightened', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Brightened', 1000, 1000)
        cv2.moveWindow('Brightened', 10, 10)
        cv2.imshow('Brightened', image)

        while cv2.waitKey() != 27:
            pass
