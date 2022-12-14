from app import db
from datetime import datetime


class User(db.Model):
    """
    用户基本信息
    """
    __tablename__ = 'user_basic'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户id')
    username = db.Column(db.String(255), unique=True, comment='用户名')
    password = db.Column(db.String(255), comment='用户密码')
    createtime = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    last_login = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后一次登陆时间')
    # last_login = db.Column(db.DateTime, default=datetime.now ,comment='最后一次登陆时间')
    status = db.Column(db.Boolean, default=True, comment='是否启用')

    def __str__(self):
        return '%s' % self.name

    def to_dict(self):
        """模型转字典, 用于序列化处理"""
        return {
            'id': self.id,
            'username': self.username,
            'createtime': self.createtime,
            'updatetime': self.updatetime,
            'last_login': self.last_login
        }


class IndiaOrder(db.Model):
    """
    india order basic info
    """
    __tablename__ = 'india_order_info'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    user_id = db.Column(db.Integer, comment='用户id')
    username = db.Column(db.String(255), comment='用户名')
    agent = db.Column(db.String(255), comment='中介名')
    order_id = db.Column(db.String(255), comment='订单号')
    file_path = db.Column(db.Text, comment='文件路径')
    score = db.Column(db.String(255), comment='查重分数')
    status = db.Column(db.String(255), default=0, comment='查重状态')
    num_queue = db.Column(db.String(255), comment='查重排队情况')
    workload = db.Column(db.String(255), comment='工作量', default=0)
    detail_path = db.Column(db.Text, comment='查重细节文件位置')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    workload_time = db.Column(db.DateTime, comment='工作量打分时间')
    update_time = db.Column(db.DateTime, default=datetime.now, comment='更新时间')


class DownloadPublicFileLink(db.Model):
    __tablename__ = 'public_download_link'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    order_id = db.Column(db.String(255), comment='订单号')
    file_path = db.Column(db.Text, comment='文件路径')
    download_link = db.Column(db.Text, comment='下载链接')
    download_time = db.Column(db.Integer, default=1, comment='下载次数')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')


class PublicFile(db.Model):
    __tablename__ = 'public_file'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    status = db.Column(db.String(255), comment='文件状态，是否可以打开')
    file_path = db.Column(db.Text, comment='文件路径')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')


class PublicSent(db.Model):
    __tablename__ = 'sentence info'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    sent = db.Column(db.Text, comment='句子')
    len_sent = db.Column(db.String(255), comment='句子长度')
    p_i = db.Column(db.String(255), comment='段落号_句子序号')
    file_path = db.Column(db.Text, comment='文件路径')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')


class InvertTable(db.Model):
    __tablename__ = 'invert table'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    word = db.Column(db.String(255), comment='单词')
    word_sent_list = db.Column(db.Text(4294967295), comment='包含单词的句子对应的id，组成的列表')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')


class Texts(db.Model):
    __tablename__ = 'texts'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')
    user_id = db.Column(db.Integer, comment='用户id')
    username = db.Column(db.String(255), comment='用户名')
    filename = db.Column(db.String(255), comment='文件名')
    file_path = db.Column(db.Text, comment='文件路径')
    status = db.Column(db.String(255), comment='状态')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
