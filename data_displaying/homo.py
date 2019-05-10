from __future__ import print_function
import cv2
import numpy as np
import sys

MAX_FEATURES = 5000
GOOD_MATCH_PERCENT = 0.05


def alignImages(im1_16bit, im2_16bit):

    im1_8bit = (im1_16bit >> 8).astype(np.uint8)
    im2_8bit = (im2_16bit >> 8).astype(np.uint8)

    cv2.namedWindow('ref', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('ref', 1000, 1000)
    cv2.moveWindow('ref', 10,10)
    cv2.imshow('ref', im2_8bit)

    cv2.namedWindow('imp', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('imp', 1000, 1000)
    cv2.moveWindow('imp', 10,10)
    cv2.imshow('imp', im1_8bit)

    while cv2.waitKey() != 27:
        pass

    print("Im1 are  ", im1_8bit.shape)
    print("Im2 are  ", im2_8bit.shape)

    print("Im1Gray are  ", im1_16bit.shape)
    print("Im2Gray are  ", im2_16bit.shape)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1_8bit, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2_8bit, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    # Draw top matches
    imMatches = cv2.drawMatches(im1_8bit, keypoints1, im2_8bit, keypoints2, matches, None)
    cv2.imwrite('matches.jpg', imMatches)

    cv2.namedWindow('dif', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('dif', 1000, 2000)
    cv2.moveWindow('dif', 10, 10)
    cv2.imshow('dif', imMatches)

    while cv2.waitKey() != 27:
        pass

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width = im1_8bit.shape
    im1Reg = cv2.warpPerspective(im1_8bit, h, (width, height))

    cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('out', 1000, 1000)
    cv2.moveWindow('out', 10,10)
    cv2.imshow('out', im1Reg)

    while cv2.waitKey() != 27:
        pass

    cv2.destroyAllWindows()

    print("AM IESIT")

    return im1Reg, h


if __name__ == '__main__':
    # Read reference image
    refFilename = sys.argv[1]
    print("Reading reference image : ", refFilename)
    imReference = cv2.imread(refFilename, cv2.IMREAD_LOAD_GDAL)
    #imReference = imReference[0:8000, 0:8000]

    # Read image to be aligned
    imFilename = sys.argv[2]
    print("Reading image to align : ", imFilename);
    im = cv2.imread(imFilename, cv2.IMREAD_LOAD_GDAL)
    #im = im[0:8000, 0:8000]

    print("Aligning images ...")
    # Registered image will be resotred in imReg.
    # The estimated homography will be stored in h.
    imReg, h = alignImages(im, imReference)

    # Write aligned image to disk.
    outFilename = sys.argv[3]
    print("Saving aligned image : ", outFilename);
    cv2.imwrite(outFilename, imReg)

    # Print estimated homography
    print("Estimated homography : \n", h)

#
