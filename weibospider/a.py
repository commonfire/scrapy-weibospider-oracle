# _*_ coding:utf-8 _*_
import re
from pyquery import PyQuery as pq
s = '''<div class="WB_text W_f14" node-type="feed_list_content" nick-name="李写意">
                            <a ignore="ignore" title="微博会员特权" href="http://vip.weibo.com/prividesc?priv=1107&amp;from=zdicon"><span class="W_icon_feedpin"><i class="W_icon icon_feedpin_lite" title="微博会员特权"></i>置顶</span></a>
                                                                我发表了新文章：好久没有写推荐了，主要是因为时间不够用。每天看看专业书，加加班，给自己做点健康的食物，时间哗啦哗啦就没有了。顺便啰嗦一句，大家不要每天光看小说，好的小说偶尔追一个半个的就足够了。剩下的时间还是要看看专业书的。<a target="_blank" render="ext" class="a_topic" extra-data="type=topic" href="http://huati.weibo.com/k/%E5%86%99%E6%84%8F%E6%AF%8F%E5%91%A8%E6%8E%A8?from=501">#写意每周推#</a> <a class="W_btn_b btn_22px W_btn_cardlink" suda-uatrack="key=tblog_card&amp;value=click_title:3922872835290799:1022-article:1022%3A1001593922871339623684" title="#写意每周推#一年即将结束，2015，珍重再见" href="http://t.cn/R4b600M" action-type="feed_list_url" target="_blank"><i class="W_ficon ficon_cd_link S_ficon">O</i><i class="W_vline S_line1"></i><em class="W_autocut S_link1">#写意每周推#一年即将结束，2015，珍重再见</em></a>                        </div><div class="WB_text W_f14" node-type="feed_list_content">
                                    呸，家长这种教育//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E5%BA%9C%E5%A4%A9%E7%9A%84%E5%BE%AE%E5%8D%9A?from=feed&amp;loc=at" usercard="name=府天的微博">@府天的微博</a>: 孩子偷窃，家长打孩子，于是孩子自杀，家长不反省自己，反而带了一大堆人跑超市去闹？就算超市可能是冤枉了孩子，你家长二话不说就在超市公然打骂孩子，这是教育还是把人往死路上推？说实在的，很可能家长当众那一巴掌才是孩子跳楼最大的诱因。市长挺倒霉的                        </div>'''
s2='''<div class="WB_text W_f14" node-type="feed_list_content" nick-name="沙漠种土豆">
                            <span class="W_icon_feedhot"><i class="W_icon icon_feedhot_lite" title="热门" exp-data="key=profile_weibo&amp;value=hotweibo&amp;src=http://rs.sinajs.cn/j.gif"></i>热门</span>
                                                                有点喷了，这些东西都是买的，又不是不花钱，这些东西其他城市的市民买不到吗？//<a target="_blank" render="ext" extra-data="type=atname" href="http://weibo.com/n/%E9%87%91%E8%9E%8D%E5%B0%8F%E5%8F%AE%E5%BD%93?from=feed&amp;loc=at" usercard="name=金融小叮当">@金融小叮当</a>:湖北的水，山西的煤，山东的菜，东北的粮食，俄罗斯的天然气，哪一样是北京的？//【那些被北京赶出去的孩子：坐在北京门槛上读书】  <a class="W_btn_b btn_22px W_btn_cardlink" title="那些被北京赶出去的孩子：坐在北京门槛上读书" href="http://t.cn/R4LOHID" action-type="feed_list_url" target="_blank"><i class="W_ficon ficon_cd_link S_ficon">O</i><i class="W_vline S_line1"></i><em class="W_autocut S_link1">那些被北京赶出去的孩子：坐在北京门槛上读书</em></a>         '''

dpq = pq(s)
dpq = dpq("div[node-type=feed_list_content]")
#if str(dpq("span")!=""):
#    print "nnnn"
