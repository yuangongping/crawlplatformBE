from SpiderKeeper.app import db, Base


class Project(Base):
    """
    Project爬虫项目ORM类
    """
    __tablename__ = 'sk_project'
    project_name = db.Column(db.String(50), unique=True)
    applicant = db.Column(db.String(50))  # 申请人
    developers = db.Column(db.String(50))  # 项目的开发者
    for_project = db.Column(db.String(50))  # 提出需求的项目
    project_cate = db.Column(db.String(100))  # 爬虫分类
    project_alias = db.Column(db.String(100))  # 项目的备注
    is_msd = db.Column(db.String(50))  # 是否是主从分布式爬虫 0 单机爬虫 1 分布式爬虫

    @classmethod
    def load_project(cls, project_list):
        """
        将爬虫项目列表里面的爬虫项目添加进入数据库
        :param project_list: 爬虫项目列表
        :return:
        """
        for project in project_list:
            existed_project = cls.query.filter_by(project_name=project.project_name).first()
            if not existed_project:
                db.session.add(project)
                db.session.commit()

    @classmethod
    def find_project_by_id(cls, project_id):
        """
        根据爬虫项目id查找爬虫项目信息
        :param project_id: 爬虫项目id
        :return:
        """
        return Project.query.filter_by(id=project_id).first()

    def to_dict(self):
        return dict(
            project_id=self.id,
            project_name=self.project_name,
            applicant=self.applicant,
            developers=self.developers,
            for_project=self.for_project,
            project_alias=self.project_alias,
            project_cate=self.project_cate,
            create_time=str(self.date_created),
            is_msd=self.is_msd
        )