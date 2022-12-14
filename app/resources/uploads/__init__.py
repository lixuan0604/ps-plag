from flask import Blueprint
from flask_restful import Api

from common.utils.constants import BASE_URL_PRIFIX
from .upload import UploadResource, GetOrderFolderResource, DownLoadPublicFile, GenerateDownloadLink, Plag, BuildInvert, UnPlag, RunPlag


# 1.创建蓝图对象
uploads_bp = Blueprint('uploads', __name__,url_prefix=BASE_URL_PRIFIX)

# 2.创建Api对象
uploads_api = Api(uploads_bp)

# 3.添加类视图
uploads_api.add_resource(UploadResource, '/upload')
uploads_api.add_resource(GetOrderFolderResource, '/get_order_folder')
uploads_api.add_resource(DownLoadPublicFile, '/download_file')
uploads_api.add_resource(GenerateDownloadLink, '/generate_link')
uploads_api.add_resource(Plag, '/plag')
uploads_api.add_resource(BuildInvert, '/build_invert')
uploads_api.add_resource(UnPlag, '/un_plag')
uploads_api.add_resource(RunPlag, '/run_plag')