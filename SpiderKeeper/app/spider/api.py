from flask import Blueprint, request
import json

from sqlalchemy import desc
from SpiderKeeper.app.spider.model import SpiderInstance
from SpiderKeeper.app.schedulers.model import JobExecution, JobInstance
from SpiderKeeper.app.projects.model import Project
from SpiderKeeper.app import app, agent, db
import requests
# from SpiderKeeper.app.flask_CAS import login_required

api_spider_bp = Blueprint('spider', __name__)
# 运行状态选项字典
switcher = {
    0: "PENDING",
    1: "RUNNING",
    2: "FINISHED",
    3: "CANCEL"
}


@app.route("/allspider",  methods=['get'])
def get_all_spiders_info():
    """
    功能: 返回所有的爬虫的相关信息
    :return: 返回数据格式: json, 样式如下：
    {
      "last_run_status": "success",
      "last_run_time": "2018-09-19 03:30:45",
      "project_alias": "深圳市共享开放平台",
      "project_id": 1,
      "project_name": "opendata_sz",
      "spider_alias": "所有数据",
      "spider_id": 1,
      "spider_name": "list"
    }
    """
    # 保存数据的临时列表
    datas = {'total_num': None, 'data': []}
    # 遍历实例数据库, 获取爬虫信息
    page_index = int(request.args.get('pageIndex', 1))
    page_size = int(request.args.get('pageSize', 12))
    total_num = 0
    job_executions = JobExecution.query.order_by(JobExecution.end_time).paginate(page_index, page_size, False).items
    for job in job_executions:
        _status = job_executions[-1].running_status
        # 状态信息格式转变
        status = switcher.get(_status, "CANCELED")
        # 获取实例的上一次运行时间
        last_run_time = job_executions[-1].end_time
        service_job_execution_id = job_executions[-1].service_job_execution_id
        _dict = dict(
            project_id=project.id,
            project_name=project.project_name,
            project_alias=project.project_alias,
            project_cate=project.project_cate,
            spider_id=SpiderInstance.query.filter_by(project_id=project.id).first().id,
            spider_name=SpiderInstance.query.filter_by(project_id=project.id).first().spider_name,
            spider_alias='',
            last_run_status=status,
            last_run_time=str(last_run_time).split('.')[0],
            run_type='',
            job_exec_id=service_job_execution_id,
            is_msd=project.is_msd
        )

        datas['data'].append(_dict)
    datas['total_num'] = total_num
    return json.dumps({"code": 200, 'data': datas})


@app.route("/runonce", methods=['post'])
def run_once():
    """
    功能: 单次运行爬虫
    :param: project_id: 工程id
    :param: spider_name: 爬虫名称
    :param: spider_arguments: 爬虫需要传入的参数
    :param: priority: 任务的优先级
    :param: daemon: 任务线程的类型, 是否为守护线程
    :return: json.dumps({"code": 200, "status": "success/e"}), e指具体抛出的异常
    """
    try:
        # 实例化JobInstance表
        job_instance = JobInstance()
        # 获取工程id参数
        project_id = request.form.get('project_id')
        # 获取爬虫名称并保存
        job_instance.spider_name = request.form.get('spider_name')
        # 保存project_id信息
        job_instance.project_id = project_id
        # 获取爬虫任务的优先级参数并保存
        job_instance.priority = request.form.get('priority', 0)
        # 将爬虫运行类型设置一次性运行方式
        job_instance.run_type = 'onetime'
        # 设置不可周期调度
        job_instance.enabled = -1
        # 数据库保存信息
        db.session.add(job_instance)
        db.session.commit()
        # 启动爬虫实例
        agent.start_spider(job_instance)
        return json.dumps({"code": 200, "status": "success"})
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "运行错误"})


@app.route("/cancelspider", methods=['post'])
def cancel_spider():
    """
    功能: 取消运行爬虫
    :param: project_id: 工程id
    :return: json.dumps({"code": 200, "status": "success/e"}), e指具体抛出的异常
    """
    try:
        # 获取工程id参数
        project_id = request.form.get('project_id')
        project_name = request.form.get('project_name')
        job_instance_id = int(request.form.get('job_instance_id'))
        # 同一个项目id可能有多条执行任务记录, 因此需要获取job_instance_id来判断要取消某个项目id下的第几条执行任务
        job_execution = JobExecution.query.filter_by(project_id=project_id, job_instance_id=job_instance_id).first()
        agent.cancel_spider(job_execution, project_name)
        return json.dumps({"code": 200, "status": "success"})
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "取消失败"})


@app.route("/history_spider_run_info",  methods=['get'])
def get_history_spider_run_info():
    """
    功能: 获取某个爬虫下的历史运行情况
    :return:
    """
    spider_name = request.args.get('spider_name')
    spider_to_job_instances = JobInstance.query.filter_by(spider_name=spider_name).all()[-100:]
    spiders_info_list = []
    # 如果spider有实例
    if spider_to_job_instances:
        for spider_to_job_instance in spider_to_job_instances:
            spider_to_job_instance_dict = spider_to_job_instance.to_dict()
            # 获取实例对象的的所有运行信息
            spider_job_execution = JobExecution.query.filter_by(
                job_instance_id=spider_to_job_instance_dict['job_instance_id']).all()
            for _spider_job_execution in spider_job_execution:
                _dict = {}
                _dict['start_time'] = _spider_job_execution.start_time.strftime('%Y-%m-%d %H:%M:%S')
                _dict['end_time'] = _spider_job_execution.end_time.strftime('%Y-%m-%d %H:%M:%S')
                # 获取状态信息
                _status = _spider_job_execution.running_status
                # 状态信息格式转变
                _dict['status'] = switcher.get(_status, "CANCELED")
                _dict['running_on'] = _spider_job_execution.running_on
                spiders_info_list.append(_dict)
        return json.dumps({"code": 200, 'data': spiders_info_list})
    # 数据以列表格式返回
    return json.dumps({"code": 200, 'data': spiders_info_list})


@app.route("/masterlog",  methods=['get'])
def masterlog():
    project_id = request.args.get('project_id')
    job_exec_id = request.args.get('job_exec_id')
    job_execution = JobExecution.query.filter_by(project_id=project_id, service_job_execution_id=job_exec_id).first()
    res = requests.get(agent.log_url_master(job_execution))
    res.encoding = 'utf8'
    raw = res.text.split('\n')
    if len(raw) > 300:
        raw = raw[:150] + raw[-150:]
        raw = '\n'.join(raw)
    else:
        raw = '\n'.join(raw)
    return json.dumps({"code": 200, 'log': raw.split('\n')})


@app.route("/slavelog",  methods=['get'])
def slavelog():
    project_id = request.args.get('project_id')
    job_exec_id = request.args.get('job_exec_id')
    job_execution = JobExecution.query.filter_by(project_id=project_id, service_job_execution_id=job_exec_id).first()
    res = requests.get(agent.log_url_slave(job_execution))
    res.encoding = 'utf8'
    raw = res.text.split('\n')
    if len(raw) > 300:
        raw = raw[:150] + raw[-150:]
        raw = '\n'.join(raw)
    else:
        raw = '\n'.join(raw)
    return json.dumps({"code": 200, 'log': raw.split('\n')})
