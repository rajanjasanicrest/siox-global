import json
import re
import scrapy
import urllib.parse

from urllib3 import HTTPResponse

from siox_hotel_scraper.utils.selenium_handler import SeleniumHandler

class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor_reviews"
    allowed_domains = ["tripadvisor.com"]

    start_urls = ["https://www.tripadvisor.com"]  # Required to establish cookies session
    
    data = []
    with open('data/texas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    def parse(self, request):

        for hotel_info in self.data:
            yield self.fetch_reviews(int(hotel_info['tripadvisor_id'][1:]), hotel_info)            

    def fetch_reviews(self, hotel_id, hotel_info):
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
            meta={'hotel_info': hotel_info}
        )

    def parse_reviews(self, response):
        hotel_info = response.meta['hotel_info']

        try:
            data = response.json()
            self.logger.info(data)
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