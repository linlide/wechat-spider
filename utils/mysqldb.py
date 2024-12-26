import pymysql
import logging

class MysqlDB:
    def __init__(self, ip='localhost', port=3306, db='', user='root', passwd='', charset='utf8mb4'):
        """初始化MySQL连接"""
        try:
            self.conn = pymysql.connect(
                host=ip,
                port=port,
                user=user,
                password=passwd,
                database=db,
                charset=charset
            )
            self.cursor = self.conn.cursor()
            logging.info("MySQL数据库连接成功")
        except Exception as e:
            logging.error(f"MySQL数据库连接失败: {e}")
            raise

    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        try:
            self.cursor.close()
            self.conn.close()
            logging.info("MySQL数据库连接已关闭")
        except:
            pass

    def add(self, sql, params=None):
        """插入数据"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"插入数据失败: {e}")
            logging.error(f"SQL语句: {sql}")
            logging.error(f"参数: {params}")
            self.conn.rollback()
            return False

    def delete(self, sql, params=None):
        """删除数据"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"删除数据失败: {e}")
            self.conn.rollback()
            return False

    def update(self, sql, params=None):
        """更新数据"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"更新数据失败: {e}")
            self.conn.rollback()
            return False

    def query(self, sql, params=None):
        """查询数据"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"查询数据失败: {e}")
            return None

    def query_one(self, sql, params=None):
        """查询单条数据"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"查询单条数据失败: {e}")
            return None

    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"执行SQL语句失败: {e}")
            self.conn.rollback()
            return False 