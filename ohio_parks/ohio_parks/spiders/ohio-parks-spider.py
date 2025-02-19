import scrapy
from serpapi import GoogleSearch

class OhioStateParksSpider(scrapy.Spider):
    name = "ohio_state_parks"
    start_urls = ["https://stateparks.com/ohio_parks_and_recreation_destinations.html"]

    def parse(self, response):
        # Extract links to individual park pages
        park_links = response.xpath('//a[contains(@href, "state_park_in_ohio.html")]/@href').extract()
        for link in park_links:
            yield response.follow(link, self.parse_park_details)

    def parse_park_details(self, response):
        # Extract details from individual park pages
        park_name = response.xpath('//div[@id="overview"]//div[@class="htext hh"]/text()').get()
        address = response.xpath('//span[@class="p_name"]/following-sibling::br[1]/text()').get()
        location_details = response.xpath('//span[@class="p_name"]/following-sibling::div/text()').get()
        latitude = response.xpath('//div[@class="parkinfo"]//a[@target="googleMaps"]/@href').re_first(r'@([\d.-]+),')
        longitude = response.xpath('//div[@class="parkinfo"]//a[@target="googleMaps"]/@href').re_first(r',([\d.-]+),')
        description = response.xpath('//div[@id="overview"]//div[@class="psbod"]/text()').get()
        phone = response.xpath('//a[contains(@href, "tel:")]/text()').get()
        reservation_phone = response.xpath('//a[contains(@href, "tel:")][2]/text()').get()
        activities = response.xpath('//div[@id="amenities_chart"]//div[@class="amenityT"]//span[@class="amenityD"]/text()').getall()

        yield {
            "park_name": park_name,
            "address": address,
            "location_details": location_details,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "phone": phone,
            "reservation_phone": reservation_phone,
            "activities": activities,
            "url": response.url,
        }