#-*- coding:utf-8 -*-
import sys
import cx_Oracle

reload(sys)
sys.setdefaultencoding('utf-8')

class OracleStore:
    '''Oracle数据库连接与命令操作'''
    def get_connection(self):
        '''连接数据库'''
        try:
            conn = cx_Oracle.connect(user='ZTQ',password='fnl12345678',dsn='10.108.144.99/orcl')
            print 'oracle_connection success!!' 
            return conn
        except cx_Oracle.Error,e:
            print "Oracle Error %d: %s" % (e.args[0],e.args[1])  

    def close_connection(self,cursor,conn):
        '''关闭数据库连接'''
        cursor.close()
        conn.close()
        print "oracle_connection close!!"

    def insert_operation(self,conn,sql):
        '''插入数据操作'''
        cur = conn.cursor()
        cur.execute(sql)
        print 'insertion success!!'

    def select_operation(self,conn,sql):
        '''从数据库中选择出数据'''
        cur = conn.cursor()
        cur.execute(sql)
        return cur


#db=OracleStore()
#conn = db.get_connection()
#sql = '''insert into "t_user_keyword"("userID","keyword") values(1111,'hahh')'''
#sql = '''update "t_spider_state" set "searchstate"=1'''
#db.insert_operation(conn,sql)


