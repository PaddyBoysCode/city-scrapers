# -*- coding: utf-8 -*-
import scrapy
import re
import urllib.parse
from datetime import datetime
from city_scrapers.spider import Spider


class Det_schoolsSpider(Spider):
    name = 'det_schools'
    agency_id = 'Detroit Public Schools'
    timezone ='America/Detroit'
    allowed_domains = ['detroitk12.org']
    start_urls = ['http://detroitk12.org/board/meetings/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        names = response.xpath('//main/h3/a/text()').extract()
        calendar_links = response.xpath('//main/h3/a/@href').extract()

        times = response.xpath('//main/h3/following-sibling::text()[1]').extract()
        times = map(lambda x: x.strip(), times)

        addresses = response.xpath('//main/h3/following-sibling::span[@class="address"]/text()').extract()

        items = zip(names, calendar_links, times, addresses)

        for item in items:
            startDate = self._parse_start(item[2])
            endDate      = self._parse_end(item[2])
            data = {
                '_type': 'event',
                'id': self._parse_id(item[1]),
                'name': item[0],
                'event_description': item[0],
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'council': self._parse_classification(item),
                'start': {
                    'date' :  startDate.date(),
                    'time' :  startDate.time(),
                    'note' :  ''
                },
                'end' : {
                    'date':  endDate.date(),
                    'time':  endDate.time(),
                    'note':  ''
                },
                'location': self._parse_location(item[3]),
                
                'documents' : [
                    {
                    'url':   '' ,
                    'note':  ''
                    }
                ],
                #'sources': self._parse_sources(response),
                'sources': [
                    {
                        'url':  '' ,
                        'note': ''
                    }
                ]
            }

            data['id'] = self._generate_id(data)

            yield data

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        parsed_url = urllib.parse.urlparse(item)
        parsed_query = urllib.parse.parse_qs(parsed_url.query)
        return parsed_query['eid'][0]
 
    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'education'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        components = item.split(' ')
        start_time = "{month} {day} {year} {hour_and_minutes}{meridiem}".format(
            month=components[0],
            day=components[1],
            year=components[2],
            hour_and_minutes=components[3],
            meridiem=components[4]
        )
        return datetime.strptime(start_time, "%B %d, %Y %I:%M%p")
        
        
    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        components = item.split(' ')
        end_time = "{month} {day} {year} {hour_and_minutes}{meridiem}".format(
            month=components[0],
            day=components[1],
            year=components[2],
            hour_and_minutes=components[6],
            meridiem=components[7]
        )
        return datetime.strptime(end_time, "%B %d, %Y %I:%M%p")
    
    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'name': '',
            'address': item,
            'neighborhood': ''
        }

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:
        * cancelled
        * tentative
        * confirmed
        * passed
        By default, return "tentative"
        """
        return 'tentative'

    def _parse_sources(self, response):
        """
        Parse or generate sources.
        """
        return [{
            'url': response.url,
            'note': '',
        }]
