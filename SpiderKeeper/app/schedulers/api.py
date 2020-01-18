import json
import os
import tempfile
from werkzeug.utils import secure_filename
from flask import Blueprint, request
from SpiderKeeper.app import app, agent, db
from SpiderKeeper.app.spider.model import SpiderInstance
from SpiderKeeper.app.schedulers.model import JobExecution, JobInstance
from SpiderKeeper.app.projects.model import Project


# 注册调度蓝本
api_schedulers_bp = Blueprint('schedulers', __name__)


@app.route("/addscheduler", methods=['post'])
def add_scheduler():
    """
    功能: 给爬虫添加周期调度实例, 添加成功后数据库同步
    :param: project_id: 工程id
    :param: spider_name: 爬虫名称
    :param: spider_arguments: 爬虫需要传入的参数
    :param: priority: 任务的优先级
    :param: daemon: 任务线程的类型, 是否为守护线程
    :param: cron_minutes: 调度周期参数-分钟
    :param: cron_hour: 调度周期参数-小时
    :param: cron_day_of_month: 调度周期参数-每月的天
    :param: cron_day_of_week: 调度周期参数-每周的星期
    :return: json.dumps({"code": 200, "status": "success/e"}), e指具体抛出的异常
    """
    try:
        project_id = request.form.get('project_id')
        jobinstances = JobInstance.query.filter_by(project_id=project_id).all()
        for jobinstance in jobinstances:
            jobinstance.enabled = 0
        job_instance = JobInstance()
        job_instance.spider_name = request.form['spider_name']
        job_instance.project_id = project_id
        job_instance.priority = request.form.get('priority') or 0
        job_instance.run_type = 'periodic'
        job_instance.cron_minutes = request.form.get('selectedminutes') or '0'
        job_instance.cron_hour = request.form.get('selectedhours') or '*'
        job_instance.cron_day_of_month = request.form.get('selecteddays') or '*'
        job_instance.cron_day_of_week = request.form.get('cron_day_of_week') or '*'
        job_instance.cron_month = request.form.get('selectedmonths') or '*'
        db.session.add(job_instance)
        db.session.commit()
        return json.dumps({"code": 200, "status": "success"})
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "添加调度错误"})


@app.route("/cancelscheduler", methods=['get'])
def cancel_scheduler():
    """
    功能: 删除job_instance
    传入参数: 分别传入工程id与job实例id: job_instance_id
    :return:
    """
    try:
        project_id = request.args.get('project_id')
        jobinstances = JobInstance.query.filter_by(project_id=project_id).all()
        for jobinstance in jobinstances:
            jobinstance.enabled = -1
            if jobinstance.run_type == 'periodic':
                db.session.delete(jobinstance)
        db.session.commit()
        return json.dumps({"code": 200, "status": "success"})
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "移除错误"})


@app.route("/delscheduler",  methods=['get'])
def del_scheduler():
    try:
        job_instance_id = request.args.get('job_instance_id')
        db.session.delete(JobInstance.query.filter_by(id=job_instance_id).first())
        db.session.commit()
        for item in JobExecution.query.filter_by(job_instance_id=job_instance_id).all():
            db.session.delete(item)
        return json.dumps({"code": 200, "status": "success"})
    except:
        return json.dumps({"code": 500, "status": "error", "msg": "删除错误"})

