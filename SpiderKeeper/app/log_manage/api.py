from flask import Blueprint
from SpiderKeeper.app import app
import json
from elasticsearch import Elasticsearch


api_log_bp = Blueprint('api_log_bp', __name__)

# --------连接Elasticsearch数据库提取日志数据--------#
es_connection = Elasticsearch(hosts=['http://172.10.10.31:9200/'])


@app.route("/logmanage", methods=['get'])
def log_manage():
    '''
    功能：从Elasticsearch中获取日志数据
    :return: {"code": 200,
                  "data": {
                        'project_group': {
                                'key':'other_agent', 'doc_count':'3405', 'key':'china_standard', 'doc_count':'123456'
                        },
                        'total': 34205,
                        'messages': {
                                'path': '/home/python/run_env/scrapyd/logs/26f688ce0b4a11e9907a0cda411d4f43.log',
                                'loglevel': 'ERROR',
                                'messages': ' Error processing {\'_id\': \'154607611718500000\.......',
                                'time': '2018-12-29',
                                'project_name': 'china_standard',
                                'type': '172.10.10.185'
                        }
                  }
    }
    '''
    try:
        # 操作elasticsearch数据库的执行语句
        # 主要是按照项目名称分组计数并查询所有的错误日志
        query_json = {
            "size": 1000,  # 控制获取数据量
            "query": {
                "term": {
                    "loglevel.keyword": "ERROR"  # 查询条件语句
                }
            },
            "aggs": {  # 分组聚合
                "project_group": {
                    "terms": {
                        "field": "project_name"
                    }
                }
            }
        }
        # 筛选需要获取的字段
        source = ["project_name", "loglevel", "time", "path", "type", "messages"]
        # 从数据库中提取数据
        es_data = es_connection.search(index='_all', body=query_json, _source=source)
        messages = []
        # 获取分组聚合的各项目出现错误的数量
        project_group = es_data['aggregations']['project_group']['buckets']
        # 获取总的错误数
        total = es_data['hits']['total']
        # 递归出现错误的详细数据及字段, 提取需要的数据
        for data in es_data['hits']['hits']:
            messages.append(data['_source'])

        data_dict = dict(
            project_group=project_group,
            total=total,
            messages=messages
        )
        return json.dumps({"code": 200, "data": data_dict})

    except Exception as e:
        return json.dumps({"code": 500, "status": "error", "msg": "日志信息获取出错"})
