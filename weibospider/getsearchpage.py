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
#print quote(str('\xe8\x88\xaa\xe5\xa4\xa7\xe4\xb8\x9c\xe5\x8c\x97\xe7\x8e\x8b'))
#print '\xe8\x88\xaa\xe5\xa4\xa7\xe4\xb8\x9c\xe5\x8c\x97\xe7\x8e\x8b'

