from SpiderKeeper.app import login_manager
from .model import Users
from flask import Blueprint
api_user_bp = Blueprint('user', __name__)
token = ''


@login_manager.user_loader
def load_user(id):
    '''
    功能：实现一个load_user()回调方法, 这个回调用于从会话中存储的用户id重新加载用户对象
    :param id: 用户id
    :return:  id存在则返回对应的用户对象, 不存在则返回none
    '''
    return Users.query.filter_by(id=id).first()



