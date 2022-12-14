import os

EXTRA_ENV_COINFIG = 'ENV_CONFIG'  # 额外配置对应的环境变量名
BASE_URL_PRIFIX = '/ps'  # 基础URL的前缀
PUBLIC_FOLDER = '/home/mary/wenshu/public'
C_FOLDER = '/home/mary/wenshu/celine'
# IP_PORT = '172.16.10.7:9871'
# http://120.77.238.45:6008/ws_static/mc_1ws_add_qiao_8.docx
IP_PORT = os.environ.get("IP_PORT")
# IP_PORT_Test = "http://172.16.10.7:8000"

file_path = "http://172.16.10.8:8001/ai/batch_generate"
# text_path = '/home/lx/workshop/PS_Plag/static'
detail_path = f"{IP_PORT}/home/burshy/workshop/ps_plag/plag_detail/"

text_path = os.environ.get("TEXT_PATH")
text_path += '/static'
# text_path = '/home/lx/workshop/ps-plag-dev/ps_plage/static'
# text_path = os.path.join(os.getcwd(), 'static')
# print(text_path)

# "/home/lx/workshop/ps-plag-dev/ps_plage"

score_addr = os.environ.get("SCORE_ADDR")
