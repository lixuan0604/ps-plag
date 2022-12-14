import hashlib
import time

from flask_restful import Resource, request
from flask import send_file
from common.models.user import IndiaOrder, DownloadPublicFileLink, PublicFile
from common.utils.constants import PUBLIC_FOLDER, C_FOLDER, IP_PORT
from app import db
from datetime import datetime
import json
import os
import shutil
import zipfile
from pathlib import Path

# from .utils import build_invert_table
from .utils import build_invert_table, plag_word, build_invert_table_, plag


class BuildInvert(Resource):
    def get(self):
        build_invert_table_()
        return 1


class Plag(Resource):
    def post(self):
        if request.form['passwd'] == 'start plag':
            while True:
                un_plag = IndiaOrder.query.filter_by(status=0)
                for info in un_plag:
                    id = info.id
                    fid = hashnow()
                    file = info.file_path
                    plag(id, fid, file)


class UnPlag(Resource):
    def post(self):
        un_plag = IndiaOrder.query.filter_by(status=0)

        result = []
        for item in un_plag:
            result.append({'id': item.id, 'file_path': item.file_path})

        return result


class RunPlag(Resource):
    def post(self):
        id = request.form['id']
        fid = request.form['fid']
        file = request.form['file']
        plag(id, fid, file)
        return {"status": 1}


class GetOrderFolderResource(Resource):
    def get(self):
        try:
            order_dict = get_order_folder(PUBLIC_FOLDER)
            return {'code': 200, 'result': order_dict}
        except Exception as e:
            return {'code': 400, 'msg': str(e)}


def get_order_folder(path):
    """
    path: public文件夹对应的位置
    return dict
    订单号对应的文件夹路径
    """
    # path目录下第一级为中介对于的目录，第二级为各中介对于的订单号文件夹
    order_folder_dict = {}
    for pwd_path, dirnames, files in os.walk(path):
        for dir in dirnames:
            for _, order_folders, ___ in os.walk(os.path.join(pwd_path, dir)):
                for order_folder in order_folders:
                    order_folder_dict[order_folder] = os.path.join(_, order_folder)
                break
        break
    # print(order_folder_dict)
    return order_folder_dict


class UploadResource(Resource):
    """上传文件"""

    def post(self):
        try:
            userid = request.form['userid']
            username = request.form['username']
            order_folder_path = request.form['order_folder']
            agent = order_folder_path.split('/')[-2]
            order_id = order_folder_path.split('/')[-1]
            files = request.files.getlist('file')
            india_os = os.path.join(order_folder_path, 'india_os')
            if not os.path.exists(india_os):
                os.makedirs(india_os)
            c_name_folder = os.path.join(C_FOLDER, str(username))
            if not os.path.exists(c_name_folder):
                os.makedirs(c_name_folder)
            for f in files:
                file_path = os.path.join(india_os, f.filename)
                f.save(os.path.join(india_os, f.filename))
                # f.save(os.path.join(c_name_folder, f.filename))
                shutil.copyfile(os.path.join(india_os, f.filename), os.path.join(c_name_folder, f.filename))
                order_info = IndiaOrder(user_id=userid, username=username, agent=agent, order_id=order_id,
                                        file_path=file_path)
                db.session.add(order_info)
                db.session.commit()
            return {'code': 200, 'msg': 'file uploaded successfully'}
        except Exception as e:
            return {'code': 400, 'error': str(e)}


def hashnow():
    key = hashlib.sha256(str(datetime.now()).encode('utf-8')).hexdigest()
    return key


class GenerateDownloadLink(Resource):
    def post(self):
        try:
            order_id = request.form['order_id']
            file_path = request.form['file_path']
            download_time = request.form['download_time']
            link = hashnow()
            download_ = DownloadPublicFileLink(order_id=order_id, file_path=file_path, download_link=link,
                                               download_time=download_time)
            db.session.add(download_)
            db.session.commit()
            d_link = f'http://{IP_PORT}/ps/download_file?fid={link}'
            return {'code': 200, 'link': d_link}
        except Exception as e:
            return {'code': 400, 'msg': str(e)}


class DownLoadPublicFile(Resource):
    def get(self):
        try:
            download = os.path.join(Path(__file__).resolve().parent.parent.parent.parent, 'download')
            # print(download)
            link = request.args.get('fid')
            # print(link)
            info = DownloadPublicFileLink.query.filter_by(download_link=link).first()
            file_path = info.file_path
            # print(file_path)
            order_id = info.order_id
            download_time = info.download_time
            id = info.id
            if download_time > 0:
                # if not os.path.exists(os.path.join(download, order_id + '.zip')):
                zipf = zipfile.ZipFile(os.path.join(download, order_id + '.zip'), 'w', zipfile.ZIP_DEFLATED)
                for root, dirs, files in os.walk(file_path):
                    f_path = root.replace(file_path, '')
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.join(f_path, file))
                zipf.close()
                download_time -= 1
                DownloadPublicFileLink.query.filter_by(id=id).update({'download_time': download_time})
                db.session.commit()
                return send_file(os.path.join(download, order_id + '.zip'), mimetype='zip', as_attachment=True)
            else:
                return {'code': 200, 'msg': 'Download link is dead'}
        except Exception as e:
            return {'code': 400, 'msg': str(e)}
