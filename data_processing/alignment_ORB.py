from __future__ import print_function
import cv2
import numpy as np
import os
import sys

DISPLAY=0
DEBUG=False

# align
MAX_FEATURES = 5000
GOOD_MATCH_PERCENT = 0.50
ALLOWED_ERROR = 0.5
ALLOWED_INTEGRAL = 100
EUCLIDIAN_DISTANCE = 200

N_R = 8
N_C = 8

class Align:
    def __init__(self, reference_8bit, current_image8bit, cfn):

        self.reference_8bit = reference_8bit
        self.current_image_8bit = cv2.normalize(current_image8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

        self.result_8bit = None
        self.matches = None

        self.cfn = cfn


    def boxedDetectAndCompute(self, image):
        orb = cv2.ORB_create(nfeatures=MAX_FEATURES // N_R // N_C, scaleFactor=2, patchSize=100)

        keypoints=[]

        for x in range(0,N_C):
            for y in range(0, N_R):
                x0 = x * image.shape[1] // N_C
                x1 = (x+1) * image.shape[1] // N_C
                y0 = y * image.shape[0] // N_R
                y1 = (y+1) * image.shape[0] // N_R

                #print ("BBOX "," ", x0,"-", x1," ", y0,"-", y1 )
                imagebox = image[y0:y1 , x0:x1]
                #self.display_image('BOX ' + str(x) + str(y), imagebox)

                keypoints_bbox = orb.detect(imagebox)

                for kp in keypoints_bbox:
                    kp.pt = (kp.pt[0] + x0, kp.pt[1] + y0)
                    keypoints.append(kp)

#        keypoints = orb.detect(image)
        keypoints, descriptors = orb.compute(image, keypoints)

        return keypoints, descriptors;

    def find_matches(self):
        """Returns whether the homography finding was succesfull or not."""
        # transform from scientific notation to decimal for easy check
        np.set_printoptions(suppress=True, precision=4)

        keypoints_ref, descriptors_ref = self.boxedDetectAndCompute(self.reference_8bit)
        keypoints_img, descriptors_img = self.boxedDetectAndCompute(self.current_image_8bit)

#        print("Keypoints 1 length ", len(keypoints_ref))
#        print("Keypoints 2 length ", len(keypoints_img))
#        print("Descriptor 1 ", descriptors_ref)
#        print("Descriptor 2 ", descriptors_img)

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors_ref, descriptors_img)

        # best matches first
        matches.sort(key=lambda x: x.distance, reverse=False)

        # remove matches with low score
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # prepare the arras which hold the matches location
        points_list_ref = []
        points_list_img = []

        matches_pruned=[]
        # fill points from the matcher
        for i, match in enumerate(matches):
            refpt = keypoints_ref[match.queryIdx].pt
            imgpt = keypoints_img[match.trainIdx].pt

#            print ( "tip: ", type(refpt),
#                    "  x  ", refpt[0] - imgpt[0],
#                    "  y  ", refpt[1] - imgpt[1])

            if ((abs(refpt[0] - imgpt[0]) < EUCLIDIAN_DISTANCE) and
                (abs(refpt[1] - imgpt[1]) < EUCLIDIAN_DISTANCE)):
                points_list_ref.append(keypoints_ref[match.queryIdx].pt)
                points_list_img.append(keypoints_img[match.trainIdx].pt)
                matches_pruned.append(match)

        points_ref = np.array(points_list_ref)
        points_img = np.array(points_list_img)

        # draw the best matches
        prunedmatches = cv2.drawMatches(self.reference_8bit, keypoints_ref,
                                        self.current_image_8bit, keypoints_img,
                                        matches_pruned,
                                        None, matchColor=(0,255,255), singlePointColor=(100,0,0),
                                        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        if (DISPLAY):
            self.display_image('prunedMATCHES', prunedmatches)

        height, width = self.reference_8bit.shape
        if False:
            # find homography
            homography, mask = cv2.findHomography(points_img, points_ref, cv2.RANSAC)
            VALID = self.validate_transform(homography)
            self.result_8bit = cv2.warpPerspective(self.current_image_8bit, homography, (width, height))
        else:
            inliers=None
            affine, inliers = cv2.estimateAffine2D(points_img, points_ref, inliers, method=cv2.LMEDS, confidence=0.99)

            for inl, refpt, imgpt in zip(inliers, points_img, points_ref):
                status = None
                if (inl == 1):
                    status = "inlier"
                else:
                    status = "outlier"
                if(DEBUG):
                    print (status , refpt[0] ,
                           "  x  ", refpt[0] - imgpt[0],
                           "  y  ", refpt[1] - imgpt[1])

            print("affine \n",
                  affine)
            self.result_8bit = cv2.warpAffine(self.current_image_8bit, affine, (width, height))
            VALID = self.validate_transform(affine)

        return VALID, prunedmatches

    def validate_transform(self, transform):
        # convert from scientific notation to decimal notation for better data interpretation
        np.set_printoptions(suppress=True, precision=4)

        w = transform.shape[1]
        h = transform.shape[0]

        identity = np.identity(3)
        identity = identity[0:h , 0:w]
        difference = np.absolute(np.subtract(identity, transform))
        compare = self.create_comparison_matrix(h, w)

        print("Transform \n", transform)
        print("Difference \n", difference)
        print("Comparison \n", compare)

        if np.less_equal(difference, compare).all():
            print("Transform is good.")
            return True
        else:
            print("Transform is not good.")
            return False

    @staticmethod
    def create_comparison_matrix(w=3, h=3):
        """Creates the matrix for comparing."""
        comparison = np.full((w, h), ALLOWED_ERROR)
        comparison[0, 2] = ALLOWED_INTEGRAL
        comparison[1, 2] = ALLOWED_INTEGRAL

        return comparison

    @staticmethod
    def display_image(window_name, image):
        """Display the image in a window."""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 1000)
        cv2.moveWindow(window_name, 10, 10)
        cv2.imshow(window_name, image)

    @staticmethod
    def display_image_flush():
        while cv2.waitKey() != 27:
            pass

def percentage(percent, image) -> tuple:
    """Find what is percent from whole."""
    height, width = image.shape
    height = (percent * height) // 100
    width = (percent * width) // 100

    return width, height


def start_alignment(reference_filename, image_filename, result_filename, processed_output_dir):
    """Starts the alignment process."""
    result_path = os.path.join(processed_output_dir, result_filename)
    print_messages(reference_filename, image_filename, result_path)

    # prepare the images for alignment
    normalised_reference_8bit, current_image_8bit, \
    scaled_normalised_reference_8bit, scaled_current_image_8bit = resize_depth(reference_filename, image_filename)

    aligner = Align(normalised_reference_8bit, current_image_8bit, result_filename)
    VALID, matchesimage = aligner.find_matches()

    if VALID:
        cv2.imwrite(result_path, aligner.result_8bit)
    cv2.imwrite(result_path + "match.TIF", matchesimage)

    if(DISPLAY):
        aligner.display_image("Rerefence", aligner.reference_8bit)
        aligner.display_image("Current Image", aligner.current_image_8bit)
        aligner.display_image("Result", aligner.result_8bit)
        aligner.display_image_flush()

    cv2.destroyAllWindows()

    return VALID

def print_messages(reference_filename, image_filename, aligned_filename):
    print("\n\n")
    print("Reference filename: ", reference_filename)
    print("Image filename ", image_filename)
    print("Aligned filename  ", aligned_filename)


def resize_depth(reference_filename, image_filename):
    """Resize the depth of the images from 16 to 8 pixels.
    Normalise reference.
    Scale images."""

    reference_16bit = cv2.imread(reference_filename, cv2.IMREAD_LOAD_GDAL)
    current_image_16bit = cv2.imread(image_filename, cv2.IMREAD_LOAD_GDAL)

    reference_8bit = (reference_16bit >> 8).astype(np.uint8)
    current_image_8bit = (current_image_16bit >> 8).astype(np.uint8)

    normalised_reference_8bit = cv2.normalize(reference_8bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC2)

    scaled_normalised_reference_8bit = cv2.resize(normalised_reference_8bit, percentage(20, normalised_reference_8bit))
    scaled_current_image_8bit = cv2.resize(current_image_8bit, percentage(20, current_image_8bit))

    return normalised_reference_8bit, current_image_8bit, scaled_normalised_reference_8bit, scaled_current_image_8bit

if __name__ == "__main__":
    try:
        VALID = start_alignment(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    except KeyboardInterrupt:
        sys.exit(3)

    if(VALID):
        sys.exit(0)
    else:
        sys.exit(1)
