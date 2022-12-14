from os.path import *
import sys

from flask_cors import CORS
from flask import Flask

# 将common路径加入模块查询路径
BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, BASE_DIR + '/common')

from app.settings.config import config_dict
from common.utils.constants import EXTRA_ENV_COINFIG

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# sqlalchemy组件对象
db = SQLAlchemy()


def create_flask_app(type):
    """创建flask应用"""

    # 创建flask应用
    app = Flask(__name__)
    # 根据类型加载配置子类
    config_class = config_dict[type]
    # 先加载默认配置
    app.config.from_object(config_class)
    # 再加载额外配置
    app.config.from_envvar(EXTRA_ENV_COINFIG, silent=True)

    # 返回应用
    return app


def register_extensions(app):
    """组件初始化"""

    # SQLAlchemy组件初始化
    from app import db
    db.init_app(app)
    # 数据迁移组件初始化
    Migrate(app, db)
    # 导入模型类
    from models import user
    # 跨域组件初始化
    CORS(app, supports_credentials=True)  # 设置supports_credentials=True, 则允许跨域传输cookie


def register_bp(app: Flask):
    """注册蓝图"""
    from app.resources.user import user_bp  # 进行局部导入, 避免组件没有初始化完成
    app.register_blueprint(user_bp)
    from app.resources.uploads import uploads_bp  # 进行局部导入, 避免组件没有初始化完成
    app.register_blueprint(uploads_bp)
    from app.resources.orderInfos import orderinfo_bp  # 进行局部导入, 避免组件没有初始化完成
    app.register_blueprint(orderinfo_bp)
    from app.resources.texts import texts_bp  # 进行局部导入, 避免组件没有初始化完成
    app.register_blueprint(texts_bp)


def create_app(type):
    """创建应用 和 组件初始化"""

    # 创建flask应用
    app = create_flask_app(type)
    # 组件初始化
    register_extensions(app)
    # 注册蓝图
    register_bp(app)

    return app
