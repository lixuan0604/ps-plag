

from flask import Blueprint
from flask_restful import Api

from common.utils.constants import BASE_URL_PRIFIX
from .text import UploadResource,DownloadResource

# 1.创建蓝图对象
texts_bp = Blueprint('texts', __name__,url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
texts_api = Api(texts_bp)

# 3.添加类视图
texts_api.add_resource(UploadResource, '/uploadfile')
# 下载文件
texts_api.add_resource(DownloadResource, '/download')

