
import json
import pickle
import os
import os.path as osp
import shutil

import pdb

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
def move(souce,target):
    shutil.move(souce, target)

def mkdir_ifmiss(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_folder_list(checked_directory, log_fn):
    checked_list = os.listdir(checked_directory)
    with open(log_fn, "w") as f:
        for item in checked_list:
            f.write(item + "\n")


def strcal(shotid, num):
    return str(int(shotid) + num).zfill(4)


def read_json(json_fn):
    with open(json_fn, "r",encoding='utf-8') as f:
        json_dict = json.load(f)
    return json_dict


def write_json(json_fn, json_dict):
    if not os.path.exists(json_fn):
        write_list = [json_dict]
    else:
        write_list = read_json(json_fn)
        write_list.append(json_dict)
    with open(json_fn, "w",encoding='utf-8') as f:
        json.dump(write_list, f, ensure_ascii=False,indent=4)


def read_pkl(pkl_fn):
    with open(pkl_fn, "rb") as f:
        pkl_contents = pickle.load(f)
    return pkl_contents


def write_pkl(pkl_fn, pkl):
    with open(pkl_fn, "wb") as f:
        pickle.dump(pkl, f)


def read_txt_list(txt_fn):
    with open(txt_fn, "r") as f:
        txt_list = f.read().splitlines()
    return txt_list


def write_txt_list(txt_fn, txt_list):
    with open(txt_fn, "w") as f:
        for item in txt_list:
            f.write("{}\n".format(item))
