from __future__ import absolute_import
from celery import shared_task
from backend.models import *
import scrapy
from scrapy.crawler import CrawlerProcess
from spiders.hotel_spider import HotelSpider


@shared_task
def crawl(url):
    process = CrawlerProcess()
    num = url[-12:-5]
    process.crawl(HotelSpider, START_URL=url, HOTEL_NUM=num)
    process.start()


@shared_task
def crawl_machine1(url):
    process = CrawlerProcess()
    num = url[-12:-5]
    process.crawl(HotelSpider, START_URL=url, HOTEL_NUM=num)
    process.start()


@shared_task
def crawl_machine2(url):
    process = CrawlerProcess()
    num = url[-12:-5]
    process.crawl(HotelSpider, START_URL=url, HOTEL_NUM=num)
    process.start()


@shared_task
def add(x, y):
    return x + y


@shared_task
def add_machine1(x, y):
    return x + y


@shared_task
def add_machine2(x, y):
    return x + y


'''

@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def addCrawlWebsite(url, desc):
    newCrawlWebsite = CrawlWebsite(url=url, desc=desc)
    newCrawlWebsite.save()


@shared_task
def addHotel(name, addr, desc, phone):
    newHotel = Hotel(name=name, addr=addr, desc=desc, phone=phone)
    newHotel.save()


@shared_task
def addRoomType(name, desc):
    newRoomType = RoomType(name=name, desc=desc)
    newRoomType.save()


@shared_task
def addCustomer(name, total_comment):
    newCustomer = Customer(name=name, total_comment=total_comment)
    newCustomer.save()


@shared_task
def addComment(customer, hotel, score, room_type, content, datetime):
    newComment = Comment(customer=customer, hotel=hotel, score=score,
                         room_type=room_type, content=content, datetime=datetime)
    newComment.save()
'''