#-*-coding:utf-8-*-
import sys
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
reload(sys)
sys.setdefaultencoding('utf-8')
try:    
    configure_logging
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
except Exception,e:
    print e
    
@defer.inlineCallbacks

def crawl():
    if len(sys.argv) == 3:
        if sys.argv[2] == 'keyuser':  #根据关键词搜索相关用户
            yield runner.crawl('keyuser',keyword=sys.argv[1])
        elif sys.argv[2] == 'keyweibocontent':  #查询关键词用户微博内容
            yield runner.crawl('keyweibocontent',uid = sys.argv[1])
        elif sys.argv[2] == 'weibocontent_userinfo':  #查询用户微博内容及基本信息
            yield runner.crawl('weibocontent_userinfo',uid = sys.argv[1])
        elif sys.argv[2] == 'userinfo_list':  #根据uidlist查询用户个人信息
            yield runner.crawl('userinfo_list',uid_listformat = sys.argv[1])
        else:
            yield runner.crawl('userinfo',uid = sys.argv[1]) # 查询用户个人信息
    else:
        if sys.argv[3] == 'weibocontent_userinfo_intime':
            yield runner.crawl('weibocontent_userinfo_intime',uid = sys.argv[1],per_page_num = sys.argv[2])

    reactor.stop()

try:
    crawl()
    reactor.run()
except Exception,e:
    print e
