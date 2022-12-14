from flask import Blueprint
from flask_restful import Api

from common.utils.constants import BASE_URL_PRIFIX
from .user import LoginResource,UserResource

# 1.创建蓝图对象
user_bp = Blueprint('user', __name__,url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
user_api = Api(user_bp)

# 3.添加类视图
user_api.add_resource(LoginResource, '/login')
user_api.add_resource(UserResource, '/user')
