""" This is a module for data loading, to classify and sort source image with defection image by their filename
using glob and re and os to get the information
"""
from glob import glob
import os
import logging
import re

# OLD VERSION
# _SRC_PATH = '/home/wzh/Desktop/src'
# _DEFECT_CRACK_PATH = '/home/wzh/Desktop/defect/crack'
# _DEFECT_INCLUSION_PATH = '/home/wzh/Desktop/defect/inclusion'

# def load_data(src_path, defect_crack_path, defect_inclusion_path):
#     crack_dict = {}
#     inclusion_dict = {}
#     src_filelist = glob("%s/*.bmp" % src_path)
#     defect_crack_filelist = glob("%s/*.bmp" % defect_crack_path)
#     defect_inclusion_filelist = glob("%s/*.bmp" % defect_inclusion_path)
#
#     print "src num: ", len(src_filelist)
#     print "crack num: ", len(defect_crack_filelist)
#     print "inclusion num: ", len(defect_inclusion_filelist)
#
#     name_list = []
#     for src in src_filelist:
#         src_name = src.split('/')[-1].split('.')[0]
#         crack_dict[src] = []
#         inclusion_dict[src] = []
#         if len(src_name.split('_')) == 3:
#             real_name = '%s_%s' % (src_name.split('_')[0], src_name.split('_')[1])
#             name_list.append(real_name)
#         elif len(src_name.split('_')) == 4:
#             real_name = '%s_%s_%s' % (src_name.split('_')[0], src_name.split('_')[1], src_name.split('_')[2])
#             name_list.append(real_name)
#         else:
#             print 'read_src_error: name format is wrong  -- %s' % src_name
#
#         crack_candidates = glob('%s/%s_*' % (defect_crack_path, real_name))
#         inclusion_candidates = glob('%s/%s_*' % (defect_inclusion_path, real_name))
#
#         for crack in crack_candidates:
#             crack_dict[src].append([crack, 'crack'])
#
#         for inclusion in inclusion_candidates:
#             inclusion_dict[src].append([inclusion, 'inclusion'])
#
#             # print src
#             # print 'crack:',crack_candidates
#             # print 'inclusion',inclusion_candidates
#             # print
#     # debug
#     # print "total load data : %d"%len(name_list)
#     # print "return in format return_dict {src_path:[[defect_src_path,defect_category]]}"
#     return src_filelist, crack_dict, inclusion_dict


def load_data_onepath(_path):
    """ This is load data method by re & glob module for defect and src in the same dir
    :param _path: input file path
    :return:name_list: array-like shape = [name1,name2,...],
            crack_dict: dict-like, shape = {name1:list[name1_crack_path...],name2:list[name2_crack_path...],...},
            src_dict: dict-like  shape = {name1:name1_src_path,name2:name2_src_path,...}
    """

    if os.path.exists(_path):
        file_list = glob('%s/*.bmp' % _path)
    else:
        logging.error("IOError: {0:<30s} is not a valid path".format(_path))
        return

    # using array-list namelist to idx the crack_file dict, source_file dict
    crack_dict = {}
    src_dict = {}
    name_list = []
    for file_path in file_list:
        if re.search('defect', file_path, re.I) and re.search('bmp', file_path, re.I):
            name = file_path.split('/')[-1].split('_')[0]
            name_list.append(name)
            if name not in crack_dict:
                crack_dict[name] = [file_path]
            else:
                crack_dict[name].append(file_path)

    for name in name_list:
        for file_path in file_list:
            if re.search(name, file_path, re.I) and re.search('bmp', file_path, re.I) \
                    and file_path not in crack_dict[name]:
                src_dict[name] = file_path

    for name in name_list:
        logging.debug('{0:<30s} : {1:<30s}'.format(name, crack_dict[name]))
        logging.debug('{0:<30s} : {1:<30s}'.format(name, src_dict[name]))

    if not name_list:
        logging.error('NumError: {0:<30s} doesnt include any defect file'.format(_path))

    return name_list, crack_dict, src_dict


if __name__ == "__main__":
    testPath = '/home/wzh/Desktop/MCI0201/real crack'
    namelist, crack, src = load_data_onepath(testPath)
    for name1 in namelist:
        print name1
        print src[name1]
        print crack[name1]
        print '\n\n\n\n'





