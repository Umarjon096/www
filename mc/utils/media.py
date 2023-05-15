# -*- coding: utf-8 -*-
import os
import cv2
import uuid
import subprocess
from django_starko.settings import MEDIA_ROOT

try:
    CAP_PROP_FRAME_COUNT = cv2.CAP_PROP_FRAME_COUNT
    CAP_PROP_FPS = cv2.CAP_PROP_FPS
except AttributeError as e:
    CAP_PROP_FRAME_COUNT = cv2.cv.CV_CAP_PROP_FRAME_COUNT
    CAP_PROP_FPS = cv2.cv.CV_CAP_PROP_FPS

def resize_img(input_path, res_path, r_width, r_height):
    '''
    Ресайзим картинку под переданный размер
    :param input_path:
    :param res_path:
    :return:
    '''
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(img,(int(r_width), int(r_height)),interpolation=cv2.INTER_AREA)
    cv2.imwrite(res_path, resized)


def get_thumbnail(fpath):
    '''
    Функция ужимает рисунки до 500 пикселей по большей стороне и сохраняет в папочке thumbnails
    :param fpath: путь до файла-изображения, которое нужно ужать
    :return: путь до файла-скриншота
    '''
    dir, fname = os.path.split(fpath)
    dir = os.path.join(MEDIA_ROOT, 'thumbnails')
    new_fname = u'r_'+fname
    img = cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
    height = img.shape[0]
    width = img.shape[1]
    is_vertical = height > width
    if height > 500 or width > 500:
        if height > width:
            r = 500 / float(height)
        else:
            r = 500 / float(width)
        dim = (int(width * r), int(height * r))
        resized = cv2.resize(img, dim,interpolation=cv2.INTER_AREA)

        cv2.imwrite(os.path.join(dir, new_fname), resized)

    else:
        cv2.imwrite(os.path.join(dir, new_fname), img)
    return new_fname, is_vertical


def make_scrnsht_and_len(video_file):
    '''
    :param video_file: путь до видео-файла
    :return: название файла-скриншота. будет сохранен в тот же каталог, где и видео
    '''
    vc = cv2.VideoCapture(video_file)
    dir, vid_fname = os.path.split(video_file)
    vid_len = 0
    if vc.isOpened():
        len = vc.get(CAP_PROP_FRAME_COUNT)
        #отмотаем вперед
        frame_to_cut = int(len/3)
        bool_frame = vc.set(CAP_PROP_FRAME_COUNT, frame_to_cut)
        #в качестве имени файла будет уникальный id
        fname = os.path.join(dir, str(uuid.uuid4()) + '.jpg')
        #if bool_frame:
        rval, frame = vc.read()
        cv2.imwrite(fname, frame)

        fps = vc.get(CAP_PROP_FPS)
        vid_len = round(len / fps, 2)
    vc.release()
    return fname, vid_len

def get_bitrate(video_file):
    command = 'ffprobe -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 -v error -i "{0}"'.format(video_file)
    ffprobe_dur = subprocess.check_output(command, shell=True).decode("utf-8").replace('\n', '')
    try:
        return int(ffprobe_dur)
    except Exception as e:
        return 0