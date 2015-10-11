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

configure_logging
settings = get_project_settings()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks

def crawl():
    if sys.argv[2] == 'keyuser':
        yield runner.crawl('keyuser',keyword = sys.argv[1])
    elif sys.argv[2] == 'keyweibocontent':
        yield runner.crawl('keyweibocontent',uid = sys.argv[1])
    elif sys.argv[2] == 'weibocontent_userinfo':
        yield runner.crawl('weibocontent_userinfo',uid = sys.argv[1])
    elif sys.argv[2] == 'userinfo_list':
        yield runner.crawl('userinfo_list',uid_listformat = sys.argv[1])
    else:
        yield runner.crawl('userinfo',uid = sys.argv[1]) 
    reactor.stop()

crawl()
reactor.run()
