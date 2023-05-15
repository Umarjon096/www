# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import json

import grp
import os
import paramiko
import pwd
import requests
#from urlparse import urlparse
from urllib.parse import urlparse
from django_starko.settings import MEDIA_ROOT, MC_PATCH_FOLDER, EMC_SSH_ADDRESS, EMC_SSH_PORT, EMC_BACKDOOR_USER, \
    EMC_BACKDOOR_PASSWORD, \
    EMC_HOST_URL, UUID
from django.contrib.auth.models import User
from mc.models import File, Item, Monitor, Playlist, Setting, SyncStatuses, SyncStateArchive, LastSyncState, Blackout, \
    Host, PendingChanges, SavedUrl
from mc.utils import django_main, create_conf_backup, delete_file, delete_unused_files
from mc.utils.commands import get_uuid, get_version, get_conf_obj
from mc.utils.host_interaction import patch_peasants, apply_all_hosts, all_hosts_lock, all_hosts_unlock, \
    all_hosts_reboot, apply_new_bl
from mc.utils.diag import get_diag_obj, ping

try:
    EMC_HOST_URL = Setting.objects.get(code='global_url').value
except Setting.DoesNotExist:
    pass


def get_free_space():
    statvfs = os.statvfs('/var/www')
    return float(statvfs.f_frsize * statvfs.f_bavail)

def download_file(url, name=None, add_path=''):
    head = requests.head(url)
    total_size = float(head.headers['content-length'])
    print(total_size)
    free_space = get_free_space()
    print(free_space)
    print('SPACE')
    if free_space < (total_size - 10000.0):
        raise Exception('NO SPACE FOR DOWNLOAD MEDIA!')
    cur_size = 0
    filename = url.split('/')[-1] if not name else name
    local_filename = os.path.join(MEDIA_ROOT, add_path, filename)
    # NOTE the stream=True parameter
    try:
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
                    cur_size += 1024
                    print('{0}% '.format(round((cur_size/total_size)*100)))
    except Exception as e:
        delete_file(local_filename)
        raise e

    uid = pwd.getpwnam("www-data").pw_uid
    gid = grp.getgrnam("www-data").gr_gid
    os.chown(local_filename, uid, gid)
    return local_filename

def send_patch_request():

    lock_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, '.lock')
    locked = os.path.isfile(lock_path)
    if locked:
        locked_time = datetime.fromtimestamp(os.path.getmtime(lock_path))
        time_spent = datetime.now()-locked_time
        if time_spent.total_seconds() > 60*60*24:
            locked = False
        else:
            return

    if not global_reachable(EMC_HOST_URL):
        return

    master_uuid = get_uuid()
    current_version = get_version()

    req = {
        'cur_version': current_version,
        'uuid': master_uuid
        }

    try:
        response = requests.post('{0}/patch_me/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
    except:
        log_sync(SyncStatuses.ERROR, u'Сервер недоступен')
        raise
    resp_obj = json.loads(response.text)
    patch_status = resp_obj['status']
    #если патча для нас нет, выходим
    if patch_status != 'patch':
        return 'no patches'

    patch_url = '{0}{1}'.format(EMC_HOST_URL, resp_obj['patch_path'])
    file_local = download_file(patch_url, resp_obj['patch_name'], add_path=MC_PATCH_FOLDER)
    patch_peasants(resp_obj['patch_name']) #если до кого-то из рабов не дойдет патч, то тут мы упадем и не будем патчить никого
    if not locked:
        open(lock_path, 'a').close()
    return 'got patch!'

def global_reachable(global_url):
    emc_domain = urlparse(global_url).netloc.split(':')[0]
    return ping(emc_domain, timeout=3)


def process_new_radios(new_radios):
    try:
        SavedUrl.objects.filter(built_in=True).delete()
        for radio in new_radios:
            SavedUrl.objects.create(name=radio['name'], url=radio['url'])
    except Exception as e:
        print(u'Error when saving radios {0}'.format(e.message))


def process_patch(patch_info):
    lock_path = os.path.join(MEDIA_ROOT, MC_PATCH_FOLDER, '.lock')
    locked = os.path.isfile(lock_path)
    if locked:
        locked_time = datetime.fromtimestamp(os.path.getmtime(lock_path))
        time_spent = datetime.now() - locked_time
        if time_spent.total_seconds() > 60 * 60 * 24:
            locked = False
        else:
            return

    patch_status = patch_info['status']
    # если патча для нас нет, выходим
    if patch_status != 'patch':
        return 'no patches'

    patch_url = '{0}{1}'.format(EMC_HOST_URL, patch_info['patch_path'])
    file_local = download_file(patch_url, patch_info['patch_name'], add_path=MC_PATCH_FOLDER)
    patch_peasants(
        patch_info['patch_name'])  # если до кого-то из рабов не дойдет патч, то тут мы упадем и не будем патчить никого
    if not locked:
        open(lock_path, 'a').close()


def send_diag_request():

    if not global_reachable(EMC_HOST_URL):
        return

    req = {}
    full_diag = json.dumps(get_diag_obj())
    req['full_diag']=full_diag

    pc, _ = PendingChanges.objects.get_or_create(pk=1)
    if pc.blackouts:
        bls = Blackout.objects.all()
        bls_json = [bl.as_json() for bl in bls]
        req['blackouts'] = json.dumps(bls_json)
    if pc.users:
        users = User.objects.all()
        users_json = [user.username for user in users]
        req['users'] = json.dumps(users_json)
    if pc.config:
        req['full_conf'] = json.dumps(create_conf_backup())

    if pc.sync:
        full_conf, conf_for_sha = map(json.dumps, get_conf_obj())
        sha_conf = hashlib.sha224(conf_for_sha).hexdigest()
        reg_email = Setting.objects.get(code=u'reg_email').value
        req['sync']= json.dumps({
            'sha_conf': sha_conf,
            'reg_email': reg_email,
            'global_sync': False
        })

    current_version = get_version()
    req['cur_version'] = current_version

    req['radio_conf'] = SavedUrl.sync_manager.get_sha()

    try:
        response = requests.post('{0}/diag_me/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
    except:
        log_sync(SyncStatuses.ERROR, u'Сервер недоступен')
        raise
    resp_obj = json.loads(response.text)
    pc.config = False
    pc.blackouts = False
    pc.users = False
    pc.save()
    #посмотрим, не пора ли нам открыть врата Мории
    remote_port = resp_obj.get('tunnel_request')
    if remote_port:
        #если пора, открываем
        backwards_ssh_tunnel(remote_port)

    # прислали ли результаты синхронизации
    sync = resp_obj.get('sync')
    if sync:
        process_sync_reply(sync)
    pc.sync = False
    pc.save()

    #новые радиостанции
    new_radios = resp_obj.get('new_radios')
    if new_radios:
        process_new_radios(new_radios)
    #а не прислали ли нам смену пароля
    change_pass = resp_obj.get('change_password')
    if change_pass:
        try:
            username=change_pass.get('username')
            password=change_pass.get('password')
            u = User.objects.get(username=username)
            u.set_password(password)
            u.save()
        except Exception as e:
            pass

    #посмотрим, не пора ли нам залочится или разлочится
    lock_or_unlock = resp_obj.get('lock_request')
    if lock_or_unlock:
        if lock_or_unlock == 'lock':
            all_hosts_lock()
        elif lock_or_unlock == 'unlock':
            all_hosts_unlock()

    #может нам прислали новый блеклист
    new_bl = resp_obj.get('new_bl')
    if new_bl:
        apply_new_bl(new_bl)

    #может нам прислали новую рег-инфу?
    reg_info_update = resp_obj.get('reg_info_update')
    if reg_info_update:
        try:
            Setting.objects.update_or_create(code=u'ent_name', defaults={'value': reg_info_update['name']})
            Setting.objects.update_or_create(code=u'ent_address', defaults={'value': reg_info_update['address']})
        except Exception as e:
            print('reg info update fail')

    #а может нас просят перезагрузиться?
    reboot_maybe = resp_obj.get('reboot_request')
    if reboot_maybe:
        all_hosts_reboot()

    media_request = resp_obj.get('media_request')
    print(u'Media request: {0}'.format(media_request))
    if media_request:
        send_media_to_global()

    patch_request = resp_obj.get('patch_request')
    print(u'Patch request: {0}'.format(patch_request))
    if patch_request:
        process_patch(patch_request)

    return resp_obj


def media_config():
    out = []
    for host in Host.objects.all():
        host_out = dict()
        host_out['uuid'] = get_uuid(host.ip)
        host_out['monitors'] = []
        for mon in Monitor.objects.filter(host=host):
            mon_out = mon.as_json()
            mon_out['playlists'] = []
            for pl in Playlist.objects.filter(monitor=mon):
                pl_out = pl.as_json()
                pl_out['items'] = []
                for it in Item.objects.filter(playlist=pl):
                    it_out = it.as_json()
                    it_out['fpath'] = os.path.split(it.file.data.path)[1] if it.file else None
                    pl_out['items'].append(it_out)
                mon_out['playlists'].append(pl_out)
            host_out['monitors'].append(mon_out)
        out.append(host_out)
    return out


def send_media_to_global():
    master_uuid = get_uuid()
    emc_ssh_domain = urlparse(EMC_HOST_URL).netloc.split(':')[0]
    transport = paramiko.Transport((emc_ssh_domain, int(EMC_SSH_PORT)))
    transport.connect(username=EMC_BACKDOOR_USER, password=EMC_BACKDOOR_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    def rm(path):
        files = sftp.listdir(path)

        for f in files:
            filepath = os.path.join(path, f)
            try:
                sftp.remove(filepath)
            except IOError:
                rm(filepath)

        sftp.rmdir(path)

    try:
        rm('{0}'.format(master_uuid))
    except IOError:
        pass
    #sftp.rmdir('{0}'.format(master_uuid))
    sftp.mkdir('{0}'.format(master_uuid))
    sftp.chmod(master_uuid, 0o777)
    files_obj = []
    doubles_protector = {}
    for it in Item.objects.all():
        if it.file and it.file.name not in doubles_protector:
            #try:
                real_f_name = os.path.basename(it.file.data.path)
                safe_f_name = real_f_name.replace("'", """'"'"'""")
                remote_f_name = u'{0}/{1}'.format(master_uuid, safe_f_name)
                sftp.put(it.file.data.path, remote_f_name)
                sftp.chmod(remote_f_name, 0o777)
                files_obj.append(dict(name=it.file.name, type=it.type, fname=real_f_name))
                doubles_protector[it.file.name] = True
            #except:
                #pass

    media_obj = {'media_data': json.dumps(media_config()), 'file_data': json.dumps(files_obj), 'uuid': get_uuid()}

    try:
        response = requests.post('{0}/media_config/'.format(EMC_HOST_URL), data=media_obj, auth=('admin','admin'))
        PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=False))
    except:
        log_sync(SyncStatuses.ERROR, u'Сервер недоступен')
        raise
    resp_obj = json.loads(response.text)
    print(resp_obj)


def send_config_request():

    if not global_reachable(EMC_HOST_URL):
        return

    master_uuid = get_uuid()

    full_conf = json.dumps(create_conf_backup())
    req = {
        'full_conf': full_conf,
        'uuid': master_uuid
    }

    try:
        response = requests.post('{0}/conf_me/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
    except:
        log_sync(SyncStatuses.ERROR, u'Сервер недоступен')
        raise
    resp_obj = json.loads(response.text)

    return resp_obj

def get_file_n_thumb(url_file, file_name, url_thumb):
    filename_to_check = url_file.split('/')[-1]
    #local_filename = os.path.join(MEDIA_ROOT, filename_to_check)
    f_exists = File.objects.filter(data=filename_to_check)
    head = requests.head(url_file)
    total_size = float(head.headers['content-length'])
    filesize = os.path.getsize(f_exists[0].data.path) if f_exists else 0
    if not f_exists or total_size != filesize:
        file_local = download_file(url_file)

        newfile = File.objects.create()
        newfile.data=os.path.basename(file_local)
        newfile.name = file_name
        if url_thumb:
            thumb_local = download_file(url_thumb, add_path='thumbnails')
            newfile.thumbnail=os.path.join('thumbnails',os.path.basename(thumb_local))
        newfile.save()
        return newfile.id
    else:
        return f_exists[0].id


def process_sync_reply(resp_obj):
    master_uuid = get_uuid()
    sync_status = resp_obj['status']
    if sync_status == 'waiting_for_auth' or sync_status == 'synced':
        log_sync(SyncStatuses.NOTHING_TO_SYNC)
        return u'Обновлений нет'
    elif sync_status == 'not_auth' or sync_status == 'new_conf_request':

        full_conf, conf_for_sha = map(json.dumps, get_conf_obj())
        sha_conf = hashlib.sha224(conf_for_sha).hexdigest()

        sync_status_str = Setting.objects.get(code=u'global_sync').value
        reg_email = Setting.objects.get(code=u'reg_email').value
        auth_string = full_conf
        ent_data = Setting.objects.get_name_and_address()
        req = {
            'hosts': auth_string,
            'uuid': master_uuid,
            'sha_conf': sha_conf,
            'reg_email': reg_email,
            'reg_info': u'{0} {1}'.format(*ent_data),
            'reg_name': ent_data[0],
            'reg_address': ent_data[1]
        }
        auth_response = requests.post('{0}/register_me/'.format(EMC_HOST_URL), data=req, auth=('admin', 'admin'))
        auth_obj = json.loads(auth_response.text)
        auth_status = auth_obj['status']
        if auth_status == 'waiting_for_auth':
            log_sync(SyncStatuses.WAITING_FOR_AUTH, u'Запрос на авторизацию устройства отправлен')
            return u'Запрос на авторизацию устройства отправлен'
        log_sync(SyncStatuses.ERROR, u'Ошибка при отправке запроса на авторизацию')
        return u'Ошибка при отправке запроса на авторизацию'

    if not resp_obj['sha_data']:
        log_sync(SyncStatuses.ERROR, u'Невозможна синхронизация')
        return u'Невозможна синхронизация'

    # File.objects.all().delete()
    mons_to_sync = []
    for host in resp_obj['hosts']:
        mons = host['monitors']
        for mon in mons:
            mon_obj = Monitor.objects.get(name=mon['name'])
            mons_to_sync.append(mon_obj.id)

    new_file_ids = []
    for fname in resp_obj['files'].keys():
        file_url = '{0}{1}'.format(EMC_HOST_URL, resp_obj['files'][fname])
        thumb_url = '{0}{1}'.format(EMC_HOST_URL, resp_obj['thumbnails'][fname]) if resp_obj['thumbnails'][fname] else None
        new_file_id = get_file_n_thumb(file_url, fname, thumb_url)
        new_file_ids.append(new_file_id)

    for file in File.objects.filter(item__playlist__monitor__in=mons_to_sync).exclude(id__in=new_file_ids):
        file.thumbnail.delete()
        file.data.delete()
        file.delete()

    for host in resp_obj['hosts']:
        mons = host['monitors']
        for mon in mons:
            mon_obj = Monitor.objects.get(name=mon['name'])
            Playlist.objects.filter(monitor=mon_obj).delete()
            pls = mon['playlists']
            for pl in pls:
                pl_obj = Playlist(content_type='hybrid' if pl['content_type'] != 'audio' else pl['content_type'],
                                  interval=pl['interval'],
                                  monitor=mon_obj,
                                  sequence=pl['sequence'],
                                  time_begin=pl['time_begin']
                                  )
                pl_obj.save()
                items = pl['items']
                for item in items:
                    fname = item['name']
                    url = item.get('url')
                    if url is None:
                        file_obj = File.objects.get(name=fname, pk__in=new_file_ids)
                    else:
                        file_obj = None
                    item_obj = Item(type=item['type'],
                                    playlist=pl_obj,
                                    sequence=item['sequence'],
                                    file=file_obj,
                                    url=url
                                    )
                    item_obj.save()
    req = {
        'uuid': master_uuid,
        'sha_data': resp_obj['sha_data']
    }
    upl_response = requests.post('{0}/confirm_upload/'.format(EMC_HOST_URL), data=req, auth=('admin', 'admin'))
    upl_obj = json.loads(upl_response.text)
    upl_status = upl_obj['status']
    if upl_status == 'synced':
        try:
            apply_all_hosts()
            log_sync(SyncStatuses.SYNCED, u'Успешная синхронизация')
            PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=False))
            return u'Успешная синхронизация'
        except:
            log_sync(SyncStatuses.ERROR, u'Данные с глобала загружены, но не применены')
            return u'Данные с глобала загружены, но не применены'
    elif upl_status == 'data_has_changed':
        return send_setup_request()
    else:
        log_sync(SyncStatuses.ERROR, u'Проблемы с синхронизацией, попробуйте позже')
        return u'Проблемы с синхронизацией, попробуйте позже'


def send_setup_request():
    if not global_reachable(EMC_HOST_URL):
        return

    master_uuid = get_uuid()
    full_conf, conf_for_sha = map(json.dumps, get_conf_obj())
    sha_conf = hashlib.sha224(conf_for_sha).hexdigest()

    sync_status_str = Setting.objects.get(code=u'global_sync').value
    reg_email = Setting.objects.get(code=u'reg_email').value

    req = {
        'sha_conf': sha_conf,
        'uuid': master_uuid,
        'reg_email': reg_email,
        'global_sync': True if sync_status_str == u'synced' else False
        }

    try:
        response = requests.post('{0}/sync_me/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
    except:
        log_sync(SyncStatuses.ERROR, u'Сервер недоступен')
        raise
    resp_obj = json.loads(response.text)

    sync_status = resp_obj['status']
    if sync_status == 'waiting_for_auth' or sync_status == 'synced':
        log_sync(SyncStatuses.NOTHING_TO_SYNC)
        return u'Обновлений нет'
    elif sync_status == 'not_auth' or sync_status == 'new_conf_request':
        auth_string = full_conf
        ent_data = Setting.objects.get_name_and_address()
        req = {
            'hosts': auth_string,
            'uuid': master_uuid,
            'sha_conf': sha_conf,
            'reg_email': reg_email,
            'reg_info': u'{0} {1}'.format(*ent_data),
            'reg_name': ent_data[0],
            'reg_address': ent_data[1]
        }
        auth_response = requests.post('{0}/register_me/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
        auth_obj = json.loads(auth_response.text)
        auth_status = auth_obj['status']
        if auth_status == 'waiting_for_auth':
            log_sync(SyncStatuses.WAITING_FOR_AUTH, u'Запрос на авторизацию устройства отправлен')
            return u'Запрос на авторизацию устройства отправлен'
        log_sync(SyncStatuses.ERROR, u'Ошибка при отправке запроса на авторизацию')
        return u'Ошибка при отправке запроса на авторизацию'
    # elif sync_status == 'new_conf_request':
    #     log_sync(SyncStatuses.WAITING_FOR_AUTH, u'Конфигурация изменилась, и сейчас мы пойдем в рекурсию')
    #     send_setup_request()
    #     return u'Конфигурация изменилась, но мы рекурснули её'

    if not resp_obj['sha_data']:
        log_sync(SyncStatuses.ERROR, u'Невозможна синхронизация')
        return u'Невозможна синхронизация'

    #File.objects.all().delete()
    for file in File.objects.all():
        file.thumbnail.delete()
        file.data.delete()
        file.delete()

    for fname in resp_obj['files'].keys():
        file_url = '{0}{1}'.format(EMC_HOST_URL, resp_obj['files'][fname])
        thumb_url = '{0}{1}'.format(EMC_HOST_URL, resp_obj['thumbnails'][fname]) if resp_obj['thumbnails'][fname] else None
        try:
            get_file_n_thumb(file_url, fname, thumb_url)
        except Exception as e:
            delete_unused_files()
            raise e


    for host in resp_obj['hosts']:
        mons = host['monitors']
        for mon in mons:
            mon_obj = Monitor.objects.get(name=mon['name'])
            Playlist.objects.filter(monitor=mon_obj).delete()
            pls = mon['playlists']
            for pl in pls:
                pl_obj = Playlist(content_type=pl['content_type'],
                                  interval=pl['interval'],
                                  monitor=mon_obj,
                                  sequence=pl['sequence'],
                                  time_begin=pl['time_begin']
                                  )
                pl_obj.save()
                items = pl['items']
                for item in items:
                    fname = item['name']
                    url = item.get('url')
                    if url is None:
                        file_obj = File.objects.get(name=fname)
                    else:
                        file_obj = None
                    item_obj = Item(type=item['type'],
                                    playlist=pl_obj,
                                    sequence=item['sequence'],
                                    file=file_obj,
                                    url=url
                                    )
                    item_obj.save()
    req = {
        'uuid': master_uuid,
        'sha_data': resp_obj['sha_data']
    }
    upl_response = requests.post('{0}/confirm_upload/'.format(EMC_HOST_URL), data=req, auth=('admin','admin'))
    upl_obj = json.loads(upl_response.text)
    upl_status = upl_obj['status']
    if upl_status == 'synced':
        try:
            apply_all_hosts()
            log_sync(SyncStatuses.SYNCED, u'Успешная синхронизация')
            PendingChanges.objects.update_or_create(pk=1, defaults=dict(sync=False))
            return u'Успешная синхронизация'
        except:
            log_sync(SyncStatuses.ERROR, u'Данные с глобала загружены, но не применены')
            return u'Данные с глобала загружены, но не применены'
    elif upl_status == 'data_has_changed':
        return send_setup_request()
    else:
        log_sync(SyncStatuses.ERROR, u'Проблемы с синхронизацией, попробуйте позже')
        return u'Проблемы с синхронизацией, попробуйте позже'


def log_sync(status, note=None, schedule_time=None):
    SyncStateArchive(status=status, note=note, schedule_time=schedule_time).save()
    try:
        lss = LastSyncState.objects.latest('time')
        lss.status = status
        lss.note = note
        lss.schedule_time = schedule_time
        lss.time = datetime.now()
        lss.save()
    except LastSyncState.DoesNotExist:
        LastSyncState(status=status, note=note, schedule_time=schedule_time).save()


def backwards_ssh_tunnel(tunnel_port):
    django_main(EMC_SSH_ADDRESS, int(EMC_SSH_PORT), EMC_BACKDOOR_USER, EMC_BACKDOOR_PASSWORD, int(tunnel_port))
    print('hohoho')
