import cv2
import numpy as np
import matplotlib.pyplot as plt

# reference coordinates are taken from realTraining2
import numpy.linalg


def getRoiByImage(img, H):
    # from top left

    # 1049x654
    scale_x = img.shape[1] / 1049
    scale_y = img.shape[0] / 654


    #p1 = np.array([20,20,1])

    #img = cv2.circle(img, p1[0:1], 5, (0,0,255), 3 )

    #r_p1 = np.matmul(H, p1)
    #plt.imshow(img)
    #plt.show()

    #return r_p1

    led1_top_left = np.rint(np.array([1 * scale_x, 69 * scale_y, 1])).astype(int)
    led1_bottom_right = np.rint(np.array([12 * scale_x, 105 * scale_y, 1])).astype(int)

    led2_top_left = np.rint(np.array([1 * scale_x, 115 * scale_y, 1])).astype(int)
    led2_bottom_right = np.rint(np.array([9 * scale_x, 147 * scale_y, 1])).astype(int)

    # led1_top_left = np.rint(H.matmul(np.array([1 * scale_x, 100 * scale_y, 1]))).astype(int)
    # led1_bottom_right = np.rint(H.matmul(np.array([35 * scale_x, 151 * scale_y, 1]))).astype(int)
    #
    # led2_top_left = np.rint(H.matmul(np.array([1 * scale_x, 151 * scale_y, 1]))).astype(int)
    # led2_bottom_right = np.rint(H.matmul(np.array([35 * scale_x, 202 * scale_y, 1]))).astype(int)
    #

    led1 = img[led1_top_left[1]:led1_bottom_right[1], led1_top_left[0]:led1_bottom_right[0]]
    led2 = img[led2_top_left[1]:led2_bottom_right[1], led2_top_left[0]:led2_bottom_right[0]]

    #led1 = cv2.cvtColor(led1, cv2.COLOR_BGR2GRAY)

    #_, thresh = cv2.threshold(led1, 250, 255, cv2.THRESH_BINARY)


    #cv2.imshow("thresh", thresh)

    #f, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    #ax1.imshow(led1)
    #ax2.imshow(led2)
    #plt.show()

    #cv2.imshow("Led1", led1)
    #cv2.imshow("Led2", led2)
    #cv2.waitKey(0)
    return led1, led2

def get_roi_by_dest_corners(img, H):
    measured_corners = np.array([[1, 69, 1], [12, 105, 1], [1, 115, 1], [9, 147, 1]])

    hinv = numpy.linalg.inv(H)

    for corner in measured_corners:
        corner[0] = corner[0]
        corner[1] = corner[1]

        t_corner = np.matmul(hinv, corner)
        corner[0] = t_corner[0]
        corner[1] = t_corner[1]

    transformed_corners = measured_corners.astype(int)


    transformed_corners = transformed_corners.astype(int)

    led1 = img[transformed_corners[0][1]:transformed_corners[1][1], transformed_corners[0][0]:transformed_corners[1][0]]
    led2 = img[transformed_corners[2][1]:transformed_corners[3][1], transformed_corners[2][0]:transformed_corners[3][0]]


    #cv2.imshow("Led1", led1)
    #cv2.imshow("Led2", led2)
    #cv2.waitKey(0)
    return led1, led2
