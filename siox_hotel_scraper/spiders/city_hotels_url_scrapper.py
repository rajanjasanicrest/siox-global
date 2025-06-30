import json
import re
import scrapy
import urllib.parse

from urllib3 import HTTPResponse

from siox_hotel_scraper.utils.selenium_handler import SeleniumHandler

class TripadvisorSpider(scrapy.Spider):
    name = "city_hotels_url_scrapper"
    allowed_domains = ["tripadvisor.com"]
    start_urls = ["https://www.tripadvisor.com"]  # Required to establish cookies session

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = "https://www.tripadvisor.com/data/graphql/ids"
        self.query_id = "c2e5695e939386e4"
        self.state = "Virginia"
        self.country = "United States"
        

        self.cities = ["Virginia Beach", "Richmond", "Chesapeake", "Arlington", "Norfolk", "Roanoke", "Newport News", "Fredericksburg", "Alexandria", "Hampton", "Lynchburg", "Charlottesville", "Portsmouth", "Suffolk", "Williamsburg", "Winchester", "Harrisonburg", "Dale City", "Centreville", "Blacksburg", "Reston", "McLean", "Leesburg", "Tuckahoe", "Ashburn", "Lake Ridge", "Woodbridge", "Burke", "Manassas", "Danville", "Linton Hall", "Annandale", "Mechanicsville", "Oakton", "Fair Oaks", "South Riding", "Petersburg", "Sterling", "Springfield", "West Falls Church", "Short Pump", "Tysons", "Cave Spring", "Staunton", "Salem", "Bailey's Crossroads", "Herndon", "Fairfax", "Brambleton", "Chantilly", "Chester", "Cherry Hill", "Hopewell", "West Springfield", "Christiansburg", "Waynesboro", "McNair", "Montclair", "Lorton", "Woodlawn", "Rose Hill", "Merrifield", "Buckhall", "Culpeper", "Meadowbrook", "Lincolnia", "Midlothian", "Franklin Farm", "Sudley", "Colonial Heights", "Laurel", "Franconia", "Gainesville", "Hybla Valley", "Idylwood", "Burke Centre", "Kingstowne", "Bon Air", "Bristol", "Hollins", "Manassas Park", "Bull Run", "Glen Allen", "Fort Hunt", "Radford", "Vienna", "Stone Ridge", "East Highland Park", "Wolf Trap", "Front Royal", "Highland Springs", "Great Falls", "Broadlands", "Falls Church", "Brandermill", "Newington", "Martinsville", "Groveton", "Kings Park West", "Huntington", "Mount Vernon", "Sugarland Run", "Lakeside", "Timberlake", "Lansdowne", "Poquoson", "Cascades", "Forest", "Newington Forest", "Manchester", "Fairfax Station", "Wyndham", "Wakefield", "Stuarts Draft", "Dranesville", "New Baltimore", "Triangle", "Lowes Island", "Gloucester Point", "Lake Monticello", "Lake Barcroft", "Yorkshire", "Madison Heights", "Loudoun Valley Estates", "Independent Hill", "Difficult Run", "Warrenton", "Woodburn", "George Mason", "Fishersville", "Belmont", "Countryside", "Crozet", "Seven Corners", "University of Virginia", "Purcellville", "Pulaski", "Rockwood", "Dunn Loring", "Smithfield", "Montrose", "Fair Lakes", "Hollymead", "Innsbrook", "Bellwood", "Dumbarton", "Abingdon", "Fort Lee", "Wytheville", "Franklin", "Lake of the Woods", "Fort Belvoir", "Vinton", "Greenbriar", "Carrollton", "South Boston", "Ashland", "Collinsville", "Farmville", "Laurel Hill", "Bull Run", "North Springfield", "Mantua", "Lexington", "Woodlake", "Strasburg", "Floris", "Long Branch", "Sandston", "Hutchison", "Aquia Harbour", "Spotsylvania Courthouse", "South Run", "Bedford", "Galax", "Bridgewater", "Buena Vista", "Belle Haven", "Braddock", "Pimmit Hills", "Potomac Mills", "Massanetta Springs", "Woodstock", "Bensley", "Stafford Courthouse", "Ettrick", "Dumfries", "Marion", "Covington", "Emporia", "Crosspointe", "Dulles Town Center", "Quantico Base", "Big Stone Gap", "Bealeton", "Richlands", "Falmouth", "Bluefield", "Orange", "Chamberlayne", "Rocky Mount", "Luray", "King George", "South Hill", "Berryville", "Bethel Manor", "Loch Lomond", "Tazewell", "Union Mill", "Pantops", "Mount Hermon", "Verona", "Hayfield", "County Center", "Broadway", "Kings Park", "University Center", "Enon", "Shenandoah Farms", "Colonial Beach", "Navy", "North Shore", "Norton", "Lake Land'Or", "Gloucester Courthouse", "Clifton Forge", "West Point", "Dahlgren", "Altavista", "Blackstone", "Chincoteague", "Lake Wilderness", "Marshall", "Daleville", "Lebanon", "Shenandoah", "One Loudoun", "Blue Ridge", "Cloverdale", "Timberville", "Elkton", "Merrimac", "Wise", "Grottoes", "Hillsville", "Pearisburg", "Arcola", "Windsor", "Crewe", "Lake Caroline", "Lovettsville", "Dublin", "Sully Square", "Shawneeland", "Waverly", "Ravensworth", "Fairlawn", "Chase City", "Goose Creek Village", "Piney Mountain", "Chilhowie", "Oak Grove", "Matoaca", "Stephens City", "Warsaw", "Rivanna", "Louisa", "Weyers Cave", "Glade Spring", "Southern Gateway", "Massanutten", "Horse Pasture", "New Market", "Amherst", "Patrick Springs", "Appomattox", "Prince George", "Narrows", "Mason Neck", "Lake Holiday", "Saltville", "Mount Jackson", "Dayton", "Pennington Gap", "East Lexington", "Stanley", "Hampden-Sydney", "Gate City", "Tappahannock", "Victoria", "Laymantown", "Raven", "Westlake Corner", "Crimora", "Apple Mountain Lake", "Twin Lakes", "Courtland", "Exmore", "Shawsville", "Clarksville", "Stuart", "Captains Cove", "Middletown", "Nellysford", "Ferrum", "Rural Retreat", "Appalachia", "Coeburn", "Haymarket", "Bull Run Mountain Estates", "Camp Barrett", "Edinburg", "Chatham", "Gordonsville", "Mountain Road", "Chatmoss", "Weber City", "Clintwood", "Union Hall", "Bowling Green", "Benns Church", "Brightwood", "Wattsville", "Basye", "Lyndhurst", "Great Falls Crossing", "Hurt", "Concord", "Central Garage", "Kilmarnock", "Dooms", "Halifax", "Kenbridge", "Claypool Hill", "Onancock", "Stanleytown", "Ruckersville", "Goochland", "Jonesville", "Cape Charles", "Rustburg", "Brookneal", "Gretna", "Buchanan", "Glasgow", "Penhook", "Harriston", "Bracey", "Honaker", "Earlysville", "Rio", "Amelia Court House", "Greenville", "Nokesville", "Cana", "Cedar Bluff", "McGaheysville", "Lawrenceville", "Mathews", "Independence", "Innovation", "Maurertown", "Jolivue", "Emory", "Pembroke", "Riverdale", "Castlewood", "Occoquan", "Rushmere", "Arrington", "Ridgeway", "Plum Creek", "Craigsville", "St. Paul", "Elliston", "Cluster Springs", "Riner", "Belmont Estates", "Atkins", "Bassett", "Passapatanzy", "Blairs", "Adwolf", "Accomac", "Boyce", "Springville", "Disputanta", "Belview", "New Hope", "Prices Fork", "Chester Gap", "Jarratt", "New Kent", "Glenvar", "Deltaville", "Blue Ridge Shores", "Laurel Park", "Henry Fork", "Pound", "Clover", "Remington", "Fieldale", "Gratton", "Middleburg", "East Stone Gap", "Pastoria", "Opal", "Shenandoah Shores", "Parksley", "Grundy", "Rich Creek", "Fort Chiswell", "Damascus", "Camptown", "Boissevain", "Barboursville", "Ivy", "Motley", "Keysville", "Baywood", "Ivanhoe", "Nassawadox", "Powhatan", "Charlotte Court House", "Dahlgren Center", "Mount Sidney", "Riverview", "Villa Heights", "Fincastle", "Round Hill", "Onley", "Skyland Estates", "Hamilton", "Kincora", "Mineral", "Sugar Grove", "Sedley", "Dante", "Saluda", "Quantico", "Gwynn", "Gargatha", "Max Meadows", "Shenandoah Retreat", "McKenney", "Oak Level", "Port Republic", "Savageville", "Dillwyn", "Cheriton", "Dryden", "Allison Gap", "Hot Springs", "The University of Virginia's College at Wise", "Haysi", "Unionville", "Mount Crawford", "La Crosse", "Keezletown", "Lafayette", "Seven Mile Ford", "Bland", "Mallow", "Floyd", "Irvington", "Gasburg", "Shipman", "Burkeville", "Scottsville", "Boykins", "Horntown", "Fairfield", "Drakes Branch", "Stanardsville", "Sandy Level", "Wintergreen", "Urbanna", "Bloxom", "Draper", "Troutville", "Chase Crossing", "Melfa", "Ewing", "Montross", "Atlantic", "Stewartsville", "Lovingston", "Big Stone Gap East", "Bastian", "Deerfield", "Parrott", "Esmont", "Iron Gate", "Dinwiddie", "North Garden", "Mappsville", "Hiltons", "Nickelsville", "Low Moor", "Phenix", "Keswick", "New Church", "Montvale", "New River", "Conicville", "Toms Brook", "Vansant", "Claremont", "Sperryville", "Stony Creek", "White Stone", "Clinchco", "Brodnax", "Bowmans Crossing", "Ripplemead", "Cleveland", "Selma", "Metompkin", "Madison", "Willis Wharf", "Clifton", "Hilltown", "Painter", "Moneta", "Newsoms", "Keokee", "Nelsonia", "Cumberland", "Wachapreague", "Fries", "Goshen", "Eastville", "Carrsville", "Dungannon", "Callaghan", "Alonzaville", "Fairview", "Keller", "Brucetown", "Quinby", "Columbia Furnace", "Temperanceville", "Weems", "Rhoadesville", "Southampton Meadows", "Ivor", "Savage Town", "Buckingham Courthouse", "Boydton", "Schuyler", "Alberta", "Sherando", "Flint Hill", "Waterford", "Fancy Gap", "Afton", "Modest Town", "McMullin", "Tangier", "Yogaville", "Dendron", "Pounding Mill", "Saxis", "Linville", "Boones Mill", "Breaks", "Pocahontas", "Stickleyville", "Midland", "Fairview Beach", "Cats Bridge", "Baskerville", "Monterey", "Troutdale", "Bobtown", "Mount Clifton", "Belspring", "Surry", "Pungoteague", "Free Union", "Greenbush", "Yorktown", "Locust Grove", "Aldie", "Big Rock", "Middlebrook", "Millboro", "Hallwood", "Boston", "Branchville", "Stonega", "Capron", "King William", "Hillsboro", "Quicksburg", "Singers Glen", "Tacoma", "Deep Creek", "Catlett", "Virgilina", "Abbs Valley", "Mendota", "New Castle", "Snowville", "Eagle Rock", "Pamplin City", "The Plains", "Sussex", "Big Island", "Meadows of Dan", "Heathsville", "Stevens Creek", "Southside Chesconessex", "Locust Mount", "Makemie Park", "Eggleston", "Falls Mills", "Nottoway Court House", "Union Level", "Port Royal", "Scotland", "Brandy Station", "Harborton", "Lee Mont", "Osaka", "Templeton", "St. Charles", "Hiwassee", "Cliftondale Park", "Augusta Springs", "Bayside", "Ebony", "Glen Wilton", "Lebanon Church", "Scottsburg", "Glen Lyn", "Oak Hall", "Tasley", "Warfield", "Duffield", "Churchville", "Greenbackville", "Washington", "Clinchport", "Calverton", "Paris", "Mechanicsburg", "Nathalie", "Gore", "Whitesville", "Hanover", "Dunbar", "Allisonia", "Schooner Bay", "Jewell Ridge", "Upperville", "Rectortown", "Columbia", "McDowell", "Charles City", "Mount Olive", "King and Queen Court House", "Palmyra", "Mappsburg", "Lancaster", "Warm Springs", "Saumsville", "Lunenburg", "Doran", "Sanford", "Franktown", "Rocky Gap", "Hudson Crossroads", "Fishers Hill", "Thynedale", "Orkney Springs", "Austinville", "Amonate", "Forestville", "Clary"]


    def parse(self, response):
        # This initial GET request is just to obtain cookies
        for city in self.cities:
            payload = [{
                "variables": {
                    "request": {
                        "query": f"{city}, {self.state}, {self.country}",
                        "limit": 10,
                        "scope": "IN_GEO_EXTEND_WORLDWIDE",
                        "locale": "en-US",
                        "scopeGeoId": 46111,
                        "searchCenter": None,
                        "enabledFeatures": ["articles"],
                        "includeNestedResults": True,
                        "includeRecent": False,
                        "locationTypes": [
                            "GEO"
                        ],
                        "types": ["LOCATION"],
                        "userId": "426A805CDEAC439A2F678D5E67302A3C",
                        "context": {
                            "listResultType": "HOTEL",
                            "searchSessionId": "001c80ffdb8aac6a.ssid",
                            "typeaheadId": "1751261788530",
                            "routeUid": "7e4c94b8-bf51-4b44-be30-b37b0eddbab0",
                            "uiOrigin": "SINGLE_SEARCH_NAV"
                        }
                    }
                },
                "extensions": {
                    "preRegisteredQueryId": self.query_id
                }
            }]

            yield scrapy.Request(
                url=self.api_url,
                method="POST",
                body=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                callback=self.parse_results,
                meta={"city": city}
            )

    def parse_results(self, response):
        city = response.meta["city"]
        data = response.json()
        results = data[0].get("data", {}).get("Typeahead_autocomplete", {}).get("results", [])
        
        for item in results:
            details = item.get("details", {})
            
            if details.get("localizedName", "").strip().lower() == city.lower():
                if self.state in details.get("localizedAdditionalNames", {}).get("longOnlyHierarchy", ""):
                    # Extract the hotels URL
                    hotels_url = details.get("HOTELS_URL")
                    if hotels_url:
                        yield {
                            f"{city}": f"https://www.tripadvisor.com{hotels_url}"
                        }
                        return  

        yield {
            f"{city}": "Not Available"
        }