import cv2
import numpy as np
import sys

def image(window_name, image):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1000, 1000)
    cv2.imshow(window_name, image)


frame1 = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
frame2 = cv2.imread(sys.argv[2], cv2.IMREAD_GRAYSCALE)

frame1_c = cv2.cvtColor(frame1, cv2.COLOR_GRAY2BGR)
hsv = np.zeros_like(frame1_c)

#remove border areas resulted from alignment of actual image features
ret1,thresh1 = cv2.threshold(frame1,1,255, cv2.THRESH_BINARY)
ret2,thresh2 = cv2.threshold(frame2,1,255, cv2.THRESH_BINARY)
frame1 = cv2.bitwise_and(frame1, thresh2)
frame2 = cv2.bitwise_and(frame2, thresh1)
image('frame1',frame1)
image('frame2',frame2)

flow = cv2.calcOpticalFlowFarneback(frame1, frame2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
hsv[...,0] = ang*180/np.pi/2

COLS = hsv.shape[1]
for col in range(COLS):
    for rows in range(10):
        hsv[rows, col, 0] = col * 255 / 7000

hsv[...,1] = 255
hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
hsv[...,2] = hsv[...,2] * 2
bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
image('opencv',bgr)


frame1_16bit = np.int16(frame1)
frame2_16bit = np.int16(frame2)


print ("in : ", "min ", frame1.min(), " max ", frame1.max(), " type: ", type(frame1[0][0]))
print ("out: ", "min ", frame1_16bit.min(), " max ", frame1_16bit.max(), " type: ", type(frame1_16bit[0][0]))

frame1_16bit_n = cv2.normalize(frame1_16bit, None, 0, 255, cv2.NORM_MINMAX)
frame1_16bit_n = np.uint8(frame1_16bit_n)

print ("out_n: ", "min ", frame1_16bit_n.min(), " max ", frame1_16bit_n.max(), " type: ", type(frame1_16bit_n[0][0]))

#image('frame116bit', frame1_16bit_n)


frame_diff = frame1_16bit - frame2_16bit

frame_diff_n = cv2.normalize(frame_diff, None, 0, 255, cv2.NORM_MINMAX)
frame_diff_n = np.uint8(frame_diff_n)

cm_frame_diff_n = cv2.applyColorMap(frame_diff_n, cv2.COLORMAP_JET);

image('diff', cm_frame_diff_n)

while cv2.waitKey(0) & 0xff != 27:
    pass

cv2.destroyAllWindows()
