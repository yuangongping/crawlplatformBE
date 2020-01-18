from flask import Blueprint, request
from SpiderKeeper.app import app
from SpiderKeeper.app.visual.model import DataCounts
from SpiderKeeper.app.schedulers.model import JobExecution
from SpiderKeeper.app.projects.model import Project
from sqlalchemy import func
from flask import jsonify
from flask import render_template
import datetime, json
import decimal


api_visual_bp = Blueprint('visual', __name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


@app.route("/add_record", methods=['post'])
def get_data_count():
    if DataCounts.insert_record(request.form):
        return jsonify({'code': 200, 'data': 'success', "msg": "添加成功"})
    else:
        return jsonify({"code": 500, "status": "error", "msg": "添加错误"})


@app.route("/collect_data_info", methods=['post'])
def collect_data_info():
    manager_person = request.form.get('manager_person', '所有人')
    start_date = request.form.get('start_date', '2020-01-01')
    end_date = request.form.get('end_date', '2020-01-31')
    page_index = int(request.form.get('pageIndex', 1))
    page_size = int(request.form.get('pageSize', 8))
    data = DataCounts.get_info(manager_person, start_date, end_date, page_index, page_size)
    total_num = DataCounts.get_data_num(manager_person, start_date, end_date)
    return json.dumps({'code': 200, 'data': {'total_num': total_num, 'data': data}})




@app.route("/visual",)
def visual():
    """
    功能: 用户首页
    :return:
    """
    return render_template('visual.html')


@app.route("/projectcount", methods=['get'])
def project_count():
    """
        功能: 返回统计的项目部署情况, 包括项目部署总数、本月部署项目数、近7天部署项目数
        :return: {"code": 200,
                  "data": {
                        'project_count': 5,
                        'month_count': 3,
                        'week_count': 2
                  }
                  }
        """
    try:
        # 获取当前时间
        localtime = datetime.datetime.now()
        # 获取7天的时间
        date_day = datetime.timedelta(days=7)
        delta_days = localtime - date_day
        # 部署项目总数
        projects_count = Project.query.with_entities(func.count(Project.id)).all()

        # 本月部署项目总数
        month_count = Project.query.with_entities(func.count(Project.id)). \
            filter(func.date_format(Project.date_created, '%Y-%m') == localtime.strftime('%Y-%m')).all()

        # 近7天部署项目总数
        week_count = Project.query.with_entities(func.count(Project.id)). \
            filter(func.date_format(Project.date_created, '%Y-%m-%d') > delta_days.strftime('%Y-%m-%d')).all()

        data_dict = dict(
            project_count=projects_count[0][0],
            month_count=month_count[0][0],
            week_count=week_count[0][0],
        )
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "项目部署数量统计出错"})


@app.route("/datacount", methods=['get'])
def data_count():
    """
        功能: 统计爬取数据量, 包括总数据量、今日数据量
        :return: {"code": 200,
                  "data": {
                        'total_data': 56,
                        'today_data': 5,
                  }
                  }
        """
    try:
        # 获取当前时间
        localtime = datetime.datetime.now()

        # 数据获取总量
        total_data = DataCounts.query.with_entities(func.sum(DataCounts.number)).all()

        # 当日获取数据量
        today_data = DataCounts.query.with_entities(func.sum(DataCounts.number)).\
            filter(func.date_format(DataCounts.date_created, '%Y-%m-%d') == localtime.strftime('%Y-%m-%d')).all()

        data_dict = dict(
                    total_data=total_data[0][0],
                    today_data=today_data[0][0])
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)

    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "数据获取量统计出错"})


@app.route("/weeksum", methods=['get'])
def week_sum():
    """
    功能: 统计近7天爬取数据量
    :return: {"code": 200,
              "data": {
                    'week_data': {
                               'index': ['05-26','05-24','05-23'],
                               'value': [5, 3, 7},
              }
              }
    """
    try:
        # 获取当前时间
        localtime = datetime.datetime.now()
        # 获取7天的时间
        date_day = datetime.timedelta(days=7)
        delta_days = localtime - date_day

        # 近7天获取数据量, 按照每天分组求和, 返回的是列表
        week_data = DataCounts.query.with_entities(func.date_format(DataCounts.date_created, '%m-%d'),
                                                   func.sum(DataCounts.number)).\
            filter(func.date_format(DataCounts.date_created, '%Y-%m-%d') > delta_days.strftime('%Y-%m-%d')).\
            group_by(DataCounts.date_modified).order_by(func.date_format(DataCounts.date_created, '%Y-%m-%d')).all()

        data_dict = dict(
                    week_data=week_data)
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)

    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "本周数据获取量统计出错"})


@app.route("/ranksum", methods=['get'])
def rank_sum():
    """
    功能: 统计爬取数据量排名
    :return: {"code": 200,
              "data": {
                    'rank_data': {'index': ['贵阳市财政局', '贵阳市人社局'],
                               'value': [3, 2]}
              }
              }
    """
    try:
        # 获取数据排名
        rank_data = DataCounts.query.with_entities(DataCounts.project_name, func.sum(DataCounts.number))\
            .group_by(DataCounts.project_name).order_by(func.sum(DataCounts.number)).all()
        data_dict = dict(
                    rank_data={'index': DataCounts.decimal2int(rank_data)[0],
                               'value': DataCounts.decimal2int(rank_data)[1]})
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)

    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "数据获取排名统计出错"})


@app.route("/hotmap", methods=['get'])
def hot_map():
    """
        功能: 返回近7天的项目调度统计信息
        :return: {"code": 200,
                  "data": {
                        'hot_map': [
                                    ['05-26', '10', 2],
                                    ['05-24', '24', 8],
                                    ['05-22', '18', 9],
                                    ]
                  }
                  }
        """
    try:
        # 获取当前时间
        localtime = datetime.datetime.now()
        # 获取7天的时间
        date_day = datetime.timedelta(days=7)
        delta_days = localtime - date_day
        # 近7天调度热力图
        hot_map = JobExecution.query.with_entities(func.date_format(JobExecution.start_time, '%Y-%m-%d'),
                                                   func.date_format(JobExecution.start_time, '%H'),
                                                   func.count(JobExecution.id)). \
            filter(func.date_format(JobExecution.start_time, '%Y-%m-%d') > delta_days.strftime('%Y-%m-%d')). \
            group_by(func.date_format(JobExecution.start_time, '%Y-%m-%d'),
                     func.date_format(JobExecution.start_time, '%H')).all()

        data_dict = dict(
            hot_map=DataCounts.array2dict_or_list(hot_map)
        )
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)

    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "项目调度信息统计出错"})


@app.route("/project_type_run", methods=['get'])
def project_type_run():
    """
    功能: 返回部署的项目分类情况及项目基本信息
    :return: {"code": 200,
              "data": {
                    'run_situation': [
                    ['贵阳市人社局', '贵阳市人社局', '公文公告', '05-26', '3'],
                    ['贵阳市财政局', '贵阳市财政局', '公文公告', '05-24', '3'],
                    ],
                    'project_type': [
                                        {'name': '公文公告',
                                        'value': 5},
                                       {'name': '其他',
                                       'value': 5},
                                       ]
              }
              }
    """
    try:
        # 查询项目调度任务表
        job_execution = JobExecution.query.group_by(JobExecution.project_id).\
            order_by(JobExecution.start_time).distinct().all()

        # 根据调度任务Id查询项目信息
        project_data = []
        for job in job_execution:
            project = Project.query.with_entities(Project.project_name, Project.project_alias, Project.project_cate,
                                                  func.date_format(JobExecution.start_time, '%Y-%m-%d %H:%i:%S'),
                                                  JobExecution.running_status).\
                filter_by(id=job.project_id).first()
            project_data.append(project)

        # 项目分类统计
        project_type = Project.query.with_entities(Project.project_cate, func.count(Project.project_cate))\
            .group_by('project_cate').all()
        data_dict = dict(
            run_situation=DataCounts.array2dict_or_list(project_data),
            project_type=DataCounts.array2dict_or_list(project_type),
        )
        return json.dumps({"code": 200, "data": data_dict}, cls=DecimalEncoder)
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "项目信息统计出错"})
