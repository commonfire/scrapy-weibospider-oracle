# _*_ coding: utf-8 _*_
from analyzer import Analyzer
import re
from pyquery import PyQuery as pq
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
analyzer = Analyzer()
#p1 = re.compile('<div.*?>(.*?)\s?//',re.S)
#p1 = re.compile('(<a.*?</a>)\s?//',re.S) 
p1=re.compile('(.*?)\s?//\s?<a',re.S)
text = '''<div class="WB_text W_f14" node-type="feed_list_content">
                                    再过500年，就是白素贞吧//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E9%9D%92%E5%9F%8E%E5%B1%B1%E5%93%92%E8%8A%B1%E7%88%B7?from=feed&amp;loc=at" usercard="name=青城山哒花爷">@青城山哒花爷</a>: //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%A1%91%E5%90%9B%E9%98%BF%E8%8E%AB?from=feed&amp;loc=at" usercard="name=桑君阿莫">@桑君阿莫</a>: //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E4%B9%9D%E9%9C%84%E5%88%98%E5%A5%95%E5%90%9B%E7%94%9C%E5%BF%83%E7%B3%95_%E8%B0%A2%E7%8E%89%E5%88%80%E7%88%B8%E7%B3%96?from=feed&amp;loc=at" usercard="name=九霄刘奕君甜心糕_谢玉刀爸糖">@九霄刘奕君甜心糕_谢玉刀爸糖</a>: 啊啊啊啊好可爱！！！啊啊啊啊！！！奶油冰淇淋<img render="ext" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/bmdaku_org.gif" title="[bm大哭]" alt="[bm大哭]" type="face" style="visibility: visible;"><img render="ext" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/bmdaku_org.gif" title="[bm大哭]" alt="[bm大哭]" type="face" style="visibility: visible;"><img render="ext" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/dc/bmdaku_org.gif" title="[bm大哭]" alt="[bm大哭]" type="face" style="visibility: visible;"><a target="_blank" render="ext" class="a_topic" extra-data="type=topic" href="http://huati.weibo.com/k/%E9%A6%96%E9%A1%B5%E5%AE%B3%E6%80%95%E8%9B%87%E7%9A%84%E5%8D%83%E4%B8%87%E4%B8%8D%E8%A6%81%E7%82%B9%E5%8D%A1?from=501">#首页害怕蛇的千万不要点卡#</a>//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E8%89%AF%E4%B9%9F%E5%9C%A8%E5%85%A8%E6%88%90F%E4%B9%8B%E6%97%B6%E8%AF%B4?from=feed&amp;loc=at" usercard="name=良也在全成F之时说">@良也在全成F之时说</a>: 啊想吃冰淇淋。。好可爱 是真的好可爱^q^                        </div>'''

text2= '''<div class="WB_text W_f14" node-type="feed_list_content">
                                    repost test!!<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E7%A7%92%E6%8B%8D?from=feed&amp;loc=at" usercard="name=秒拍">@秒拍</a> <a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%8E%A6%E9%97%A8%E6%A0%A1%E5%9B%AD?from=feed&amp;loc=at" usercard="name=厦门校园">@厦门校园</a> //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E4%B8%9C%E5%93%A5byr?from=feed&amp;loc=at" usercard="name=东哥byr">@东哥byr</a>: 哈哈哈转发测试<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E4%B8%9C%E5%93%A5byr?from=feed&amp;loc=at" usercard="name=东哥byr">@东哥byr</a>//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E4%B8%9C%E5%93%A5byr?from=feed&amp;loc=at" usercard="name=东哥byr">@东哥byr</a>:哈哈哈//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E4%B8%9C%E5%93%A5byr?from=feed&amp;loc=at" usercard="name=东哥byr">@东哥byr</a>: //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%8C%97%E9%82%AE%E5%88%98%E5%86%9B?from=feed&amp;loc=at" usercard="name=北邮刘军">@北邮刘军</a>:很多人都在用正则表达式 //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%98%8E%E9%A3%8EAndy?from=feed&amp;loc=at" usercard="name=明风Andy">@明风Andy</a>: <a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%88%91%E7%9A%84%E5%8D%B0%E8%B1%A1%E7%AC%94%E8%AE%B0?from=feed&amp;loc=at" usercard="name=我的印象笔记">@我的印象笔记</a>                        </div>'''

#total_pq = text_pq('div[node-type=feed_list_content]')
text = '''<div class="WB_text W_f14" node-type="feed_list_content">
                                    ttttttt<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%B1%9F%E5%AE%81%E5%85%AC%E5%AE%89%E5%9C%A8%E7%BA%BF?from=feed&amp;loc=at" usercard="name=江宁公安在线">@江宁公安在线</a> //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%B1%9F%E6%B9%96%E5%A4%AA%E5%A6%96%E7%94%9F?from=feed&amp;loc=at" usercard="name=江湖太妖生">@江湖太妖生</a>:卧槽，这么恶心的家伙为什么还活着！//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%A5%BD%E8%8C%B6%E8%B4%AA%E9%A6%99%E5%8F%88%E6%81%8B%E8%8A%B1?from=feed&amp;loc=at" usercard="name=好茶贪香又恋花">@好茶贪香又恋花</a>: 这种畜生没人管么？！<img render="ext" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7c/angrya_org.gif" title="[怒]" alt="[怒]" type="face" style="visibility: visible;"><img render="ext" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/7c/angrya_org.gif" title="[怒]" alt="[怒]" type="face" style="visibility: visible;">//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E6%B9%BE%E6%B9%BE%E6%98%AF%E5%B0%8F%E8%80%81%E8%99%8E?from=feed&amp;loc=at" usercard="name=湾湾是小老虎">@湾湾是小老虎</a>: //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%90%83%E8%A5%BF%E7%93%9C%E7%9A%84%E5%A4%8F%E5%A4%8F%E5%A4%8F%E5%AF%BB?from=feed&amp;loc=at" usercard="name=吃西瓜的夏夏夏寻">@吃西瓜的夏夏夏寻</a>:求人肉//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E9%9B%A8%E8%90%BD%E5%9B%9B%E6%9C%88?from=feed&amp;loc=at" usercard="name=雨落四月">@雨落四月</a>:好恶心……求人肉                        </div>'''


text='''<div class="WB_text W_f14" node-type="feed_list_content">
                                     //<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%A4%A9%E8%93%9D%E5%8F%B6%E6%96%91%E6%96%93?from=feed&amp;loc=at" usercard="name=天蓝叶斑斓">@天蓝叶斑斓</a>:转发微博                        </div>'''

text = unicode(text)
total_pq = pq(text)
d = total_pq('div[node-type=feed_list_content]')
#analyzer.get_content(total_pq)


match = p1.search(d.html())
if match:
    print "yes"
    #if match.group(1).strip() == "":
    #    print "null"
    data_pq = pq(match.group(1))
    #print data_pq('a').text()
    #for i,item in  enumerate(list(data_pq.contents())):
    #    print str(i)+str(item)
    #content = analyzer.get_content_src(data_pq) 
    #print content
else:
    print "no"

