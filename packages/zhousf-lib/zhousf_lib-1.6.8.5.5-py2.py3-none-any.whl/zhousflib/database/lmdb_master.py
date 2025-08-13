# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: lmdb (Lightning Memory-Mapped Database) 快如闪电的内存映射数据库
# 支持多进程
"""
pip install lmdb

[question]
MDB_MAP_FULL: Environment mapsize limit reached
[solution]
提升map_size或定时删除历史数据

[question]
lmdb.PanicError: mdb_txn_begin: MDB_PANIC: Update of meta page failed or environment had fatal error

"""
from pathlib import Path

import pickle
import lmdb

"""
实例化数据库
db = LMDB(Path(__file__).parent)
插入数据
db.insert("student", {"a": 99, "b": 95})
删除数据
db.delete("student")
修改数据
db.update("student", {"a": 98, "b": 100})
查询数据
print(db.query("student"))
显示所有数据
db.display()
"""


class LMDB(object):

    def __init__(self, db_dir: Path, map_size=int(1e9)):
        """
        初始化
        :param db_dir: 文件目录
        :param map_size: 1e9 ≈ 1GB;
                         1e10 ≈ 10GB;
                         1e11 ≈ 100GB(最大值)
        """
        self.env = self.initialize(db_dir, map_size)

    @staticmethod
    def initialize(db_dir: Path, map_size=int(1e9)):
        return lmdb.open(path=str(db_dir), map_size=map_size)

    def insert(self, key: str, value):
        """
        插入数据
        :param key:
        :param value:
        :return:
        """
        txn = self.env.begin(write=True)
        txn.put(str(key).encode(), pickle.dumps(value))
        txn.commit()

    def delete(self, key: str):
        """
        删除
        :param key:
        :return:
        """
        txn = self.env.begin(write=True)
        txn.delete(str(key).encode())
        txn.commit()

    def update(self, key: str, value):
        """
        更新
        :param key:
        :param value:
        :return:
        """
        self.insert(key, value)

    def query(self, key: str):
        """
        查询
        :param key:
        :return:
        """
        txn = self.env.begin()
        res = txn.get(str(key).encode())
        return None if res is None else pickle.loads(res)

    def query_all(self):
        """
        for k, v in db.query_all().items():
            print(k, v)
        """
        txn = self.env.begin()
        cur = txn.cursor()
        result = {}
        for key, value in cur:
            result[bytes(key).decode()] = pickle.loads(value)
        return result

    def display(self):
        """
        显示所有数据
        :return:
        """
        txn = self.env.begin()
        cur = txn.cursor()
        for key, value in cur:
            print(bytes(key).decode(), pickle.loads(value))

    def clear_all(self):
        """
        删除所有数据
        :return:
        """
        txn = self.env.begin(write=True)
        cur = txn.cursor()
        for key, value in cur:
            print(bytes(key).decode(), pickle.loads(value))
            txn.delete(str(key).encode())
        txn.commit()

    def close(self):
        self.env.close()

