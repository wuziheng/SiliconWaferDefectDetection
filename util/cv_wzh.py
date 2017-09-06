""" This module wrap some cv2 function to fit our target """
from datetime import datetime
import logging
import cv2
import numpy as np
import matplotlib.pyplot as plt


def show(window_name, mat, show_flag):
    """ wrapper of cv2.imshow, control show by show_flag """
    if show_flag:
        cv2.imshow(winname=window_name, mat=mat)
        cv2.waitKey()
    else:
        pass


def safe_crop(crop_image, i, j, slice_size):
    """ safe crop of image, which will stop at the border and keep slice_size if i j is near the border by move i j """
    if (i in range(slice_size / 2, crop_image.shape[0] - slice_size / 2)
        and j in range(slice_size / 2, crop_image.shape[1] - slice_size / 2)):
        return [crop_image[i - slice_size / 2:i + slice_size / 2, j - slice_size / 2:j + slice_size / 2], (i, j)]
    if i < slice_size / 2:
        i = slice_size / 2 + 1
    if i > crop_image.shape[0] - slice_size / 2:
        i = crop_image.shape[0] - slice_size / 2 - 1
    if j < slice_size / 2:
        j = slice_size / 2 + 1
    if j > crop_image.shape[1] - slice_size / 2:
        j = crop_image.shape[1] - slice_size / 2 - 1
    return [safe_crop(crop_image, i, j, slice_size)[0], (i, j)]


def find_target_contour(src):
    """ This is a target_contour find function, for given src and a preset threshold,
        find the outer contour of this src image,method is to get the contour which area
        is bigger than half of the src

    :param: Input: the src image {np.array((width,height))}
    :return: contour list-like shape=[[x1,y1],[x2,y2]...] list for contour,
            which is designated by cv2.findContours method
    """

    start_time = datetime.now()

    # find contours interface by cv2
    contours, _ = cv2.findContours(src, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # find the target contour by area set
    target_contour = 0
    for _contour in contours:
        if cv2.contourArea(_contour) > 0.5 * src.shape[0] * src.shape[1]:
            target_contour = _contour

    end_time = datetime.now()
    logging.info('Spends {0:<8.3f} ms'.format(
        (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

    # if show:
    #     # picture for draw result
    #     total = np.ones((src.shape[0], src.shape[1]))
    #     cv2.drawContours(total, contours, -1, (0, 255, 255), 20)
    #     plt.imshow(total, 'gray')
    #     plt.show()

    return target_contour


def border_locate(_contour, shape=(4096, 4096), show_flag=0):
    """This is a function roughly detect the border and corner coords for the src image

    :param:  contour: {[[x1,y1],[x2,y2]...]} list for contour, which is designated by cv2.findContours method
    :param:  shape: img.shape (width,height)
             show: display flag ,show return detail if show == 1
    :return: border_coords: list 8 coords for 4lines
    """

    start_time = datetime.now()

    coordx = [i[0][0] for i in _contour]
    coordy = [i[0][1] for i in _contour]

    proposal = []
    # collect the contour points which owns a mutation in slope
    for i in range(8, len(coordx) - 8):
        if coordx[i + 8] - coordx[i] != 0 and coordx[i + 4] - coordx[i] != 0 \
                and coordx[i + 6] - coordx[i] != 0:
            k1 = abs(float(coordy[i + 4] - coordy[i]) / float(coordx[i + 4] - coordx[i]))
            k2 = abs(float(coordy[i + 6] - coordy[i]) / float(coordx[i + 6] - coordx[i]))
            k3 = abs(float(coordy[i + 8] - coordy[i]) / float(coordx[i + 8] - coordx[i]))
            if abs(k1 - 1) + abs(k2 - 1) + abs(k3 - 1) < 1:
                proposal.append([coordx[i], coordy[i]])

    # preset corner_length
    corner_length = 150
    corner_list = []

    left_up_list = [i for i in proposal if i[0] < shape[0] / 4 and i[1] < shape[1] / 4]
    # using the approximate corner center and a corner length threshold(150) exclude obvious wrong proposal
    left_up_center = np.mean(np.array(left_up_list), axis=0)
    left_up_list = [i for i in left_up_list if
                    i[0] in range(int(left_up_center[0] - corner_length), int(left_up_center[0] + corner_length)) \
                    and i[1] in range(int(left_up_center[1] - corner_length),
                                      int(left_up_center[1] + corner_length))]
    # find the corner point on the corner segment
    corner_list.append(min(left_up_list, key=lambda x: x[0]))
    corner_list.append(max(left_up_list, key=lambda x: x[0]))

    right_up_list = [i for i in proposal if i[0] > shape[0] * 3 / 4 and i[1] < shape[1] / 4]
    right_up_center = np.mean(np.array(right_up_list), axis=0)
    right_up_list = [i for i in right_up_list if i[0] in range(int(right_up_center[0] - corner_length),
                                                               int(right_up_center[0] + corner_length))
                     and i[1] in range(int(right_up_center[1] - corner_length),
                                       int(right_up_center[1] + corner_length))]
    corner_list.append(min(right_up_list, key=lambda x: x[1]))
    corner_list.append(max(right_up_list, key=lambda x: x[0]))

    right_down_list = [i for i in proposal if i[0] > shape[0] * 3 / 4 and i[1] > shape[1] * 3 / 4]
    right_down_center = np.mean(np.array(right_down_list), axis=0)
    right_down_list = [i for i in right_down_list if i[0] in range(int(right_down_center[0] - corner_length),
                                                                   int(right_down_center[0] + corner_length))
                       and i[1] in range(int(right_down_center[1] - corner_length),
                                         int(right_down_center[1] + corner_length))]
    corner_list.append(max(right_down_list, key=lambda x: x[0]))
    corner_list.append(min(right_down_list, key=lambda x: x[0]))

    left_down_list = [i for i in proposal if i[0] < shape[0] / 4 and i[1] > shape[1] * 3 / 4]
    left_down_center = np.mean(np.array(left_down_list), axis=0)
    left_down_list = [i for i in left_down_list if i[0] in range(int(left_down_center[0] - corner_length),
                                                                 int(left_down_center[0] + corner_length))
                      and i[1] in range(int(left_down_center[1] - corner_length),
                                        int(left_down_center[1] + corner_length))]

    corner_list.append(max(left_down_list, key=lambda x: x[0]))
    corner_list.append(min(left_down_list, key=lambda x: x[0]))

    logging.debug('border_locate: 8corner coordinates: ' + str(corner_list))

    end_time = datetime.now()
    logging.info('Spends {0:<8.3f} ms'.format(
        (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

    if show_flag:
        # picture for draw result
        total = np.ones(shape)
        cv2.drawContours(total, contour, -1, (0, 255, 255), 20)
        for corner in corner_list:
            cv2.circle(total, (corner[0], corner[1]), 40, (0, 155, 155), 10)
        plt.imshow(total, 'gray')
        plt.show()

    return corner_list


def slice_by_border(src_path, _border, slice_size=200, method='border', _offset=10):
    """A function get the slice the 'input image' in to the (slice_size,slice_size) shape
    slices along to the input 'border', also can choose the slice method

    :param: src_path: the file_path for input image
    :param: _border: array-like,shape = [[x0,y0],[x1,y1]...] 8 border corners coordinates of ROI
    :param  slice_size: return image.shape width (default=200)
    :param  method: ['corner','border','inner','all'] control the output slices range
    :param _offset: the preset min interval between inner slices with border
    :returns corner_list: array-like, shape = [[slice,[coord]],...]
             border_list: array-like, shape = [[slice,[coord]],...]
             inner_list:  array-like, shape = [[slice,[coord]],...]

             return corner if method = 'corner'
             return border if method == 'border'
             return inner if method == 'inner'
             return corner,border,inner if method = 'all'
    """

    start_time = datetime.now()

    corner_slice = []
    border_slice = []
    inner_slice = []

    src = cv2.imread(src_path, 0)

    if method == 'corner' or method == 'all':
        for h in range(4):
            start = _border[h * 2]
            end = _border[h * 2 + 1]
            for (i, j) in zip(range(start[0], end[0], slice_size / 2 if end[0] > start[0] else -slice_size / 2),
                              range(start[1], end[1], slice_size / 2 if end[1] > start[1] else -slice_size / 2)):
                corner_slice.append(safe_crop(src, j, i, slice_size))

        if method == 'corner':
            logging.info('Method corner, return a list contains corner slices')
            end_time = datetime.now()
            logging.info('Spends {0:<8.3f} ms\n'.format(
                (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

            return corner_slice

    if method == 'border' or method == 'all':

        start, end = _border[1], _border[2]
        for i in range(start[0] + slice_size / 2, end[0] - slice_size / 2, slice_size):
            j = (end[1] - start[1]) * (i - start[0]) / (end[0] - start[0]) + start[1]
            # print start,end,i,j
            border_slice.append([np.rot90(safe_crop(src, j, i, slice_size)[0], 1), safe_crop(src, j, i, slice_size)[1]])

        start, end = _border[3], _border[4]
        for j in range(start[1] + slice_size / 2, end[1] - slice_size / 2, slice_size):
            i = (end[0] - start[0]) * (j - start[1]) / (end[1] - start[1]) + start[0]
            # print start,end,i,j
            border_slice.append([np.rot90(safe_crop(src, j, i, slice_size)[0], 2), safe_crop(src, j, i, slice_size)[1]])

        start, end = _border[5], _border[6]
        for i in range(start[0] - slice_size / 2, end[0] + slice_size / 2, -slice_size):
            j = (end[1] - start[1]) * (i - start[0]) / (end[0] - start[0]) + start[1]
            # print start,end,i,j
            border_slice.append([np.rot90(safe_crop(src, j, i, slice_size)[0], 3), safe_crop(src, j, i, slice_size)[1]])

        start, end = _border[7], _border[0]
        for j in range(start[1] - slice_size / 2, end[1] + slice_size / 2, -slice_size):
            i = (end[0] - start[0]) * (j - start[1]) / (end[1] - start[1]) + start[0]
            # print start,end,i,j
            border_slice.append(safe_crop(src, j, i, slice_size))

        # if 0:
        #     for _border in border_slice:
        #         cv2.imshow('border_slice', _border[0])
        #         cv2.waitKey()

        if method == 'border':
            logging.info('Method border, return a list contains border slices')
            end_time = datetime.now()
            logging.info('Spends {0:<8.3f} ms\n'.format(
                (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

            return border_slice

    if method == 'inner' or method == 'all':
        # inner part from top to bottom
        start1, end1 = _border[1], _border[2]
        start2, end2 = _border[6], _border[5]
        for i in range(start1[0] + slice_size / 2, end1[0] - slice_size / 2, slice_size):
            j_up = (end1[1] - start1[1]) * (i - start1[0]) / (end1[0] - start1[0]) + start1[1]
            j_down = (end2[1] - start2[1]) * (i - start2[0]) / (end2[0] - start2[0]) + start2[1]

            middle_line = (j_up + j_down) / 2
            for j in range(j_up + slice_size / 2 + _offset, middle_line + slice_size / 2, slice_size):
                inner_slice.append(safe_crop(src, j, i, slice_size))
            for j in range(j_down - slice_size / 2 - _offset, middle_line - slice_size / 2, -slice_size):
                # fix a small bug,corner always slice fault,we remove them
                if i == start1[0] + slice_size / 2 and j == j_down - slice_size / 2 - _offset:
                    pass
                elif i + slice_size > end1[0] - slice_size / 2 and j == j_down - slice_size / 2 - _offset:
                    pass
                else:
                    inner_slice.append(safe_crop(src, j, i, slice_size))

        # left part
        start1, end1 = _border[0], _border[7]
        for j in range(start1[1] + slice_size / 2, end1[1] - slice_size / 2, slice_size):
            i_left = (end1[0] - start1[0]) * (j - start1[1]) / (end1[1] - start1[1]) + start1[0]
            for i in range(i_left + slice_size / 2 + _offset, _border[1][0] + slice_size / 2, slice_size):
                inner_slice.append(safe_crop(src, j, i, slice_size))

        # right part
        start1, end1 = _border[3], _border[4]
        for j in range(start1[1] + slice_size / 2, end1[1] - slice_size / 2, slice_size):
            i_left = (end1[0] - start1[0]) * (j - start1[1]) / (end1[1] - start1[1]) + start1[0]
            for i in range(i_left - slice_size / 2 - _offset, _border[3][0] - slice_size / 2, -slice_size):
                inner_slice.append(safe_crop(src, j, i, slice_size))

        # if 0:
        #     for inner in inner_slice:
        #         cv2.imshow('inner', inner[0])
        #         print inner[1]
        #         cv2.waitKey()

        if method == 'inner':
            logging.info('Method border, return a list contains inner slices')
            end_time = datetime.now()
            logging.info('Spends {0:<8.3f} ms\n'.format(
                (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

            return border_slice

    if method == 'all':
        logging.debug('Method All,return 3 lists contains corner,border,inner')
        end_time = datetime.now()
        logging.info('Spends {0:<8.3f} ms\n'.format(
            (end_time - start_time).seconds * 1000 + (end_time - start_time).microseconds / 1000.0))

        return corner_slice, border_slice, inner_slice


def detect_inner_crack(arr, defect_num=50, debug_flag=0):
    """ This is core method of defect detection, use deep fisrt search to count the connected(not strictly) defect area
    :param arr: input array, shape = [width,height]
    :param defect_num: preset min area of confirmed defect area
    :param debug_flag: debug flag to control debug information print
    :return:
            flag: True if defect_max > defect_num
            defect_num: the max connected(not strictly) defect area during detection
    """
    if np.mean(arr) > 254.6:
        return False, 0

    search = 3  # search is the threshold of intermittent of 2 defects pixel

    label = np.zeros(arr.shape, dtype=int)
    label_idx = 1

    # background for inner after threshold is 255, defect is 0
    for i in range(0, arr.shape[0]):
        for j in range(0, arr.shape[1]):
            if arr[i, j] != 255 and label[i, j] == 0:
                label[i, j] = label_idx
                try:
                    dfs(i, j, arr, label, label_idx, search)
                    label_idx += 1
                except:
                    return True, 500  # dfs is to0 deep: raise for True and set defect_max=500

    defect_max = 0
    # collect the connection pixel area and count max
    for i in range(1, np.max(label + 1)):
        defect_max = max(defect_max, np.sum(label == i))
        if debug_flag:
            print "label = %d of %d" % (i, np.max(label)), "num: ", np.sum(label == i)

    if debug_flag:
        plt.imshow(label)
        plt.show()
    return defect_max > defect_num, defect_max


def dfs(i, j, arr, label, label_idx, search=3):
    """ An inplement of deep first search
    :param i: start point idx1
    :param j: start point idx2
    :param arr: input array, shape =[width,height]
    :param label: start point label if start point is defect
    :param label_idx: the last label_idx before
    :param search: threshold of intermittent of 2 defects pixel
    :return: None
    """
    for k in range(i - search, i + search + 1):
        for h in range(j - search, j + search + 1):
            if k == i and h == j or k < search or k > label.shape[0] - search or h < search or h > label.shape[1] \
                    - search:
                continue
            elif arr[k, h] != 255 and label[k, h] == 0:
                label[k, h] = label_idx
                dfs(k, h, arr, label, label_idx, search)


if __name__ == "__main__":
    #test_sample = '/home/wzh/Desktop/MCI0201/real crack/Semilab219151216C-218_0.bmp'
    test_sample = '../data/Semilab219151216C-218_0.bmp'

    img = cv2.imread(test_sample, 0)

    try:
        contour = find_target_contour(img)
    except:
        print "ERROR: find_target_contour error"
        exit(2)

    try:
        border = border_locate(contour)
    except:
        print "ERROR: border_locate error"
        exit(3)

    try:
        _slice = slice_by_border(test_sample, border, 200, "corner")
    except:
        print "ERROR: slice_by_border error"
        exit(4)

    print 'finished'
