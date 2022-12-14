import json

import requests
from flask_restful import Resource, request
from sqlalchemy.orm import load_only
from app import db

from common.models.user import IndiaOrder

from flask import jsonify, g, send_file, make_response
from datetime import datetime

from common.utils.constants import score_addr


class orderInfoResource(Resource):

    def get(self):
        '''获取订单信息列表'''
        query = request.args.get('query')
        pagenum = int(request.args.get('pagenum'))
        pagesize = int(request.args.get('pagesize'))
        result = []
        page_total = None
        if query:
            query_result = IndiaOrder.query.filter(IndiaOrder.username.like("%" + query + "%")).all()
            if query_result:
                for que in query_result:
                    query_info = {}
                    query_info["id"] = que.id
                    query_info["username"] = que.username
                    query_info["agent"] = que.agent
                    query_info["order_id"] = que.order_id
                    query_info["file_path"] = 'public' + que.file_path.split('public')[-1]
                    query_info["score"] = que.score
                    query_info["status"] = que.status
                    query_info["workload"] = que.workload
                    query_info["create_time"] = que.create_time
                    query_info["workload_time"] = que.workload_time
                    det = que.detail_path
                    query_info["detail_path"] = det.rsplit('/')[-1] if que.detail_path else det
                    result.append(query_info)
            page_total = len(result)
        else:
            paginate = IndiaOrder.query.order_by(IndiaOrder.id.desc()).paginate(page=pagenum, per_page=pagesize,
                                                                                error_out=False)
            pag = paginate.items
            for item in pag:
                all_info = {}
                all_info["id"] = item.id
                all_info["username"] = item.username
                all_info["agent"] = item.agent
                all_info["order_id"] = item.order_id
                all_info["file_path"] = 'public' + item.file_path.split('public')[-1]
                all_info["score"] = item.score
                all_info["status"] = item.status
                all_info["workload"] = item.workload
                all_info["create_time"] = item.create_time
                all_info["workload_time"] = item.workload_time
                det = item.detail_path
                all_info["detail_path"] = det.rsplit('/')[-1] if item.detail_path else det
                result.append(all_info)
            page_total = paginate.total
        return jsonify({'result': result, 'total': page_total})

    def put(self):
        '''更改用户状态'''
        id = int(request.args.get('id'))
        score = request.args.get('workload')
        order = IndiaOrder.query.filter(IndiaOrder.id == id).first()
        if order:
            try:
                order.workload = score
                order.workload_time = datetime.now()
                db.session.commit()
                return jsonify({'code': 0, 'success': 'Modify Workload successfully!'})
            except Exception as e:
                return jsonify({'code': 1, 'error': 'Failed to modify the Workload!'})
        else:
            return jsonify({'code': 1, 'error': 'The current user to modify the Workload does not exist!'})


class ScoreRource(Resource):
    '''获取每月的总分数'''

    def get(self):
        starttime = request.args.get('starttime')
        starttime_s = starttime + " 00:00:00"
        endtime = request.args.get('endtime')
        endtime_e = endtime + " 23:59:59"
        query = request.args.get('query')
        query_q = query.strip()
        query_result = IndiaOrder.query.filter(IndiaOrder.username.like("%" + query_q + "%")).all()
        if query_result is None:
            return jsonify({'code': 400, 'message': 'The queried user does not exist, please check and re-enter!'})

        pagenum = int(request.args.get('pagenum'))
        pagesize = int(request.args.get('pagesize'))
        result = []
        if query_q:
            paginate = IndiaOrder.query.filter(IndiaOrder.workload_time.between(starttime_s, endtime_e),
                                               IndiaOrder.username.like("%" + query_q + "%")).paginate(page=pagenum,
                                                                                                       per_page=pagesize,
                                                                                                       error_out=False)
        else:
            paginate = IndiaOrder.query.filter(IndiaOrder.workload_time.between(starttime_s, endtime_e)).paginate(
                page=pagenum, per_page=pagesize,
                error_out=False)
        info = paginate.items
        for i in info:
            query_info = {}
            query_info['username'] = i.username
            query_info['score'] = 0 if i.workload == '' else int(i.workload)
            result.append(query_info)
        ret = {}
        for s in result:
            ret[s['username']] = ret.get(s['username'], 0) + s['score']
        score = []
        for key, value in ret.items():
            item = {}
            item['username'] = key
            item['score'] = value
            score.append(item)
        page_total = len(score)
        return jsonify({'result': score, 'total': page_total})


class DownloadResource(Resource):
    # 下载文件
    def post(self):

        filepath = 'http://' + score_addr + '/plag_detail/' + request.json['filepath']
        print(filepath)
        try:
            return make_response(send_file(filepath, as_attachment=True))
        except:
            return json.dumps({"code": 400, "msg": "plag job no finish, please wait a moment."})


class ShowDetail(Resource):
    def post(self):
        file_id = int(request.form.get('id'))
        info = IndiaOrder.query.filter_by(id=file_id).first()
        result = []
        if info.detail_path:
            filesplit = info.detail_path.rsplit('/')
            if filesplit:
                url = 'http://' + score_addr + '/plag_detail/'+filesplit[-1]
                data = requests.get(url)
                result = (json.loads(data.text))
                print(result)
                # for i in data.text:
                #     print(i.sent)
                return jsonify({"code": 200,'result': result})
            else:
                return json.dumps({"code": 400, "msg": "File path does not exist"})


        else:
            return json.dumps({"code": 400, "msg": "error"})


    def put(self):
        '''修改订单状态'''
        id = int(request.args.get('id'))
        status = request.args.get('status')
        order = IndiaOrder.query.filter(IndiaOrder.id == id).first()
        if order:
            try:
                order.status = status
                db.session.commit()
                return jsonify({'code': 0, 'success': 'Modify Workload successfully!'})
            except Exception as e:
                return jsonify({'code': 1, 'error': 'Failed to modify the Workload!'})
        else:
            return jsonify({'code': 1, 'error': 'The current user to modify the Workload does not exist!'})