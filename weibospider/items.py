# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from  scrapy import Field,Item

class WeibospiderItem(Item):
    # define the fields for your item here like:
    uid = Field()            #微博用户uid
    content = Field()        #微博发表内容
    time = Field()           #微博发表时间
    atuser = Field()         #微博@用户（昵称）
    repostuser = Field()     #微博转发用户（昵称）
    followuidlist = Field()  #关注用户uid列表
    userinfo = Field()       #用户基本信息
    image_urls = Field()     #用户头像图片链接
    keyword_uid = Field()    #与关键词相关的用户uid
    keyword = Field()        #搜索的关键词
