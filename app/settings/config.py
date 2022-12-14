
class DefaultConfig:
    """默认配置"""
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://product:pl,okm098@172.16.10.7/ps_flag_pro'  # 连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据变化
    SQLALCHEMY_ECHO = False  # 是否打印底层执行的SQL

    SECRET_KEY = 'kdjklfjkd87384hjdhjh'

    # # redis配置
    # REDIS_HOST = '192.168.105.140'  # ip
    # REDIS_PORT = 6381  # 端口




config_dict = {
    'dev': DefaultConfig
}