# -*- coding: utf-8 -*-
import os
import mimetypes
from transliterate import translit
from django_starko.settings import MEDIA_ROOT, BITRATE_LIMIT

from mc.models import File

from .media import make_scrnsht_and_len, get_thumbnail, get_bitrate


def convert_chunks_to_mime(old_name, new_name):
    '''Пишем чанки в готовый файл и возвращаем его mime-тип'''
    old = os.path.join(MEDIA_ROOT, old_name)
    new = os.path.join(MEDIA_ROOT, new_name)
    # new = os.path.join(MEDIA_ROOT, new_name.decode())
    os.rename(old, new)
    return mimetypes.guess_type(new)[0]


def process_ready_file(file, file_uuid):
    '''Обрабатываем готовый файл и возвращаем словарь'''
    newfile_name = translit(file.name, 'ru', reversed=True)
    #print(newfile_name)
    #newfile_name = newfile_name.encode('ascii', 'backslashreplace')
    #print(newfile_name)
    mime_type = convert_chunks_to_mime(file_uuid, newfile_name)
    newfile, _created = File.objects.get_or_create(data=newfile_name)
    newfile.data.name = newfile_name
    newfile.name = os.path.basename(newfile_name)
    file_data = {}
    file_data['name'] = newfile.name
    file_data['url'] = newfile.data.url
    file_data['path'] = newfile.data.path
    file_data['type'] = mime_type.split('/')[0]
    if file_data['type'] in ('video', 'image'):
        if file_data['type'] == 'video':
            scrn_path, dur = make_scrnsht_and_len(file_data['path'])
            thumb_file, is_vertical = get_thumbnail(scrn_path)
            newfile.duration = dur
            newfile.bitrate = get_bitrate(file_data['path'])
        else:
            thumb_file, is_vertical = get_thumbnail(file_data['path'])
        newfile.thumbnail = os.path.join('thumbnails', thumb_file)
        newfile.is_vertical = is_vertical
        file_data['thumb_url'] = newfile.thumbnail.url
    else:
        file_data['thumb_url'] = None
    newfile.save()
    file_data['file_id'] = newfile.id
    file_data['bitrate'] = newfile.bitrate
    file_data['bitrate_violation'] = newfile.bitrate > BITRATE_LIMIT
    return file_data
