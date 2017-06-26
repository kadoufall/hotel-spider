#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request

# from hotel.items import HotelItem
from backend.models import *

import requests
import traceback

import time
import os


class HotelSpider(Spider):
    # log.start("log",loglevel='INFO')
    name = "hotel"

    log = "hotel.txt"
    commentLog = "comment.txt"
    elong_log = "elong.txt"

    download_delay = 1
    allowed_domains = [r"http://hotels.ctrip.com/hotel/2906601.html",
                       r"http://hotels.ctrip.com/hotel/4678450.html",
                       r"http://hotels.ctrip.com/hotel/1357524.html"]
    start_urls = [
        #        r"http://hotels.ctrip.com/hotel/2906601.html",
        #        r"http://hotels.ctrip.com/hotel/4678450.html",
        r"http://hotels.ctrip.com/hotel/1357524.html",
    ]
    hotel_num = "1357524"

    dianping_root = r"http://hotels.ctrip.com/hotel/dianping/"
    dianping = r"http://hotels.ctrip.com/hotel/dianping/%s.html" % hotel_num

    def __init__(self, START_URL=None, *args, **kwargs):
        super(HotelSpider, self).__init__(*args, **kwargs)
        if START_URL.find("ctrip")!=-1:   # 携程
            num = START_URL[-12:-5]
            self.start_urls = [r"http://hotels.ctrip.com/hotel/%s.html" % num]
            self.hotel_num = num
            self.dianping = r"http://hotels.ctrip.com/hotel/dianping/%s.html" % num
            self.log = r"hotel-%s.txt" % num
            self.commentLog = r"comment-%s.txt" % num
        elif START_URL.find("elong")!=-1:     # 艺龙
            pass
            
    # default crawl function
    def parse_elong(self, response):
        browser = webdriver.Firefox()
        browser.get(response.url)
        browser.find_element_by_xpath("//a[@href='#review']").click()

        sel = Selector(text=browser.page_source)
        comment_list = sel.xpath(
            '//p[@class="dcomt_con_txt"]/text()').extract()

        total_page = 47
        content_list = []
        for i in range(2, total_page):
            url = r"http://hotel.elong.com/ajax/detail/gethotelreviews?hotelId=90936440&recommendedType=0&pageIndex=%s&mainTagId=0&subTagId=0" % i
            r = requests.get(url)
            contents = r.json()['contents']
            for content in contents:
                content_list.append(content["content"])
            time.sleep(1)

        with open(self.elong_log, 'w') as f:
            for c in content_list:
                f.write(c)
                f.write("\r\n")

        browser.quit()

    def parse(self, response):
        '''Hotel.objects.all().delete()
        RoomType.objects.all().delete()
        Customer.objects.all().delete()
        Comment.objects.all().delete()
        CrawlWebsite.objects.all().delete()'''
        # 点击房型列表按钮，获取房型列表
        browser = webdriver.Firefox()
        browser.get(response.url)
        browser.find_element_by_xpath(
            "//div[@class='hotel_tabs_box']/ul/li[1]/a").click()
        response = Selector(text=browser.page_source)
        # browser.find_element_by_xpath()

        '''tempaaa = response.xpath('//div[@class="hotel_tabs_box"]')
        print "tempaaa", len(tempaaa)
        tempbbb = tempaaa.xpath("./ul/li[1]/a")
        print "tempbbb", len(tempbbb)'''

        title = response.xpath(
            '//h2[contains(@class, "cn_n")]/text()').extract()
        city = response.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_commonHead_lnkCity"]/text()').extract()
        location = response.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_commonHead_lnkLocation"]/text()').extract()
        address = response.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_commonHead_lbAddress"]/text()').extract()
        road = response.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_commonHead_lnkRoadCross"]/text()').extract()
        zone = response.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_commonHead_lnkMapZone2"]/text()').extract()

        title = title[0] if title else ""
        city = city[0] if city else ""
        location = location[0] if location else ""
        address = address[0] if address else ""
        road = road[0] if road else ""
        zone = zone[0] if zone else ""

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 存入数据库
        # 如果正在爬取则取消当前任务
        newCrawlWebsite = CrawlWebsite.objects.get_or_create(url=self.start_urls[0])
        
        if newCrawlWebsite[1]==False and newCrawlWebsite[0].lock:
            browser.quit()
            os._exit()

        newCrawlWebsite[0].desc = title
        newCrawlWebsite[0].lock = True
        newCrawlWebsite[0].done = False
        newCrawlWebsite[0].lastest_time = localtime
        newCrawlWebsite[0].save()

        '''print "title:", title
        #CrawlWebsite.objects.all().delete()
        try:
            resu = CrawlWebsite.objects.filter(desc=title)
            print "sqlite_title：", resu
        except:
            traceback.print_exc()
        '''

        # score
        commnet_score = response.xpath(
            '//a[@class="commnet_score"]/@title').extract()[0]

        # info
        l = response.xpath('//div[@id="htlDes"]')[0]
        info_head = l.xpath('p/text()')[0].extract().strip()
        info_middle = l.xpath(
            '//span[@id="J_realContact"]/@data-real')[0].extract().strip().split("<a target")[0]
        info_tail = l.xpath(
            '//span[@id="ctl00_MainContentPlaceHolder_hotelDetailInfo_lbDesc"]/text()')[0].extract().strip()

        # facilities
        sel = response.xpath('//div[@id="J_htl_facilities"]')[0]
        uls = sel.xpath('.//ul')

        facilities = []

        for ul in uls:
            lis = ul.xpath('./li[@class=""]')
            t = []
            for li in lis:
                t.append(li.xpath('./@title')[0].extract())

            for tt in t:
                facilities.append(tt)
                print "tt", tt

        # tags
        sel_tags = response.xpath('//div[@class="special_label"]')[0]
        cons = sel_tags.xpath('./i')

        print "len.cons:", len(cons)
        tags = []
        for con in cons:
            tags.append(con.xpath('text()')[0].extract().strip())

        '''for tag in tags:
            print "tag:", tag'''
        # policy
        sel = response.xpath('//table[@class="detail_extracontent"]')[0]
        trs = sel.xpath('./tbody/tr')

        policy = {}

        for tr in trs:
            th = tr.xpath('./th//text()')[0].extract()
            td = tr.xpath('./td//text()')[0].extract()
            policy[th] = td.strip()

        '''for key, val in policy.iteritems():
            print(u"{0}: {1}".format(key, val))'''

        new_desc = info_head + "\r\n" + info_middle + "\r\n" + info_tail
        # print "new_desc", new_desc

        temp_policy = []
        for key, value in policy.items():
            # print "key, value:", key, value
            temp_policy.append(key)
            temp_policy.append(value)

        # data to save
        new_policy = " ".join(temp_policy)
        new_facilities = " ".join(facilities)
        new_tags = " ".join(tags)
        new_traffic = city + " " + location + " " + address + " " + road + " " + zone
        # save hotel information
        newHotel = Hotel(name=title, addr=address, desc=new_desc, policy=new_policy, facilities=new_facilities,
                         traffic=new_traffic, score=commnet_score, tags=new_tags)
        newHotel.save()

        # save the room information
        # room_type

        room_table = response.xpath('//table[@id="J_RoomListTbl"]')
        print "room_table", len(room_table)
        rooms = room_table.xpath(
            './tbody/tr[@class=""]/td/a[starts-with(@class,"room")]')
        print "rooms", len(rooms)
        this_hotel = Hotel.objects.filter(name=title)[0]
        for room in rooms:
            room_name = room.xpath('text()')[0].extract().strip()
            newRoomType = RoomType(name=room_name, hotel=this_hotel)
            newRoomType.save()
            print "room_name ", room_name

        '''sel_rooms = response.xpath('//ul[@class="searchresult_caplist"]')
        for room in sel_rooms:
            room_desc = []
            room_lis = room.xpath('./li')
            for li in room_lis:
                room_desc.append(li.xpath('text()')[0].extract().strip())

            new_room_desc = " ".join(room_desc)
            newRoomType = RoomType(name=room_name,desc=new_room_desc)

        '''

        # parse user's information

        self.parse_comments(self.dianping, browser, title)

        # 完成爬取
        newCrawlWebsite[0].lock = False
        newCrawlWebsite[0].done = True
        newCrawlWebsite[0].save()

        '''
        with open(self.log, 'w') as f:
            f.write(title)
            f.write(city)
            f.write(location)
            f.write(address)
            f.write(road)
            f.write(zone)
            f.write("\r\n")
            f.write(commnet_score)
            f.write("\r\n")
            f.write(info_head)
            f.write(info_middle)
            f.write(info_tail)
            f.write("\r\n")

            for facility in facilities:
                f.write(" ".join(facility))

            f.write("\r\n")

            for key, val in policy.iteritems():
                f.write(u"{0}: {1}".format(key,val))

            f.write("\r\n")
            f.write("\r\n")
            f.write("\r\n")

        '''

    def parse_comments(self, url, browser, hotel_name):
        ret = []
        print "parse comments here!"
        f = open(self.commentLog, 'w')
        f.write("\t".join(
            ["context", "user_name", "level", "comment", "commented", "imgs", "purpose",
                "checkin_date", "room", "publish_date", "data_voted", "pos", "equipment",
                "service", "health", "score"]
        )
        )
        f.write("\r\n")
        f.close()
        print "parse comments here!00000000000000000"
        '''browser = webdriver.Firefox()'''

        first_page_url = r"%s%s_p1t0.html" % (
            self.dianping_root, self.hotel_num)
        browser.get(first_page_url)
        sel = Selector(text=browser.page_source)

        page_list = sel.xpath('//div[@class="c_page_list layoutfix"]/a')
        int_a_nums = len(page_list)
        print "a_nums", int_a_nums
        the_total = page_list[int_a_nums - 1]
        total = int(the_total.xpath('@value').extract()[0])
        print "total_pages", total

        # total = 54
        # total = 167
        # total = 73
        # total = 3

        links = []
        # "http://hotels.ctrip.com/hotel/dianping/2906601_p1t0.html"
        for page in range(1, total + 1):
            links.append(r"%s%s_p%st0.html" %
                         (self.dianping_root, self.hotel_num, page))
        print "here1111111111111111111111"
        for link in links:
            browser.get(link)
            time.sleep(2)

            sel = Selector(text=browser.page_source)
            time.sleep(1)

            comment_objs = sel.xpath(
                '//div[@class="comment_block J_asyncCmt"]')
            f = open("comments.log", 'a')

            print("=====%s=====" % link)
            print("=====%s=====" % len(comment_objs))

            try:
                print "try in:"
                for comment_obj in comment_objs:
                    context = comment_obj.xpath(
                        './/div[@class="J_commentDetail"]/text()').extract()[0]
                    user_name = comment_obj.xpath(
                        './/div[contains(@class, "user_info")]/p[@class="name"]/span//text()').extract()[0]
                    level = comment_obj.xpath(
                        './/div[contains(@class, "user_info")]/p[contains(@class, "level")]/@class').extract()[0]
                    package = comment_obj.xpath(
                        './/div[contains(@class, "user_info")]/p[contains(@class, "num")]//text()').extract()
                    comment = commented = imgs = "0"
                    for p in package:
                        if p.find(u"点评总数") != -1:
                            comment = p.split(u"点评总数")[1].strip()
                        if p.find(u"被点有用") != -1:
                            commented = p.split(u"被点有用")[1].strip()
                        if p.find(u"上传图片") != -1:
                            imgs = p.split(u"上传图片")[1].strip()
                    # 住房目的
                    purpose = comment_obj.xpath(
                        './/span[contains(@class, "type")]//text()').extract()[0]
                    checkin_date = comment_obj.xpath(
                        './/span[contains(@class, "date")]//text()').extract()[0]
                    room = comment_obj.xpath(
                        './/a[contains(@class, "room J_baseroom_link")]//text()').extract()[0]
                    publish_date = comment_obj.xpath(
                        './/p[contains(@class, "comment_bar_info")]//text()').extract()[0].replace(u"发表于", "")
                    data_voted = comment_obj.xpath(
                        './/a[contains(@class, "useful")]/@data-voted').extract()[0]
                    score = comment_obj.xpath(
                        './/span[contains(@class, "score")]/span//text()').extract()[0]
                    package = comment_obj.xpath(
                        './/span[contains(@class, "small_c")]/@data-value').extract()[0].split(',')

                    # position equipment service health
                    tmp = []

                    for p in package:
                        k, v = p.split(":")
                        tmp.append(v)

                    f.write("\t".join([context.replace("\n", "").replace("\r\n", ""),
                                       user_name.replace("\n", "").replace(
                                           "\r\n", ""), level, comment, commented, imgs, purpose,
                                       checkin_date, room, publish_date, data_voted, tmp[0], tmp[1],
                                       tmp[2], tmp[3], score]))
                    f.write("\r\n")
                    # save customer information
                    new_user_name = user_name.replace(
                        "\n", "").replace("\r\n", "")
                    print "save user informations!"
                    newCustomer = Customer(name=new_user_name, user_level=level, total_comment=int(comment),
                                           useful_num=int(commented), upload_img_num=int(imgs))
                    newCustomer.save()

                    #

                    new_context = context.replace("\n", "").replace("\r\n", "")

                    temp_customer_id = Customer.objects.filter(
                        name=new_user_name)[0]
                    customer_id = temp_customer_id.id
                    print "customer_id", customer_id

                    temp_hotel_id = Hotel.objects.filter(name=hotel_name)[0]
                    hotel_id = temp_hotel_id.id
                    print "hotel_id", hotel_id

                    temp_roomtype_id = RoomType.objects.filter(name=room)

                    temp_room_instan = []
                    if len(temp_roomtype_id) == 0:
                        this_hotel = Hotel.objects.filter(name=hotel_name)[0]
                        newRoomType = RoomType(name=room, hotel=this_hotel)
                        newRoomType.save()
                        temp_roomtype_id = RoomType.objects.filter(name=room)[
                            0]
                    else:
                        temp_roomtype_id = temp_roomtype_id[0]

                    newComment = Comment(customer=temp_customer_id, hotel=temp_hotel_id, room_type=temp_roomtype_id,
                                         score_position=float(tmp[0]), score_equipment=float(tmp[1]),
                                         score_service=float(tmp[2]), score_health=float(tmp[3]), score=float(score),
                                         purpose=purpose, content=context, datetime=checkin_date)
                    newComment.save()

            except:
                traceback.print_exc()
                print "exception happened!"
            finally:
                f.close()

            time.sleep(5)

        browser.quit()
