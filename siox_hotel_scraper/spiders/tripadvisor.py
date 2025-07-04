import json
import re
import scrapy
import urllib.parse

from urllib3 import HTTPResponse

from siox_hotel_scraper.utils.selenium_handler import SeleniumHandler

class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]

    start_urls = []
    with open('state_list/arkansas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        start_urls = [list(entry.values())[0] for entry in data if list(entry.values())[0] != "Not Available"]

    scrapped_urls = []
    try:
        with open('data/arkansas.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            scrapped_urls = [x['tripadvisor_id'] for x in data]
            print('list of scrapped ids fetched')

    except FileNotFoundError:
        print("No previous data found, starting fresh.")

    def generate_payload(self, offset, geoid):
        return [{
            "variables": {
                "geoId": geoid,
                "currency": "USD",
                "filters": {
                    "selectTravelersChoiceWinner": False,
                    "selectTravelersChoiceBOTBWinner": False

                },
                "offset": offset,
                "limit": 30,
                "sort": "BEST_VALUE",
                "clientType": "DESKTOP",
                "viewType": "LIST",
                "productId": "Hotels",
                "pageviewId": "xxx",
                "sessionId": "xxx",
                "route": {
                    "page": "HotelsFusion",
                    "params": {
                        "geoId": geoid,
                        "contentType": "hotel",
                        "webVariant": "HotelsFusion"
                    }
                },
                "loadLocationSEOData": True,
                "requestNumber": 1,
                "userEngagedFilters":False

            },
            "extensions": {
                "preRegisteredQueryId": "3166880147a6527c"
            }
        }]

    def start_requests(self):
        for url in self.start_urls:
            geo_id1 = int(re.search(r'-g(\d+)', url).group(1))
            payload = self.generate_payload(offset=0, geoid=geo_id1)
            yield scrapy.Request(
                url='https://www.tripadvisor.com/data/graphql/ids',
                method="POST",
                body=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                meta={"offset": 0, 'geo_id':geo_id1, 'dont_proxy': True},
                callback=self.parse,
            )

    def parse(self, response):

        geo_id2 = response.meta.get('geo_id')
        json_data = json.loads(response.text)[0]
        hotels = json_data["data"]["list"]["results"]
        total = json_data["data"]["list"]["searchMetadata"]["totalLocationsInSearch"]
        for hotel in hotels:
            web_link = hotel['location']['url']
            tripadvisor_id = int(re.search(r'-d(\d+)', web_link).group(1))
            if tripadvisor_id:
                full_url = response.urljoin(web_link)
                if f'd{tripadvisor_id}' not in self.scrapped_urls:
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_hotel,
                        meta={'tripadvisor_id': tripadvisor_id}
                    )
                else:
                    print('Skipping already scrapped!')

        # Pagination
        offset = response.meta["offset"]
        next_offset = offset + 30
        if next_offset < total:
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(self.generate_payload(offset=next_offset, geoid=geo_id2)),
                headers={"Content-Type": "application/json"},
                meta={"offset": next_offset},
                callback=self.parse
            ) 

    def parse_hotel(self, response):
    # def parse(self, response):
        # rendered_html = self.selenium_handler.get_rendered_html(response.url)
        # # Create a fake Scrapy Response from Selenium output
        # response = HTTPResponse(url=response.url, body=rendered_html, encoding='utf-8')
        # print(f"Selenium Response: {response}")

        # basic information
        hotel_name = response.xpath('//h1[@id="HEADING"]/text()').get()
        if not hotel_name:
            yield scrapy.Request(
                response.url,
                self.parse_hotel,   
            )
            return
        hotel_url = response.url

        tripadvisor_id = None  
        trpadv_id_match = re.search(r'd\d+', hotel_url)
        if trpadv_id_match:
            tripadvisor_id = trpadv_id_match.group()  

        # address
        city = ''
        state = ''
        zip_code = ''
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

        if tripadvisor_id:
            # Extract the numeric ID (remove the 'd' prefix)
            location_id = int(tripadvisor_id[1:])

            # Yield request to fetch first 10 reviews
            yield self.fetch_reviews(location_id, meta={
                'hotel_info': {
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
            })

    def fetch_reviews(self, hotel_id, meta):
        url = "https://www.tripadvisor.com/data/graphql/ids"
        headers = {
            "Content-Type": "application/json",
        }

        body = [
            {
                "variables": {
                    "locationId": hotel_id,
                    "filters": [{"axis": "LANGUAGE", "selections": ["en"]}],
                    "limit": 10,
                    "offset": 0,
                    "sortBy": "SERVER_DETERMINED",
                    "sortType": None,
                    "language": "en",
                    "useAwsTips": True
                },
                "extensions": {
                    "preRegisteredQueryId": "51c593cb61092fe5"
                }
            }
        ]

        return scrapy.Request(
            url=url,
            method="POST",
            headers=headers,
            body=json.dumps(body),
            callback=self.parse_reviews,
            meta={'dont_proxy': True, **meta}  # ⛔ disables proxy like Zyte Smart Proxy
        )

    def parse_reviews(self, response):
        hotel_info = response.meta['hotel_info']

        try:
            data = response.json()
            reviews_data = data[0]["data"]["ReviewsProxy_getReviewListPageForLocation"][0]["reviews"]
        except Exception as e:
            self.logger.warning(f"Failed to parse review JSON: {e}")
            hotel_info["reviews"] = []
            yield hotel_info
            return

        parsed_reviews = []

        for review in reviews_data:
            user = review.get("userProfile", {})
            trip_info = review.get("tripInfo", {})
            additional_ratings = review.get("additionalRatings", [])
            mgmt_response = review.get("mgmtResponse")

            parsed_reviews.append({
                "title": review.get("title"),
                "rating": review.get("rating"),
                "text": review.get("text"),
                "publishedDate": review.get("publishedDate"),
                "user": {
                    "displayName": user.get("displayName"),
                },
                "additional_ratings": {
                    r["ratingLabelLocalizedString"]: r["rating"]
                    for r in additional_ratings
                },
                "mgmt_response": mgmt_response
            })

        hotel_info["reviews"] = parsed_reviews
        yield hotel_info

