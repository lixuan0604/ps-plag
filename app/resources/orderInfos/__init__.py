from flask import Blueprint
from flask_restful import Api

from common.utils.constants import BASE_URL_PRIFIX
from .orderinfo import orderInfoResource, ScoreRource, DownloadResource,ShowDetail

# 1.创建蓝图对象
orderinfo_bp = Blueprint('orderInfos', __name__, url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
orderinfo_api = Api(orderinfo_bp)

# 3.添加类视图
orderinfo_api.add_resource(orderInfoResource, '/orderinfo')
orderinfo_api.add_resource(ScoreRource, '/getscore')
orderinfo_api.add_resource(DownloadResource, '/download')
orderinfo_api.add_resource(ShowDetail, '/detail')
