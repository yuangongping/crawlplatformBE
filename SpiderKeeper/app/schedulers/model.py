import datetime
from sqlalchemy import desc
from SpiderKeeper.app import db, Base


class JobPriority():
    LOW, NORMAL, HIGH, HIGHEST = range(-1, 3)


class JobRunType():
    ONETIME = 'onetime'
    PERIODIC = 'periodic'


class SpiderStatus():
    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobExecution(Base):
    """
    执行任务ORM类
    """
    __tablename__ = 'sk_job_execution'
    project_id = db.Column(db.INTEGER, nullable=False, index=True)  # 爬虫项目id
    service_job_execution_id = db.Column(db.String(255), nullable=False, index=True)  # 任务执行历史id
    job_instance_id = db.Column(db.INTEGER, nullable=False, index=True)  # 对应的执行的调度任务id
    create_time = db.Column(db.DATETIME)  # 该条历史任务的创建时间
    start_time = db.Column(db.DATETIME)  # 执行任务开始时间
    end_time = db.Column(db.DATETIME)  # 执行任务结束时间
    running_status = db.Column(db.INTEGER, default=SpiderStatus.PENDING)  # 执行状态
    running_on = db.Column(db.Text)  # 执行主机 'localhost:6800'

    def to_dict(self):
        """
        以字典方式放回Job任务的自身信息
        :return: dict Job任务的自身信息
        """
        job_instance = JobInstance.query.filter_by(id=self.job_instance_id).first()
        return {
            'project_id': self.project_id,
            'job_execution_id': self.id,
            'job_instance_id': self.job_instance_id,
            'service_job_execution_id': self.service_job_execution_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'running_status': self.running_status,
            'running_on': self.running_on,
            'job_instance': job_instance.to_dict() if job_instance else {}
        }

    @classmethod
    def find_job_by_service_id(cls, service_job_execution_id):
        return cls.query.filter_by(service_job_execution_id=service_job_execution_id).first()

    @classmethod
    def list_job_by_service_ids(cls, service_job_execution_ids):
        return cls.query.filter(cls.service_job_execution_id.in_(service_job_execution_ids)).all()

    @classmethod
    def list_uncomplete_job(cls):
        return cls.query.filter(cls.running_status != SpiderStatus.FINISHED,
                                cls.running_status != SpiderStatus.CANCELED).all()

    @classmethod
    def list_jobs(cls, project_id, each_status_limit=100):
        """
        通过爬虫项目id列出前n条 等待执行、正在执行、执行完成的任务信息
        :param project_id: 工程id
        :param each_status_limit: 每个执行状态返回的任务条数, 默认为100条
        :return: dict 每个执行状态的任务信息
        """
        result={}
        result['PENDING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.PENDING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['RUNNING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.RUNNING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['COMPLETED'] = [job_execution.to_dict() for job_execution in
                               JobExecution.query.filter(JobExecution.project_id == project_id).filter(
                                   (JobExecution.running_status == SpiderStatus.FINISHED) | (
                                       JobExecution.running_status == SpiderStatus.CANCELED)).order_by(
                                   desc(JobExecution.date_modified)).limit(each_status_limit)]
        return result

    @classmethod
    def list_run_stats_by_hours(cls, project_id):
        """
        列出一个工程在24小时内每个小时的蜘蛛运行状态, 用于前端可视化展现
        :param project_id: 工程id
        :return: list 每个小时内的运行状态列表 ex: [{'00:00': 6, '01:00': 3}]
        """
        result = {}
        hour_keys = []
        last_time = datetime.datetime.now() - datetime.timedelta(hours=23)
        last_time = datetime.datetime(last_time.year, last_time.month, last_time.day, last_time.hour)
        for hour in range(23, -1, -1):
            time_tmp = datetime.datetime.now() - datetime.timedelta(hours=hour)
            hour_key = time_tmp.strftime('%Y-%m-%d %H:00:00')
            hour_keys.append(hour_key)
            result[hour_key] = 0  # init
        for job_execution in JobExecution.query.filter(JobExecution.project_id == project_id,
                                                       JobExecution.date_created >= last_time).all():
            hour_key = job_execution.create_time.strftime('%Y-%m-%d %H:00:00')
            result[hour_key] += 1
        return [dict(key=hour_key, value=result[hour_key]) for hour_key in hour_keys]


class JobInstance(Base):
    """
    调度任务ORM类
    """
    __tablename__ = 'sk_job_instance'
    spider_name = db.Column(db.String(100), nullable=False, index=True)  # 蜘蛛名称
    project_id = db.Column(db.INTEGER, nullable=False, index=True)  # 爬虫项目id
    tags = db.Column(db.Text)  # 任务的标签（通过英文逗号隔开）
    spider_arguments = db.Column(db.Text)  # 任务执行参数, 通过英文逗号隔开 (ex.: arg1=foo,arg2=bar)
    priority = db.Column(db.INTEGER)  # 任务优先级
    desc = db.Column(db.Text)  # 任务描述
    cron_minutes = db.Column(db.String(20), default="0")  # 周期调度时间-分钟, 默认是0
    cron_hour = db.Column(db.String(20), default="*")  # 周期调度时间-小时, 默认是*
    cron_day_of_month = db.Column(db.String(20), default="*")  # 周期调度时间-天, 默认是*
    cron_day_of_week = db.Column(db.String(20), default="*")  # 周期调度时间-星期, 默认是*
    cron_month = db.Column(db.String(20), default="*")  # 周期调度时间-月份, 默认是*
    enabled = db.Column(db.INTEGER, default=0)  # 0/-1  # 是否可以被周期调度 0可以 -1不可以
    run_type = db.Column(db.String(20))  # periodic/onetime  调度方式 周期性 和 一次性

    def to_dict(self):
        """
        以字典方式放回Job任务的自身信息
        :return: dict Job任务的自身信息
        """
        return dict(
            job_instance_id=self.id,
            project_id=self.project_id,
            spider_name=self.spider_name,
            tags=self.tags.split(',') if self.tags else None,
            spider_arguments=self.spider_arguments,
            priority=self.priority,
            desc=self.desc,
            cron_minutes=self.cron_minutes,
            cron_hour=self.cron_hour,
            cron_day_of_month=self.cron_day_of_month,
            cron_day_of_week=self.cron_day_of_week,
            cron_month=self.cron_month,
            enabled=self.enabled == 0,
            run_type=self.run_type

        )

    @classmethod
    def list_job_instance_by_project_id(cls, project_id):
        """
        通过爬虫项目id列出其所有的Job任务信息
        :param project_id: 爬虫项目id
        :return: list Job任务信息
        """
        return cls.query.filter_by(project_id=project_id).all()

    @classmethod
    def find_job_instance_by_id(cls, job_instance_id):
        """
        通过Job任务id查询Job任务信息
        :param job_instance_id: Job任务id
        :return: JobInstance Job任务信息
        """
        return cls.query.filter_by(id=job_instance_id).first()