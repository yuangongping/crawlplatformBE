from SpiderKeeper.app import db, Base


class SpiderInstance(Base):
    """
    蜘蛛spider ORM类
    """

    __tablename__ = 'sk_spider'

    spider_name = db.Column(db.String(100))
    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    spider_name_slave = db.Column(db.String(100))

    @classmethod
    def update_spider_instances(cls, project_id, spider_instance_list):
        """
        根据爬虫项目爬虫项目Project id及蜘蛛信息列表, 更新爬虫项目爬虫项目中的Spider蜘蛛信息
        :param project_id: 爬虫项目ID
        :param spider_instance_list: Spider蜘蛛信息列表
        :return:
        """

        # 如果数据库中没有爬虫项目ID及Spider这条记录就往数据库插入该记录
        for spider_instance in spider_instance_list:
            existed_spider_instance = cls.query.filter_by(project_id=project_id,
                                                          spider_name=spider_instance.spider_name).first()
            if not existed_spider_instance:
                db.session.add(spider_instance)
                db.session.commit()

        # 从数据库中取出某个爬虫项目下所有的Spider蜘蛛信息
        # 如果数据库中的Spider蜘蛛不在提交过来的蜘蛛信息列表里面则从数据库中删除该蜘蛛信息
        for spider in cls.query.filter_by(project_id=project_id).all():
            existed_spider = any(
                spider.spider_name == s.spider_name
                for s in spider_instance_list
            )
            if not existed_spider:
                db.session.delete(spider)
                db.session.commit()

    @classmethod
    def list_spider_by_project_id(cls, project_id):
        """
        通过爬虫项目id列出某个爬虫项目在sk_spider表下的所有蜘蛛信息
        :param project_id: 爬虫项目id
        :return: 某个爬虫项目id在sk_spider表下的所有蜘蛛信息
        """
        return cls.query.filter_by(project_id=project_id).all()

    def to_dict(self):
        return dict(spider_instance_id=self.id,
                    spider_name=self.spider_name,
                    spider_name_slave=self.spider_name_slave,
                    project_id=self.project_id)

    @classmethod
    def list_spiders(cls, project_id):
        """
        通过爬虫项目id列出某个爬虫项目下的所有蜘蛛及其任务运行信息(蜘蛛最新的任务的创建时间、平均运行时间)
        :param project_id:  爬虫项目id
        :return: list 某个爬虫项目id下的所有蜘蛛及其任务运行信息
        """

        # 该sql语句用于获取所有蜘蛛最新的任务的创建时间
        # 返回 [(蜘蛛名称1, 最新的任务创建时间), (蜘蛛名称2, 最新的任务创建时间)]
        sql_last_runtime = '''
            select * from (select a.spider_name,b.date_created from sk_job_instance as a
                left join sk_job_execution as b
                on a.id = b.job_instance_id
                order by b.date_created desc) as c
                group by c.spider_name
            '''
        # 该sql语句用于获取所有蜘蛛的平均运行时间
        # 返回 [(蜘蛛名称1, 任务平均运行时间), (蜘蛛名称2, 任务平均运行时间)]
        # ****** 这里有个问题, 实际把sql复制执行的时候, 返回的平均运行时间都是0, 待进一步解决 **********
        sql_avg_runtime = '''
            select a.spider_name,avg(end_time-start_time) from sk_job_instance as a
                left join sk_job_execution as b
                on a.id = b.job_instance_id
                where b.end_time is not null
                group by a.spider_name
            '''
        last_runtime_list = dict(
            (spider_name, last_run_time) for spider_name, last_run_time in db.engine.execute(sql_last_runtime))
        avg_runtime_list = dict(
            (spider_name, avg_run_time) for spider_name, avg_run_time in db.engine.execute(sql_avg_runtime))
        res = []
        for spider in cls.query.filter_by(project_id=project_id).all():
            last_runtime = last_runtime_list.get(spider.spider_name)
            res.append(dict(spider.to_dict(),
                            **{'spider_last_runtime': last_runtime if last_runtime else '-',
                               'spider_avg_runtime': avg_runtime_list.get(spider.spider_name)
                               }))
        return res
