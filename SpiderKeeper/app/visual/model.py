from SpiderKeeper.app import db, Base
from sqlalchemy import func
from SpiderKeeper.app.projects.model import Project

class DataCounts(Base):
    __tablename__ = 'sk_data_count'
    project_name = db.Column(db.String(255))  # 工程名 **必须与上传到爬虫平台的英文工程名同名
    developers = db.Column(db.String(255))
    address = db.Column(db.String(255))
    db_name = db.Column(db.String(255))
    table_name = db.Column(db.String(255))
    number = db.Column(db.String(255))
    image_number = db.Column(db.String(255))
    video_number = db.Column(db.String(255))
    audio_number = db.Column(db.String(255))
    file_number = db.Column(db.String(255))
    image_size = db.Column(db.String(255))
    video_size = db.Column(db.String(255))
    audio_size = db.Column(db.String(255))
    file_size = db.Column(db.String(255))

    @classmethod
    def to_dict(cls, obj):
        return dict(
            projectName=obj.project_name,
            date=str(obj.date_created).split()[0],
            address=obj.address,
            dbName=obj.db_name,
            tableName=obj.table_name,
            image="{} / {}".format(obj.image_number, obj.image_size),
            video="{} / {}".format(obj.video_number, obj.video_size),
            audio="{} / {}".format(obj.audio_number, obj.audio_size),
            files="{} / {}".format(obj.file_number, obj.file_size),
            total=obj.number
        )

    @classmethod
    def decimal2int(cls, data):
        data_list = []
        index_list =[]
        for i in data:
            data_list.append(i[1])
            index_list.append(i[0])
        return index_list, data_list

    @classmethod
    def array2dict_or_list(cls, data):
        data_list = []
        for i in data:
            if len(i) > 2:
                index_list = list(i)
                data_list.append(index_list)
            else:
                data_dict = {}
                data_dict['value'] = i[1]
                data_dict['name'] = i[0]
                data_list.append(data_dict)
        return data_list

    @classmethod
    def insert_record(cls, data_dict):
        try:
            record = cls(
                project_name=data_dict.get('project_name'),
                address=data_dict.get('address'),
                db_name=data_dict.get('db_name'),
                table_name=data_dict.get('table_name'),
                number=data_dict.get('number'),
                image_number=data_dict.get('image_number'),
                video_number=data_dict.get('video_number'),
                audio_number=data_dict.get('audio_number'),
                file_number=data_dict.get('file_number'),
                image_size=data_dict.get('image_size'),
                video_size=data_dict.get('video_size'),
                audio_size=data_dict.get('audio_size'),
                file_size=data_dict.get('file_size'),
            )
            db.session.add(record)
            db.session.commit()
            return True
        except:
            return False

    @classmethod
    def get_info(cls, manager_person, start_date, end_date, page_index, page_size):
            data = []
            if manager_person == "所有人":
                objs = cls.query.filter(
                        func.date_format(cls.date_created, '%Y-%m-%d') >= start_date,
                        func.date_format(cls.date_created, '%Y-%m-%d') <= end_date
                    ).paginate(page_index, page_size, False).items
            else:
                objs = cls.query.filter(
                    func.date_format(cls.date_created, '%Y-%m-%d') >= start_date,
                    func.date_format(cls.date_created, '%Y-%m-%d') <= end_date,
                    cls.developers.contains(manager_person)
                ).paginate(page_index, page_size, False).items
            for obj in objs:
                data.append(cls.to_dict(obj))
            return data

    @classmethod
    def get_data_num(cls, manager_person, start_date, end_date):
        if manager_person == "所有人":
             return cls.query.filter(func.date_format(cls.date_created, '%Y-%m-%d') >= start_date,
                                func.date_format(cls.date_created, '%Y-%m-%d') <= end_date).count()
        else:
            return cls.query.filter(
                func.date_format(cls.date_created, '%Y-%m-%d') >= start_date,
                func.date_format(cls.date_created, '%Y-%m-%d') <= end_date,
                cls.developers.contains(manager_person)
            ).count()





