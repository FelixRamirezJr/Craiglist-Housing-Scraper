import scrapy
import re

class CraiglistSpider(scrapy.Spider):
    name = 'CraiglistSpider'
    start_urls = ['https://geo.craigslist.org/iso/us/']

    def parse(self, response):
        craiglist_locations = []
        ignore = "https://www.|https://forums.|terms.of.use|www"

        # Extract all the craiglist urls
        for location in response.css('li'):
            if location != None:
                location_link = location.css('a::attr(href)').extract_first()
                if location_link != None and not re.compile(ignore).match(location_link):
                    place = location.xpath('a/text()').extract()
                    if (isinstance(place, list) and len(place) > 0): # If it's an array we need to only get the first el
                        place = place[0]
                    else:
                        place = location.xpath('a/b/text()').extract()[0]
                    craiglist_locations.append({'place': place, 'url': location_link})

        for location in craiglist_locations:
            print location

        # Now that we have our craiglist locations with place and link, loop through them
        # for location in craiglist_locations:
        #     city, state = ("",)*2
        #     if location['place']:
        #         print location['place']
        #         city_state = re.compile(",|/|-").split(location['place'])
        #         city = city_state[0] # First element in list should always be the city
        #         if len(city_state) > 1:
        #             state = city_state[1] # Second element in the list should always be in the state

            # Now we have extracted the city and state, let's visit the url and get to the housing
