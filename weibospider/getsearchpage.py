#-*-coding: utf-8 -*-
import sys
from urllib import urlencode,quote

reload(sys)
sys.setdefaultencoding('utf-8')


class GetSearchpage:
    '''获取指定关键词搜索网页的url'''
    data = {
        'nodup':'1',
        'page':'',
    }

    def get_searchurl(self,keyword):
        encoded_keyword = quote(quote(keyword))        
        return encoded_keyword+'&'+urlencode(GetSearchpage.data)

#a = GetSearchpage()
#print a.get_searchurl('空闹')

