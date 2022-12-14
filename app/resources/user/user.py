from flask_restful import Resource,request
import datetime
import json
from flask import Response,session,jsonify,g
from common.models.user import User
from app import db
from datetime import datetime
from sqlalchemy.orm import load_only
class LoginResource(Resource):
    """用户登录"""
    def post(self):
        '''实现登录接口'''
        data = request.get_data()
        data = json.loads(data)
        username = data.get('username')
        passwd = data.get('password')
        # 校验参数是否完整
        if not all([username, passwd]):
            return {'code': 400, 'message': '请输入用户名和密码!'}
        userinfo = User.query.filter_by(username=username, status=1).first()
        if userinfo:
            if userinfo.password == passwd:
                # 设置session
                session["username"] = userinfo.username
                session["user_id"] = userinfo.id
                userinfo.last_login = datetime.now()
                db.session.add(userinfo)
                db.session.commit()
                userinfo_dict = {
                    "username":userinfo.username,
                    "id":userinfo.id
                }
                return {'code': 200,'result': userinfo_dict}
            else:
                return {'code': 400, 'message': '密码错误！!'}
        else:
            return {'code': 400, 'message': '用户已失效或不存在！!'}

    def get(self):
        '''获取用户列表'''
        query = request.args.get('query')
        pagenum = int(request.args.get('pagenum'))
        pagesize = int(request.args.get('pagesize'))
        result = []
        page_total = None
        if query:
            query_result = User.query.filter(User.username.like("%"+query+"%")).all()
            if query_result:
                for que in query_result:
                    query_info = {}
                    query_info["id"] = que.id
                    query_info["username"] = que.username
                    query_info["password"] = que.password
                    query_info["createtime"] = que.createtime
                    query_info["last_login"] = que.last_login
                    query_info["status"] = que.status
                    result.append(query_info)
                page_total = len(result)
        else:
            paginate = User.query.order_by(User.id.desc()).paginate(page=pagenum,per_page=pagesize,error_out=False)
            pag = paginate.items
            for item in pag:
                all_info = {}
                all_info["id"] = item.id
                all_info["username"]=item.username
                all_info["password"] = item.password
                all_info["createtime"] = item.createtime
                all_info["last_login"] = item.last_login
                all_info["status"] = item.status
                result.append(all_info)
            page_total = paginate.total
        return jsonify({'result': result,'total':page_total})

class UserResource(Resource):
    """用户操作"""
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        # 查询用户是否存在
        user = User.query.options(load_only(User.id)).filter(User.username==username).first()
        if user:
            return jsonify({'code': 1, 'message': 'User already exists, please re-enter!'})
        add_user = User(username=username,password=password,status=1,createtime=datetime.now())
        db.session.add(add_user)
        db.session.commit()
        return jsonify({'userid': add_user.id,'message':'Added successfully'})

    def put(self):
        '''更改用户状态'''
        username = request.args.get('username')
        status = request.args.get('status')
        user = User.query.options(load_only(User.id)).filter(User.username == username).first()
        if user:
            try:
                if status=='true':
                    user.status=True
                else:
                    user.status = False
                db.session.commit()
                return jsonify({'code': 0, 'success': 'Change user status successfully!'})
            except Exception as e:
                return jsonify({'code': 1, 'error': 'Failed to change user status!'})
        else:
            return jsonify({'code': 1, 'error': 'The current user to modify the status does not exist!'})

    def delete(self):
        username = request.json.get('username')
        user = User.query.filter(User.username == username).first()
        if user:
            # 删除数据
            db.session.delete(user)
            # 提交会话 增删改都要提交会话
            db.session.commit()
            return jsonify({'code': 0, 'success': 'Delete user successfully!'})
        else:
            return jsonify({'code': 1, 'error': 'This user does not exist!'})