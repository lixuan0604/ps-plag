import os.path
from flask import jsonify, g, send_file, make_response
from flask_restful import Resource, request
from sqlalchemy.orm import load_only
from app import db
from common.models.user import User, Texts
from datetime import datetime
import requests, json
from common.utils.constants import file_path, text_path

from celery_tasks.text.tasks import sent_text


#
# # 允许的扩展名
# ALLOWED_EXTENSIONS = {'docx'}
# # 检查后缀名是否为允许的文件
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UploadResource(Resource):

    def post(self):
        # userid = request.form['userid']
        try:
            username = request.form['username']
            files = request.files.getlist('file')
            filenames = ''
            for name in files:
                file_name = name.filename.rsplit('.', 1)[0].lower()
                filenames += file_name + ','
            userinfo = User.query.filter_by(username=username).first()
            if userinfo:
                text = Texts(user_id=userinfo.id, filename=filenames, username=username, create_time=datetime.now(),
                             status=2)
                db.session.add(text)
                db.session.commit()
                path = []
                for file in files:
                    path.append(os.path.join(text_path, file.filename))
                    name = os.path.join('static', file.filename)
                    file.save(name)

                data = {"id": text.id, "path": path}
                sent_text.delay(url=file_path,data=data)
                # res = requests.post(file_path, json=data)
                print(path)
                return {'code': 200, 'message': '文件上传成功！!'}
            else:
                return {'code': 400, 'error': '用户已失效或不存在！!'}

        except Exception as e:
            return {'code': 400, 'error': str(e)}

    def get(self):
        '''获取text 信息'''
        pagenum = int(request.args.get('pagenum'))
        pagesize = int(request.args.get('pagesize'))
        result = []
        paginate = Texts.query.order_by(Texts.id.desc()).paginate(page=pagenum, per_page=pagesize,
                                                                  error_out=False)
        pag = paginate.items
        for item in pag:
            all_info = {}
            all_info["id"] = item.id
            all_info["username"] = item.username
            all_info["filename"] = item.filename
            all_info["file_path"] = item.file_path
            all_info["status"] = item.status
            all_info["create_time"] = item.create_time
            result.append(all_info)
        page_total = paginate.total
        return jsonify({'result': result, 'total': page_total})


class DownloadResource(Resource):
    # 下载文件
    def post(self):

        filepath = request.json['filepath']
        try:
            return make_response(send_file(filepath, as_attachment=True))
        except:
            return json.dumps({"code": 400, "msg": "plag job no finish, please wait a moment."})
