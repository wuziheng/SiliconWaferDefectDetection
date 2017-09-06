import re
import logging
import cv2
import util.cv_wzh as cv3
import util.data_wzh as data
from util.crack_wzh import slice_process_inner
from util.crack_wzh import slice_process_corner

# logging config
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)-16s[line:%(lineno)-4d] %(levelname)-8s %(funcName)-20s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='info.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(funcName)-20s : %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def image_process(src_path, _name):

    logging.info('{:<18s}'.format(_name))
    logging.info('DETECTION STARTS:\n')
    img_threshold_value = 60

    _ret, _threshold_image = cv2.threshold(cv2.imread(src_path, 0),
                                           img_threshold_value,
                                           255,
                                           cv2.THRESH_BINARY)

    _target_contour = cv3.find_target_contour(_threshold_image)

    _border = cv3.border_locate(_target_contour, _threshold_image.shape, 0)

    _corner_slices, _border_slices, _inner_slices = cv3.slice_by_border(src_path, _border, method='all')

    logging.info('{:<6s} search start'.format('border'))
    for b_slice in _border_slices:
        border_detect_flag, border_defect_num = slice_process_corner(b_slice, 30, show_flag=False)
        if border_detect_flag:
            message = '({0:4d}, {1:4d}) : defect Num / threshold : {2:3d} / {3:3d}'.format(b_slice[1][0], b_slice[1][1],
                                                                                           border_defect_num, 30)
            logging.warning(message)
            # slice_process_corner(b_slice, 30, show_flag=True)
    logging.info('{:<6s} search end\n'.format('border'))

    logging.info('{:<6s} search start'.format('inner'))
    for i_slice in _inner_slices:
        inner_detect_flag, inner_defect_num = slice_process_inner(i_slice, 30, 0)
        if inner_detect_flag:
            message = '({0:4d}, {1:4d}) : defect Num / threshold : {2:3d} / {3:3d}'.format(i_slice[1][0], i_slice[1][1],
                                                                                           inner_defect_num, 30)
            logging.warning(message)
            if inner_defect_num == 500:
                logging.error('inner detect dfs search fault !')
                # num ==500 means dfs fault which always mean pic is too many fault
            # slice_process_inner(i_slice, 30, 1)
    logging.info('{:<6s} search end\n'.format('inner'))

    logging.info('{:<6s} search start'.format('corner'))
    for c_slice in _corner_slices:
        corner_detect_flag, corner_defect_num = slice_process_corner(c_slice, 20)
        if corner_detect_flag:
            message = '({0:4d}, {1:4d}) : defect Num / threshold : {2:3d} / {3:3d}'.format(c_slice[1][0], c_slice[1][1],
                                                                                           corner_defect_num, 30)
            logging.warning(message)
            # slice_process_corner(c_slice, 20, show_flag=True)
    logging.info('{:<6s} search end\n'.format('corner'))
    # logging.info('DETECTION ENDS\n\n')


if __name__ == "__main__":

    newPath = 'data'
    test_name = 'Semilab261151217B-1457_0'

    # newPath = '/home/wzh/Desktop/MCI0201/real crack'
    # test_name = 'Semilab261151217B-1457_0'

    # newPath =  '/home/wzh/Desktop/MCI0201/remained/252151210C'
    # testname =  'Semilab252151210C-570_0'

    name_list, crack_dict, src_dict = data.load_data_onepath(newPath)

    # debug for a single picture
    if 1:
        for name in name_list:
            if re.search(name, test_name, re.I):
                test_name = name
        image_process(src_dict[test_name], test_name)

    # debug for a dir
    if 0:
        for name in name_list:
            print name
            try:
                image_process(src_dict[name])
            except:
                print name, 'algorithm wrong'
            print name, ' detect is end !'
            print '\n\n\n\n\n\n\n\n\n'

    # debug a single picture pipeline
    if 0:
        show = 1
        for name in name_list:
            if re.search(name, test_name, re.I):
                test_name = name

        ret, thre = cv2.threshold(cv2.imread(src_dict[test_name], 0), 60, 255, cv2.THRESH_BINARY)

        target_contour = cv3.find_target_contour(thre)

        border = cv3.border_locate(target_contour, thre.shape, 0)
        print border

        corner_slice, border_slice, inner_slice = cv3.slice_by_border(src_dict[test_name], border, method='all')

        if 1:
            for _slice in border_slice:
                flag, num = slice_process_corner(_slice, 20)
                if flag:
                    print _slice[1], 'Defect Num: %d' % num
                    flag, num = slice_process_corner(_slice, 20, show_flag=True)

            print 'border search end'

        if 0:
            for _slice in inner_slice:
                flag, num = slice_process_inner(_slice, 30)
                if flag:
                    print _slice[1], 'Defect Num: %d' % num
                    flag, num = slice_process_inner(_slice, 30, show_flag=True)

            print 'inner search end'

        if 0:
            for _slice in corner_slice:
                flag, num = slice_process_corner(_slice, 20)
                if flag:
                    print _slice[1], 'Defect Num: %d' % num
                    flag, num = slice_process_corner(_slice, 20, show_flag=True)

        print 'border search end'
