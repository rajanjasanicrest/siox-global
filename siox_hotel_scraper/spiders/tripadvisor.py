import re
import scrapy
import urllib.parse

class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    # start_urls = ["https://www.tripadvisor.com/Hotels-g28931-Georgia-Hotels.html"]
    start_urls = ["https://www.tripadvisor.com/Hotel_Review-g60814-d7216821-Reviews-Homewood_Suites_By_Hilton_Savannah_Historic_District_Riverfront-Savannah_Georgia.html"]

    # def parse(self, response):
        
    #     hotel_list = response.xpath('//div[@data-automation="hotel-card-title"]//a/@href').getall()

    #     for hotel_link in hotel_list:
    #         yield {
    #             'hotel_link': hotel_link
    #         }
    #         yield scrapy.Request(
    #             response.urljoin(hotel_link),
    #             self.parse_hotel,
                
    #         )

    #     next_page = response.xpath(
    #         '//a[@aria-label="Next page"]/@href'
    #     ).get()
    #     if next_page:
    #         # yield {
    #         #     'next_page': next_page
    #         # }
    #         yield response.follow(next_page, callback=self.parse) 

    # def parse_hotel(self, response):
    def parse(self, response):


        # basic information
        hotel_name = response.xpath('//h1[@id="HEADING"]/text()').get()
        hotel_url = response.url

        tripadvisor_id = None  
        trpadv_id_match = re.search(r'd\d+', hotel_url)
        if trpadv_id_match:
            tripadvisor_id = trpadv_id_match.group()  

        # address
        address = response.xpath("//button[contains(@class, 'UikNM')]//span[contains(@class, 'pZUbB')]/text()").get()
        match = re.search(r",\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})", address)
        if match:
            city = match.group(1).strip()
            state = match.group(2)
            zip_code = match.group(3)

        categories = response.xpath('//div[@class="ZPHZV"]//div[@class="jxnKb"]//div[contains(@class, "Ygqck")]/text()').getall()
        ratings = response.xpath('//div[@class="ZPHZV"]//div[@class="jxnKb"]//div[contains(@class, "biKBZ")]/text()').getall()

        ratings_dict = dict(zip(categories, ratings))

        overall_rating = response.xpath("//div[contains(@class, 'biGQs') and contains(@class, '_P') and contains(@class, 'hzzSG') and contains(@class, 'LSyRd')]/text()").get()

        region_rank = response.xpath("//div[@class='d']//div[contains(@class, 'biGQs') and contains(@class, '_P') and contains(@class, 'pZUbB') and contains(@class, 'KxBGd')]/text()").get()

        script_src = response.xpath(
            '//script[starts-with(@src, "data:text/javascript")]/@src'
        ).get()

        if script_src:
            # Step 2: URL-decode the content
            decoded_script = urllib.parse.unquote(script_src)

            # Step 3: Use regex to find lat/lng values
            match = re.search(r'latitude.*?([0-9\.\-]+).*?longitude.*?([0-9\.\-]+)', decoded_script)

            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                print(f"✅ Latitude: {latitude}, Longitude: {longitude}")
            else:
                print("❌ Coordinates not found in decoded script.")
        else:
            print("❌ No matching <script> tag with 'data:text/javascript' found.")


        total_reviews = response.xpath('').get()

        yield {
            'hotel_name': hotel_name,
            'hotel_url': hotel_url,
            'tripadvisor_id': tripadvisor_id,
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'region_rank': region_rank,
            'overall_rating': overall_rating,
            'latitude': latitude,
            'longitude': longitude,
            **ratings_dict,
        }