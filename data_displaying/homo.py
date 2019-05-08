from __future__ import print_function
import cv2
import numpy as np
import sys

MAX_FEATURES = 2500
GOOD_MATCH_PERCENT = 0.25


def alignImages(im1, im2):
    # Convert images to grayscale
    im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    # Draw top matches
    imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
    cv2.imwrite('matches.jpg', imMatches)

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width, channels = im2.shape
    im1Reg = cv2.warpPerspective(im1, h, (width, height))

    cv2.namedWindow('ref', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('ref', 1000, 1000)
    cv2.moveWindow('ref', 10,10)
    cv2.imshow('ref', im2)

    cv2.namedWindow('imp', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('imp', 1000, 1000)
    cv2.moveWindow('imp', 10,10)
    cv2.imshow('imp', im1)

    cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('out', 1000, 1000)
    cv2.moveWindow('out', 10,10)
    cv2.imshow('out', im1Reg)
    """
    diffImg = cv2.drawMatches(im2, keypoints2, im1, keypoints1, matches, None)
    cv2.namedWindow('dif', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('dif', 1000, 2000)
    cv2.moveWindow('dif', 10, 10)
    cv2.imshow('dif', diffImg)
    """

    while cv2.waitKey() != 27:
        pass

    cv2.destroyAllWindows()

    print("AM IESIT")

    return im1Reg, h


if __name__ == '__main__':
    # Read reference image
    refFilename = sys.argv[1]
    print("Reading reference image : ", refFilename)
    imReference = cv2.imread(refFilename, cv2.IMREAD_COLOR)
    imReference = imReference[0:8000, 0:8000]

    # Read image to be aligned
    imFilename = sys.argv[2]
    print("Reading image to align : ", imFilename);
    im = cv2.imread(imFilename, cv2.IMREAD_COLOR)
    im = im[0:8000, 0:8000]

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
