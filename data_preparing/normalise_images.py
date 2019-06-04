"""Module to normalise images based on sun elevation."""
import cv2
import numpy
import os


class Normalise:
    def __init__(self, directory):
        self.directory = directory

    def parse_directory(self):
        for file in os.listdir(self.directory):
            if file.endswith(".TIF"):
                print("Normalising ", file)

                file_path = self.directory + file
                image = cv2.imread(file_path, cv2.IMREAD_LOAD_GDAL)

                print("Maximum value: ", image.max())
                print("Minimum value: ", image.min())

                image_8bit = (image >> 8).astype(numpy.uint8)

                print("Maximum value: ", image_8bit.max())
                print("Minimum value: ", image_8bit.min())

                normalised_image = self.normalise(image_8bit)
                normalised_filename = self.directory + "normalised_" + file
                print(normalised_filename)
                cv2.imwrite(normalised_filename, normalised_image)

    @staticmethod
    def normalise(image):
        """Scale image to an interval."""
        print("START.......................")
        print("Maximum value: ", image.max())
        print("Minimum value: ", image.min())

        result = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

        print("Maximum value after normalising: ", result.max())
        print("Minimum value after normalising: ", result.min())

        return result

    @staticmethod
    def setup_image_window(image):
        """Setup the window to see the image."""
        cv2.namedWindow('Brightened', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Brightened', 1000, 1000)
        cv2.moveWindow('Brightened', 10, 10)
        cv2.imshow('Brightened', image)

        while cv2.waitKey() != 27:
            pass


if __name__ == "__main__":

    normal = "/storage/maria/D/Programming/Facultate/test_input_dir/AF5X14005043_70.969_37.903/"
    normalised = Normalise(normal)
    normalised.parse_directory()



