import uuid
import lxml.html
from datetime import datetime
from random import random
from time import sleep
from urllib import request
from django.db import transaction
from django.core.files.base import ContentFile

from .models import Raw, PhotoRaw, Photo


class NotDoneYetError(Exception):
    pass


class Grabber():

    def __init__(self, completeon):
        self.completeon = completeon
        self.base_url = "http://auction.spb.ru"

    def run(self):
        start_time = datetime.now()
        print('Started at', start_time.strftime('%Y-%m-%d %H:%M'))

        auction_url = self.auction_category_url()
        coin_urls = self.get_coin_list(auction_url)

        with transaction.atomic():
            self.completeon.status = 'p'
            self.completeon.total = len(coin_urls)
            self.completeon.processed = 0
            self.completeon.save()

        for url in coin_urls[5:8]:
            try:
                self.get_coin(url)
            except Exception as e:
                self.completeon.status = 'f'
                self.completeon.save()
                raise e
            else:
                self.completeon.processed += 1
                self.completeon.save()

        self.completeon.status = 'd'
        self.completeon.save()

        done_time = datetime.now()
        print('Done at', done_time.strftime('%Y-%m-%d %H:%M'))
        print('Took:', done_time - start_time)

    def auction_url(self):
        return "%s/?auctID=%d" % (
            self.base_url, self.completeon.auction.number)

    def auction_category_url(self):
        return self.auction_url() + "&catID=%d" % (self.completeon.category.id)

    def get_page(self, url):
        print(url)
        sleep(random() * 1)
        with request.urlopen(url) as c:
            return c.read().decode('windows-1251', 'ignore')

    def get_image(self, url):
        with request.urlopen(url) as c:
            content = c.read()
            return content

    def get_coin_list(self, auction_url):
        coin_urls = []

        content = self.get_page(auction_url)
        html = lxml.html.fromstring(content)
        table = html.cssselect('body > table > tr')[2]
        table = table.cssselect('td')[1]
        table = table.cssselect('table > tr')[1]
        table.cssselect('td > table')[0].drop_tree()
        links = table.cssselect('a')
        coin_urls += self.parse_list(content)
        for link in links:
            url = link.attrib['href']
            if self.base_url not in url:
                url = self.base_url + url
            content = self.get_page(url)
            coin_urls += self.parse_list(content)

        return coin_urls

    def get_coin(self, url):
        content = self.get_page(url)
        html = lxml.html.fromstring(content)
        table = html.cssselect('body > table > tr')[2]
        table = table.cssselect('td')[1]
        table = table.cssselect('table > tr > td')[0]
        if table.text_content().find("Торги по лоту завершились") < 0:
            raise NotDoneYetError()

        if self.completeon.auction.date is None:
            content = table.cssselect('b')[0].text_content()
            # Convert '12:00:00 05-12-2007' to '05-12-2007'
            date = datetime.strptime(content.split()[1], '%d-%m-%Y')
            self.completeon.auction.date = date.strftime('%Y-%m-%d')
            self.completeon.auction.url = self.auction_url()
            self.completeon.auction.save()

        with transaction.atomic():
            part = lxml.html.tostring(table, encoding='unicode')
            raw = Raw.objects.create(url=url, html=part,
                                     auction=self.completeon.auction,
                                     category=self.completeon.category)
            links = table.cssselect('a')
            for num, link in enumerate(links):
                url = link.attrib['href']
                if self.base_url not in url:
                    url = self.base_url + url

                photo = Photo(url=url, position=num)
                img_data = ContentFile(self.get_image(url))
                file = str(uuid.uuid4()) + '.jpg'
                photo.file.save(file, img_data)

                PhotoRaw.objects.create(raw=raw, photo=photo)

    def parse_list(self, content):
        coin_urls = []
        html = lxml.html.fromstring(content)
        table = html.cssselect('body > table > tr')[2]
        table = table.cssselect('td')[1]
        table = table.cssselect('table > tr')[1]
        table = table.cssselect('td > table > tr')
        for row in table[2:]:
            link = row.cssselect('td > a')[0]
            url = link.attrib['href']
            if self.base_url not in url:
                url = self.base_url + url
            coin_urls.append(url)

        return coin_urls
