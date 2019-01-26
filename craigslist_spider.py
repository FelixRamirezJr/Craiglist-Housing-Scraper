import scrapy
import re

# CONSTANTS
real_estate_route = '/d/real-estate/search/rea'

# shared-line-bubble order of information
bedrooms_and_bath_index = 0
square_feed_index = 1

# attrgroup information order
dimensions_index = 0
extras_index = 1



class CraiglistSpider(scrapy.Spider):
    name = 'CraiglistSpider'
    start_urls = ['https://geo.craigslist.org/iso/us/']
    allowed_domains = ['craigslist.org']

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

                    if location_link.lower() != "//www.craigslist.org/about/terms.of.use":
                        real_estate_sold_link = location_link + real_estate_route
                        yield scrapy.Request(real_estate_sold_link, callback=self.parse_location, meta={'place': place})

        # print all the locations that we found
        for location in craiglist_locations:
            print location

    def parse_location(self, response):
        #self.logger.info("Visiting %s", response.url)
        # Go through each of the housing
        for house_for_sale in response.css('.result-row'):
            house_for_sale_link = house_for_sale.css( 'a::attr(href)' ).extract_first()
            #self.logger.info( "House for sale link: %s", house_for_sale_link )
            yield scrapy.Request( house_for_sale_link, callback=self.parse_investment, meta={'place': response.meta['place']} )

        # If there is a next page, go to the next page
        for next_page in response.css('.next'):
            next_page_route = next_page.css('a::attr(href)').extract()[0]
            next_page_link = response.url.replace( real_estate_route, next_page_route )
            if next_page_route != None and len( next_page_route ) > 0:
                #self.logger.info( 'Visiting the next page with: %s', next_page_link )
                yield scrapy.Request( next_page_link, callback=self.parse_location, meta={'place': response.meta['place']} )

    # Method for a specific post of real estate
    def parse_investment(self, response):
        data = {'rooms': '', 'bathrooms': '', 'price': '', 'link': '', 'location': response.meta['place']}
        #self.logger.info("parse_investment: %s -- at the location: %s", response.url, response.meta['place'])
        # Get the price
        for price in response.css('.price'):
            data['price'] = price.xpath('text()').extract()[0]

        # Get the bedrooms and baths
        for index, shared_line_bubble_data in enumerate(response.css('.shared-line-bubble')):
            if index == bedrooms_and_bath_index:
                data['rooms'] = shared_line_bubble_data.xpath('b/text()').extract()[0]
                data['bathrooms'] = shared_line_bubble_data.xpath('b/text()').extract()[1]

        # Now that we have the data, send it to the server
        if not(len(data['rooms'] ) == 0 or len( data['bathrooms'] ) == 0):
            print "==========="
            print data
            print "==========="
