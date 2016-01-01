# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import logging
import cx_Oracle
import sys
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
import getinfo
import re
from dataoracle import OracleStore

#import logging

reload(sys)
sys.setdefaultencoding('utf8')

#logger = logging.getLogger(__name__)  

class WeibospiderPipeline(object):
    
    settings = get_project_settings()
    start_uid = settings['UID']
    weibocontent_timestamp = 0  #记录数据库中最新微博时间戳
    keyword_timestamp = 0       #记录数据库中最新关键词搜索结果时间戳

    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbargs = dict(
            user = settings['ORACLE_USER'],
            password = settings['ORACLE_PASSWD'],
            dsn = settings['ORACLE_DSN'],
        )
        dbpool = adbapi.ConnectionPool('cx_Oracle',**dbargs)
        return cls(dbpool)

    def open_spider(self,spider):
        #获取数据库中微博内容最新时间戳
        if spider.name in ('keyweibocontent','weibocontent_userinfo','weibocontent_danger','weibocontent_userinfo_intime'):
            db=OracleStore();conn = db.get_connection()
            sql = "select * from t_user_weibocontent where userID = '%s' order by publishTimeStamp desc" % str(spider.uid) 
            cursor = db.select_operation(conn,sql)
            count = cursor.fetchone()
            if not count:  #count为None，即数据库中没有该用户微博及时间戳的数据
                WeibospiderPipeline.weibocontent_timestamp = None
            else:
                WeibospiderPipeline.weibocontent_timestamp = count[6] #获取数据库中最新的时间戳（publishTimeStamp）字段 
            db.close_connection(conn,cursor)
        if spider.name == 'keyuser':
            db=OracleStore();conn = db.get_connection()
            sql = "select * from t_user_keyword where keyword = '%s' order by publishTimeStamp desc" % str(spider.keyword) 
            cursor = db.select_operation(conn,sql)
            count = cursor.fetchone()
            if not count:  #count为None，即数据库中没有该关键词搜索结果及时间戳的数据
                WeibospiderPipeline.keyword_timestamp = None
            else:
                WeibospiderPipeline.keyword_timestamp = count[4] #获取数据库中最新的时间戳（publishTimeStamp）字段 
            db.close_connection(conn,cursor)


    def process_item(self,item,spider):
        if spider.name == 'keyweibocontent':
            d = self.dbpool.runInteraction(self._keyweibocontent_insert,item,spider)  
        elif spider.name == 'weibocontent_danger':
            d = self.dbpool.runInteraction(self._weibocontent_danger_insert,item,spider)  
        elif spider.name == 'userfollow':
            d = self.dbpool.runInteraction(self._userfollow_insert,item,spider)  
        elif spider.name == 'userinfo' or spider.name == 'userinfo_list':     #'userphoto':
            d = self.dbpool.runInteraction(self._userinfo_insert,item,spider)  
        elif spider.name == 'keyuser':
            d = self.dbpool.runInteraction(self._keyuser_insert,item,spider)
        elif spider.name == 'userid_info_list':
            d = self.dbpool.runInteraction(self._userid_info_update,item,spider)
        else: 
            d = self.dbpool.runInteraction(self._weibocontent_userinfo_insert,item,spider)

        d.addErrback(self._handle_error,item,spider) 
        d.addBoth(lambda _:item)
        return d

    def _userfollow_insert(self,conn,item,spider): 
        if len(item['follow_uid_list']) and not len(item['follower_uid_list']):
            for i in range(len(item['follow_uid_list'])):
                conn.execute('''insert into t_user_follow(userID,followID) values(:1,:2)''',(str(item['uid']),item['follow_uid_list'][i]))
        
        if len(item['follower_uid_list']) and not len(item['follow_uid_list']):
            for i in range(len(item['follower_uid_list'])):
                conn.execute('''insert into t_user_follower(userID,followerID) values(:1,:2)''',(str(item['uid']),item['follower_uid_list'][i]))


    def _keyweibocontent_insert(self,conn,item,spider):
        #插入发表微博内容和时间
        self._weibocontent_item_insert(conn,item,'atuser')


    def _weibocontent_danger_insert(self,conn,item,spider):
        #爬取微博计算危险人物
        self._weibocontent_item_insert(conn,item,'origin')

    def _weibocontent_userinfo_insert(self,conn,item,spider):
        #插入用户个人基本信息及微博
        if 'userinfo' in item:   #判断item中是否有userinfo字段
            self._userinfo_insert(conn,item,spider)
        else:
            self._weibocontent_item_insert(conn,item,'atuser')


    def _userinfo_insert(self,conn,item,spider):
        #将微博用户个人信息插入数据库 
        if item['image_urls']:  #item['image_urls']不为None
            if 'png' not in item['image_urls']:
                imageurl = "images/userphoto/full/"+str(item['uid'])+".jpg"
                thumbnail_url = "images/userphoto/thumbs/small/"+str(item['uid'])+"_thumbnail.jpg" 
            else:
                tmp = item['image_urls']
                imageurl = "images/userphoto/full/"+tmp[tmp.rindex('/')+1:tmp.rindex('.')]+".jpg"
                thumbnail_url = "images/userphoto/thumbs/small/"+tmp[tmp.rindex('/')+1:tmp.rindex('.')]+"_thumbnail.jpg"
        else:
            imageurl = ''
            thumbnail_url = ''

        user_property = item['user_property'] 

        if user_property != 'icon_verify_co_v': #该账号为个人账号
            conn.execute('''insert into t_user_info(userID,userAlias,location,sex,blog,domain,brief,birthday,registertime,imageurl,thumbnailurl,property) values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)''',[str(item['uid']),item['userinfo']['昵称：'.decode('utf-8')],item['userinfo']['所在地：'.decode('utf-8')],item['userinfo']['性别：'.decode('utf-8')],item['userinfo']['博客：'.decode('utf-8')],item['userinfo'.decode('utf-8')]['个性域名：'.decode('utf-8')],item['userinfo']['简介：'.decode('utf-8')],item['userinfo']['生日：'.decode('utf-8')],item['userinfo']['注册时间：'.decode('utf-8')],imageurl,thumbnail_url,user_property])
        else:  #该账号为公众账号
            conn.execute('''insert into t_publicuser_info(userID,userAlias,contacts,phonenum,email,property) values(:1,:2,:3,:4,:5,:6)''',[str(item['uid']),item['userAlias_public'],item['userinfo']['联系人：'.decode('utf-8')],item['userinfo']['电话：'.decode('utf-8')],item['userinfo']['邮箱：'.decode('utf-8')],user_property])
        
        #conn.execute("update t_user_info set imagestate = 1 where userID = "+str(item['uid']))
        #conn.execute("update t_user_info set imageurl=:1,thumbnailurl=:2 where userID=:3",[imageurl,thumbnail_url,str(item['uid'])])

    def _userid_info_update(self,conn,item,spider):
        print "!!!!!",item['atuser_nickname'] 
        print "!!!!!",item['atuser_uid'] 

    def _keyuser_insert(self,conn,item,spider):
        #将关键词相关用户uid插入数据库
        if not WeibospiderPipeline.keyword_timestamp: #此时值为None，即数据库中没有该关键词搜索结果及时间戳
            for i in range(len(item['keyword_uid'])):
                conn.execute('''insert into t_user_keyword(userID,keyword,userAlias,publishTime,publishTimeStamp) values(:1,:2,:3,to_date(:4,'YYYY-MM-DD HH24:MI'),:5)''',[item['keyword_uid'][i],str(item['keyword']),item['keyword_alias'][i],item['keyword_time'][i],item['keyword_timestamp'][i]])
        else:
            for i in range(len(item['keyword_uid'])):
                if item['keyword_timestamp'][i] > WeibospiderPipeline.keyword_timestamp:
                    conn.execute('''insert into t_user_keyword(userID,keyword,userAlias,publishTime,publishTimeStamp) values(:1,:2,:3,to_date(:4,'YYYY-MM-DD HH24:MI'),:5)''',[item['keyword_uid'][i],str(item['keyword']),item['keyword_alias'][i],item['keyword_time'][i],item['keyword_timestamp'][i]])


    def _handle_error(self,failure,item,spider):
        logging.error(failure)

        
    def _weibocontent_item_insert(self,conn,item,type):
        if not WeibospiderPipeline.weibocontent_timestamp: #此时值为None，即数据库中没有该用户微博及时间戳
            for i in range(len(item['content'])):
                if "'" in item['content'][i]:
                    content_tmp = item['content'][i].replace("'","\'")
                    conn.execute('''insert into t_user_weibocontent(userID,content,publishTime,repostuser,id,publishTimeStamp) values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,(select nvl(MAX(id),0)+1 as "id" from t_user_weibocontent),:5)''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['timestamp'][i]])
                else:
                    conn.execute('''insert into t_user_weibocontent(userID,content,publishTime,repostuser,id,publishTimeStamp) values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,(select nvl(MAX(id),0)+1 as "id" from t_user_weibocontent),:5)''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['timestamp'][i]])
                if type == 'atuser':
                    if item['atuser_nickname_list'][i] != {}:  #插入@用户昵称等信息
                        for atuser in item['atuser_nickname_list'][i]:
                            conn.execute('''insert into t_user_weibocontent_atuser(userID,publishTime,atuser,publishTimeStamp) values(:1,to_date(:2,'YYYY-MM-DD HH24:MI'),:3,:4)''',[str(item['uid']),item['time'][i],atuser,item['timestamp'][i]])
        
        else:
            for i in range(len(item['content'])):
                if item['timestamp'][i] > WeibospiderPipeline.weibocontent_timestamp: #插入大于当前时间戳，即更新后的微博内容
                    if "'" in item['content'][i]:
                        content_tmp = item['content'][i].replace("'","\'")
                        conn.execute('''insert into t_user_weibocontent(userID,content,publishTime,repostuser,id,publishTimeStamp) values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,(select nvl(MAX(id),0)+1 as "id" from t_user_weibocontent),:5)''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['timestamp'][i]])
                    else:
                        conn.execute('''insert into t_user_weibocontent(userID,content,publishTime,repostuser,id,publishTimeStamp) values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,(select nvl(MAX(id),0)+1 as "id" from t_user_weibocontent),:5)''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['timestamp'][i]])
                    if type == 'atuser':
                        if item['atuser_nickname_list'][i] != {}:  #插入@用户昵称等信息
                            for atuser in item['atuser_nickname_list'][i]:
                                conn.execute('''insert into t_user_weibocontent_atuser(userID,publishTime,atuser,publishTimeStamp) values(:1,to_date(:2,'YYYY-MM-DD HH24:MI'),:3,:4)''',[str(item['uid']),item['time'][i],atuser,item['timestamp'][i]])

        
