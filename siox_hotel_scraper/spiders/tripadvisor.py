import json
import re
import scrapy
import urllib.parse

from urllib3 import HTTPResponse

from siox_hotel_scraper.utils.selenium_handler import SeleniumHandler

class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    
    start_urls = [
        "https://www.tripadvisor.com/Hotels-g30138-Abilene_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g30165-Amarillo_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g30183-Arlington_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g30196-Austin_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g55711-Dallas_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g55732-Denton_Texas-Hotels.html",
        "https://www.tripadvisor.com/Hotels-g55857-Fort_Worth_Texas-Vacations.html",    
    ]

    scrapped_urls = []
    with open('data/georgia.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        scrapped_urls = [x['hotel_url'] for x in data]



    def parse(self, response):
        
        hotel_list = response.xpath('//div[@data-automation="hotel-card-title"]//a/@href').getall()

        for hotel_link in hotel_list:
            if response.urljoin(hotel_link) not in self.scrapped_urls:
                yield scrapy.Request(
                    response.urljoin(hotel_link),
                    self.parse_hotel,   
                )
            else:
                print('------------------------')
                print('Avoiding the link as scrapped once.')
                print('------------------------')

        next_page = response.xpath(
            '//a[@aria-label="Next page"]/@href'
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse) 

    def parse_hotel(self, response):
    # def parse(self, response):
        # rendered_html = self.selenium_handler.get_rendered_html(response.url)
        # # Create a fake Scrapy Response from Selenium output
        # response = HTTPResponse(url=response.url, body=rendered_html, encoding='utf-8')
        # print(f"Selenium Response: {response}")

        # basic information
        hotel_name = response.xpath('//h1[@id="HEADING"]/text()').get()
        hotel_url = response.url

        tripadvisor_id = None  
        trpadv_id_match = re.search(r'd\d+', hotel_url)
        if trpadv_id_match:
            tripadvisor_id = trpadv_id_match.group()  

        # address
        address = response.xpath("//button[contains(@class, 'UikNM')]//span[contains(@class, 'pZUbB')]/text()").get()
        if address:
            match = re.search(r",\s*([^,]+),\s*([A-Z]{2})\s+(\d{5})", address)
            if match:
                city = match.group(1).strip()
                state = match.group(2)
                zip_code = match.group(3)
        else:
            self.logger.warning("⚠️ Address not found or XPath failed.")

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


        # Extract all text and comment nodes inside the div
        review_parts = response.xpath('//div[@data-automation="bubbleReviewCount"]//text()').getall()

        # Join all parts together
        review_raw = ''.join(review_parts)

        # Use regex to extract the number
        match = re.search(r'([\d,]+)\s+reviews', review_raw)
        if match:
            total_reviews = int(match.group(1).replace(',', ''))
        else:
            total_reviews = None


        number_of_rooms = response.xpath(
            '//div[text()="NUMBER OF ROOMS"]/following-sibling::div[1]/text()'
        ).get()

        # texts = []
        # review_texts = response.xpath("//span[contains(@class, 'orRIx')]/span/text()").getall()
        # for text in review_texts:
        #     texts.append(text.strip())
        # print(f"Total number of reviews: {len(texts)}")
        # print(f"List of reviews: {texts}")

        # responses = []
        # review_responses = response.xpath('//span[contains(@class, "XCFtd")]/text()').getall()
        # for text in review_responses:
        #     if text:  # Check if the text is not empty
        #         responses.append(text.strip())
        #     else:
        #         responses.append(None)
        # print(f"Total number of responses: {len(responses)}")
        # print(f"List of review Responses: {responses}")

            
        
        # link = response.meta.get('js_link')
        # if link:
        #     print(f"Link for nearby hotels (via Selenium): {link}")
        # else:
        #     print("No link found for nearby hotels.")



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
            'total_reviews': total_reviews,
            'number_of_rooms': number_of_rooms,
            **ratings_dict,
        }

