from flask import Blueprint, request, send_from_directory
import json
import os
import tempfile
from werkzeug.utils import secure_filename
from SpiderKeeper.app.spider.model import SpiderInstance
from SpiderKeeper.app.schedulers.model import JobExecution, JobInstance
from SpiderKeeper.app.projects.model import Project
from SpiderKeeper.app.spider.api import switcher
from SpiderKeeper.app import app, agent, db
from flask import render_template
from flask import make_response
import datetime
from SpiderKeeper.app.projects.renrenspider.run import RenRenSpider
from SpiderKeeper.app.projects.renrenspider import settings
import socket
from flask import Response
# from SpiderKeeper.app.flask_CAS import login_required

api_project_bp = Blueprint('project', __name__)


@app.route("/", methods=['get'])
def index():
    """
    功能: 用户首页
    :return:
    """
    res = make_response(render_template('index.html'))
    res.set_cookie('username', 'admin')
    res.set_cookie('roles', 'admin,developer')
    return res


@app.route("/allproject", methods=['get'])
def all_project():
    """
    功能: 获取工程的相关信息
    :return: 返回数据格式: json, 样式如下：
    {
      "code": 200,
      "data": [
        {
          "applicant": "李科君",
          "create_time": "2018-09-19 03:30:45",
          "developers": ["袁公萍","程培东"],
          "for_project": "全国一体化大数据中心典型应用",
          "project_alias": "深圳市共享开放平台",
          "project_id": 1,
          "project_name": "opendata_sz",
          "is_msd": "0"
          "status": "FINISGED"
        }]}
    """
    datas = {'total_num': None, 'data': []}
    page_index = int(request.args.get('pageIndex', 1))
    page_size = int(request.args.get('pageSize', 8))
    datas['total_num'] = Project.query.count()
    # 遍历数据库中的所有工程
    for project in Project.query.order_by(Project.date_created.desc()).paginate(page_index, page_size, False).items:
        _dict = project.to_dict()  # 得到工程信息, 字典格式
        # 依据工程的id查询JobExecution表, 获取运行状态信息, 读取最后一个则为最新的信息
        # 判断工程是否是首次运行, 是则读取状态信息, 否则status=PENDING
        _status = JobExecution.query.filter_by(project_id=_dict['project_id']).all()
        if _status:
            _status = _status[-1].running_status
            _dict['status'] = switcher.get(_status, "CANCELED")
        else:
            _dict['status'] = 'PENDING'
        # 将状态信息(数字格式)转换为英文格式
        datas['data'].append(_dict)
    return json.dumps({'code': 200, 'data': datas})


@app.route("/addproject", methods=['POST'])
def add_project():
    """
    功能: 创建工程, 上传工程的egg文件, 将工程部署到scrapyd服务器上
    :param: project_name: 工程名称
    :param: project_alias: 工程备注或中文名称
    :param: for_project: 引用工程
    :param: developers: 爬虫项目的开发者
    :param: applicant: 爬虫申请人
    :param: egg_file: 待上传的爬虫项目的egg文件
    :return: 返回数据格式: json, 部署成功,返回success, 否则返回error
    """
    status = 'error'
    project = Project()
    is_msd = request.form.get('is_msd')  # 是否为分布式
    project.is_msd = is_msd
    project.project_name = request.form.get('project_name')  # 工程名
    project.project_alias = request.form.get('project_alias')  # 工程备注
    project.for_project = request.form.get('for_project', None)  # 引用工程
    project.developers = request.form.get('developers', None)  # 开发者
    project.project_cate = request.form.get('pro_type', None)  # 爬虫分类
    project.applicant = request.form.get('applicant', None)  # 申请人
    project.date_created = datetime.datetime.now().strptime(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    project.date_modified = datetime.datetime.now().strptime(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    if not is_msd:
        return json.dumps({"code": 500, "status": '项目类型不能为空, 项目类型为分布式or单机'})
    # 判断是否有值输入
    if request.form.get('project_name') == '' or request.form.get('project_alias') == '':
        return json.dumps({"code": 200, "status": 'no input!'})

    # 判断工程名是否存在
    existed_project = project.query.filter_by(project_name=request.form['project_name']).first()
    # 工程存在则不能保存信息以及部署, 不存在则正常部署
    if existed_project:
        return json.dumps({"code": 200, "status": 'existed'})

    egg_path_dict = {}  # 用于存放egg文件保存路径
    if is_msd == '0':  # 如果为单机爬虫
        egg = request.files['egg']  # 如果是单机部署, 则文件放在某一个从服务器中
        if egg:
            filename = secure_filename(egg.filename)  # 获取egg文件名
            dst_egg = os.path.join(tempfile.gettempdir(), filename)  # 拼接文件路径
            egg.save(dst_egg)  # 保存egg文件
            egg_path_dict['egg'] = dst_egg  # 将项目文件路径保存到egg路径字典中
        else:  # 如果有一个没有上传文件
            return json.dumps({"code": 500, "status": ' egg file are must'})
    else:
        # 获取上传文件
        master_egg = request.files['master_egg']
        slave_egg = request.files['slave_egg']
        # 判断表单是否传入文件
        if master_egg and slave_egg:
            master_filename = secure_filename(master_egg.filename)  # 获取master文件名
            slave_filename = secure_filename(slave_egg.filename)  # 获取slave文件名
            dst_master_egg = os.path.join(tempfile.gettempdir(), master_filename)  # 拼接文件路径
            dst_slave_egg = os.path.join(tempfile.gettempdir(), slave_filename)  # 拼接文件路径
            slave_egg.save(dst_slave_egg)  # 保存slave文件
            master_egg.save(dst_master_egg)  # 保存master文件
            egg_path_dict['master'] = dst_master_egg  # 将master项目文件路径保存到egg路径字典中
            egg_path_dict['slave'] = dst_slave_egg  # 将slave项目文件路径保存到egg路径字典中
        else:  # 如果有一个没有上传文件
            return json.dumps({"code": 500, "status": 'master and slave egg are must'})

    if agent.deploy(project, egg_path_dict, is_msd):
        status = 'success'
        # 部署成功后才将数据保存至数据库
        db.session.add(project)
        db.session.commit()

        return json.dumps({"code": 200, "status": status})
    else:
        return json.dumps({"code": 500, "status": "error", "msg": "部署错误"})


@app.route("/editproject", methods=['POST'])
def edit_project_info():
    try:
        project_id = request.form.get('project_id')
        project = Project.query.filter_by(id=project_id).first()
        project.project_name = request.form.get('project_name')  # 工程名
        project.project_alias = request.form.get('project_alias')  # 工程备注
        project.for_project = request.form.get('for_project')  # 引用工程
        project.developers = request.form.get('developers')  # 开发者
        project.project_cate = request.form.get('project_cate')  # 爬虫分类
        project.applicant = request.form.get('applicant')  # 申请人
        db.session.commit()
        return json.dumps({"code": 200, "status": "success"})
    except:
        return json.dumps({"code": 500, "status": "error", "msg": "更新错误"})


@app.route("/delproject", methods=['post'])
def del_project():
    """
    功能: 通过project_id删除工程,首先在scrapyd服务器进行删除,
          然后同步数据进行删除
    :param project_id: 工程id
    :return: 如果在scrapyd服务器删除成功, 且数据库同步后返回success, 否则返回error
    """
    try:
        project_name = request.form.get('project_name')
        # 依据id检索工程
        project = Project.query.filter_by(project_name=project_name).first()
        # 判断scrapyd服务器是否删除成功, 成功则进行数据库同步, 并返回status
        if agent.delete_project(project):
            # 删除工程
            db.session.delete(project)
            # 删除数据裤中对应工程下的spider
            spiders = SpiderInstance.query.filter_by(project_id=project.id).all()
            for spider in spiders:
                db.session.delete(spider)
            # 删除数据裤中对应工程下的job_instances
            instances = JobInstance.query.filter_by(project_id=project.id).all()
            for instance in instances:
                db.session.delete(instance)
            # 删除数据裤中对应工程下的job_execution
            executions = JobExecution.query.filter_by(project_id=project.id).all()
            for execution in executions:
                db.session.delete(execution)
            db.session.commit()
            return json.dumps({"code": 200, "status": "success"})
    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "删除错误"})


@app.route("/projectinfo",  methods=['get'])
def get_single_project_info():
    """
    功能: 返回单个工程的相关信息
    :param project_name: 工程名
    :return: 返回json数据格式, 样例如下：
     {
      "code": 200,
      "data": [{
        "project_id": 1,
        "project_name": "opendata_sz",
        "project_alias": "深圳市共享开放平台",
        "create_time": "2018-09-22 11:30:23",
        "developers": ["程培东","袁公萍"],
        "for_project": "全国一体化大数据中心",
        "applicant": "胥月",
        "spiders": [{
            "spider_id": 1,
            "spider_alias": "所有数据",
            "spider_name": "list",
            "last_run_time": "2018-09-19 03:30:45",
            "last_run_status": "success",
            "circle_type": null
            },{
            "spider_id": 2,
            "spider_alias": "数据",
            "spider_name": "shuju",
            "last_run_time": "2018-09-19 07:37:25",
            "last_run_status": "success",
            "circle_type": "week"
          }
        ]
      }]
    }
    """
    project_name = request.args.get('project_name')
    # 返回的临时spiders数据列表变量
    spiders_info_list = []
    # 依据project_name查询工程信息
    project_info = Project.query.filter_by(project_name=project_name).first()
    # 遍历爬虫数据库
    for spider in SpiderInstance.query.filter_by(project_id=project_info.id).all():
        # 返回字典信息
        spider_dict = spider.to_dict()
        # 查找该spider对应的实例
        spider_to_job_instances = JobInstance.query.filter_by(
            project_id=spider_dict.get('project_id'),
            spider_name=spider_dict.get('spider_name')).all()
        # 如果spider没有实例
        if not spider_to_job_instances:
            spider_info = dict(
                spider_id=spider_dict.get('spider_instance_id'),
                spider_alias=None,
                spider_name=spider_dict.get('spider_name'),
                last_run_time=None,
                last_run_status=None,
                circle_type=None,
                job_exec_id=None,
                enabled=None,
            )
            spiders_info_list.append(spider_info)
        else:
            for spider_to_job_instance in spider_to_job_instances:
                spider_to_job_instance_dict = spider_to_job_instance.to_dict()
                # 获取实例对象的最后一次运行时间
                spider_job_execution = JobExecution.query.filter_by(
                    job_instance_id=spider_to_job_instance_dict['job_instance_id']).all()
                if len(spider_job_execution) > 0:
                    last_run_time = spider_job_execution[-1].end_time
                    # 获取状态信息
                    _status = spider_job_execution[-1].running_status
                    # 状态信息格式转变
                    status = switcher.get(_status, "CANCELED")
                    job_exec_id = spider_job_execution[-1].service_job_execution_id
                else:
                    status = 'PENDING'
                    last_run_time = None
                    job_exec_id = None

                # 获取每个实例对应的spider的信息
                corn = """
                每天：{}点
                """.format(
                    spider_to_job_instance_dict.get('cron_hour')
                )
                spider_info = dict(
                    job_instance_id=spider_to_job_instance_dict.get('job_instance_id'),
                    spider_id=spider_dict.get('spider_instance_id'),
                    spider_alias=spider_to_job_instance_dict['desc'],
                    spider_name=spider_dict['spider_name'],
                    last_run_time=str(last_run_time).split('.')[0],
                    last_run_status=status,
                    circle_type=spider_to_job_instance_dict['run_type'],
                    job_exec_id=job_exec_id,
                    enabled=spider_to_job_instance_dict.get('enabled'),
                    cron=corn
                )
                # 将spider信息放入spiders列表里
                spiders_info_list.append(spider_info)
    # 信息合并到工程信息下, 格式字典
    _dict = dict(
        project_id=project_info.id,
        project_name=project_name,
        project_alias=project_info.project_alias,
        create_time=str(project_info.date_modified),
        developers=project_info.developers,
        for_project=project_info.for_project,
        applicant=project_info.applicant,
        spiders=spiders_info_list,
        project_cate=project_info.project_cate,
        is_msd=project_info.is_msd
    )
    # 数据以列表格式返回
    return json.dumps({"code": 200, 'data': _dict})


@app.route("/fasterscrapy", methods=['post'])
def faster_scrapy():
    try:
        settings.PROJECT_NAME = request.form.get('projectName')
        settings.SPIDER_NAME = request.form.get('spiderName')
        settings.DB_IP = request.form.get('dbAddress')
        settings.DB_NAME = request.form.get('dbName')
        settings.DB_USERNAME = request.form.get('dbUserName')
        settings.DB_PASSWORD = request.form.get('dbPassword')
        settings.TABLE_NAME = request.form.get('bdTableName')
        settings.TABLE_COMMENTS = request.form.get('bdTableComment')
        settings.ITEMS = json.loads(request.form.get('items'))
        settings.BEIZHU = request.form.get('bdTableComment')
        settings.DATATYPE = request.form.get('dataType')
        # 生成项目文件夹
        renRenSpider = RenRenSpider(settings)
        renRenSpider.creat_all()
        # 将项目文件打包成压缩文件并返回至前端
        renRenSpider.zipFile()
        return json.dumps({'code': 200, 'data': '成功！'})
    except:
        return json.dumps({'code': 500, 'data': '生成文件错误！'})


@app.route("/download/<projectname>", methods=['get'])
def download(projectname):
    filepath = './SpiderKeeper/app/projects/renrenspider/temp/{}.zip'.format(projectname)
    filename = os.path.basename(filepath)
    response = Response(file_iterator(filepath))
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
    return response


def file_iterator(file_path, chunk_size=512):
    """
        文件读取迭代器
    :param file_path:文件路径
    :param chunk_size: 每次读取流大小
    :return:
    """
    with open(file_path, 'rb') as target_file:
        while True:
            chunk = target_file.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break

