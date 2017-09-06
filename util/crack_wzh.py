""" This module for crack detection of silicon wafer samples, further will exist other modules for other types
    defects detection such as water droplets/ dirty
    :method slice_process_inner: no borderline samples detection using adaptive threshold +
                                 dfs search (connectivity area)
    :method slice_process_corner: for border and corner crack detection using close operation
                                    and adaptive threshold + dfs search (connectivity area)
"""
import logging
import cv2
import numpy as np
import util.cv_wzh as cv3


def slice_process_inner(input_slice, defect_num_threshold=30, show_flag=False, debug_flag=False):
    """Inner slice defect detection via adaptive threshold and dfs search method

    :param input_slice: array-like, shape = [image,[coord_x,coord_y]]
            input image and its center coordinate of the raw input
    :param defect_num_threshold:{int }
            the preset threshold of min-area of single defect area
    :param show_flag: (default: False)
            control flag of show image or not
    :param debug_flag: (default: False)
            control flag of some debug information
    :return:
            inner_defect_num: max area of the connectivity defect area in slice
            inner_detect_flag:
                True if max defect area of slice < defect_num_threshold
    """

    img = input_slice[0]

    cv3.show('inner_src', img, show_flag=show_flag)

    # this can be optimized by shift sum, a blur can replace by a gauss filter
    blur = img
    for i in range(1, img.shape[0] - 1):
        blur[i] = np.mean(img[i - 1:i + 2, ], axis=0, keepdims=True)

    # adaptive threshold by 4sigma, because distribution of raw image is a gauss
    # and defect is another small gauss left of main peak, 4sigma is enough
    _mean, _std, _threshold_value = (np.mean(blur[blur > 130]), np.std(blur[blur > 130]),
                                     np.mean(blur[blur > 130]) - np.std(blur[blur > 130]) * 4)

    _, threshold_image = cv2.threshold(blur, _threshold_value, 255, cv2.THRESH_BINARY)

    inner_detect_flag, inner_defect_num = cv3.detect_inner_crack(threshold_image, defect_num_threshold)

    cv3.show('threshold_bef', threshold_image, show_flag=(show_flag and debug_flag))
    if inner_detect_flag:
        logging.debug('slice_process_inner: {0:>6,.3f} {1:>6,.3f} {2:>6,.3f}'.format(_mean, _std, _threshold_value))
        logging.debug(
            'slice_process_inner: {0:>6,.3f} {1:>6,.3f} {2:>6,.3f} {3}'.format(np.mean(threshold_image),
                                                                               np.max(threshold_image),
                                                                               inner_defect_num,
                                                                               inner_detect_flag))

    return inner_detect_flag, inner_defect_num


def slice_process_corner(input_slice, defect_num_threshold=50, show_flag=False, debug_flag=False):
    """Corner(border) slice defect detection via closed(image) operation and dfs search method

    :param input_slice: array-like, shape = [image,[coord_x,coord_y]]
            input image and its center coordinate of the raw input
    :param defect_num_threshold:{int }
            the preset threshold of min-area of single defect area
    :param show_flag: (default: False)
            control flag of show image or not
    :param debug_flag: (default: False)
            control flag of some debug information
    :return:
            corner_defect_num: max area of the connectivity defect area in slice
            corner_detect_flag:
                True if max defect area of slice < defect_num_threshold
    """
    img = input_slice[0]
    cv3.show('border_src', img, show_flag=show_flag)

    # adaptive threshold by 4sigma, because distribution of raw image is a gauss
    # and defect is another small gauss left of main peak, 4sigma is enough
    # mean, std = (np.mean(img[img > 130]), np.std(img[img > 130]))
    threshold_value = np.mean(img[img > 130]) - np.std(img[img > 130]) * 4

    _ret, threshold_image = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)

    cv3.show('border_threshold', threshold_image, show_flag=show_flag and debug_flag)

    # dilate = cv2.dilate(threshold_image, np.ones((5, 5), np.uint8), 1)
    close = cv2.erode(cv2.dilate(threshold_image, np.ones((5, 5), np.uint8), 1), np.ones((5, 5), np.uint8), 1)
    diff = close - threshold_image
    inv_diff = diff.copy()  # inverse the image to fit the designed dfs
    inv_diff[diff == 0] = 255
    inv_diff[diff == 255] = 0

    cv3.show('close', inv_diff, show_flag=show_flag and debug_flag)

    corner_detect_flag, corner_defect_num = cv3.detect_inner_crack(inv_diff, defect_num_threshold)

    if corner_detect_flag:
        logging.debug(
            '({0:<4d}, {1:<4d}) Defect Num: {2:<3d}, {3:<3d}'.format(input_slice[1][0], input_slice[1][1],
                                                                     corner_defect_num, corner_detect_flag))

    return corner_detect_flag, corner_defect_num
