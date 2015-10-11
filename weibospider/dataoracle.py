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
#            conn = cx_Oracle.connect(user='ZTQ',password='fnl12345678',dsn='10.108.144.99/orcl')
            conn = cx_Oracle.connect(user='bupt',password='bupt',dsn='10.108.147.143/orcl')
            print 'oracle_connection success!!' 
            return conn
        except cx_Oracle.Error,e:
            print "Oracle Error %d: %s" % (e.args[0],e.args[1])  

    def close_connection(self,conn,*cursor):
        '''关闭数据库连接'''
        for cur in cursor:
            cur.close()
        conn.close()
        print "oracle_connection close!!"

    def insert_operation(self,conn,sql):
        '''插入数据操作'''
        try:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()  #!!注意必须有此处的事务提交，否则插入操作不生效
            self.close_connection(conn,cur)
        except cx_Oracle.Error,e:
            print e.message  #raise e
    
    def update_operation(self,conn,sql):
        '''更新数据操作'''    
        self.insert_operation(conn,sql)

    def select_operation(self,conn,sql):
        '''从数据库中选择出数据'''
        cur = conn.cursor()
        cur.execute(sql)
        return cur
