# -*- coding=utf-8 -*-

import pymongo
import yaml
from datetime import datetime
from django.conf import settings


class Mongodb(object):
    '''
     初始化mongo连接，封装插入，查询, 过滤数据
    '''

    def __init__(self, db='autoops', collection='tasklog'):
        self.client = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
        self.db = self.client[db]
        self.col = self.db[collection]

    def insert(self, content):
        return self.col.insert_one(content)

    def find_all(self):
        return self.col.find().sort('createtime', -1)

    def filter(self, adhoc_id):
        result = []
        if adhoc_id:
            args = {'taskid': adhoc_id, '_id': 0}
            logs = self.col.find(args).sort('time')
            for res in logs:
                result.append(res)
            print('...........................mongo', result, adhoc_id)
        else:
            return False


class InsertAdhocLog():
    '''
    记录ad-hoc模式日志
    '''

    def __init__(self, taskid):
        with open(r'%s/conf/taskdo.yml' % settings.BASE_DIR, encoding='utf-8') as file:
            self.status_conf = yaml.load(file)
        self.task_id = ''
        if taskid:
            self.task_id = int(taskid)
        else:
            return False
        self.map_id = self.status_conf['ansible_log']['adhoc_format']

    def record(self, statuid, input_con={}):
        if statuid not in self.map_id:
            return False
        timevalue = datetime.now()
        record_info = self.map_id[statuid] if self.map_id[statuid] else input_con
        content = {"taskid": self.task_id, "time": timevalue, "id": statuid, "desc": record_info}
        mongo_obj = Mongodb(collection='taskadhoclog')
        mongo_obj.insert(content)
        print("........................insert content", content)

    def getrecord(self):
        mongo_obj = Mongodb(collection='taskadhoclog')
        result = mongo_obj.filter(self.task_id)
        print("........................get result", result)
        if result:
            return result
