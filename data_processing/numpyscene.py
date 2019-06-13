import cv2

class SatImage:
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
