import time
import json
import csv
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, parse_qs
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

import requests
from bs4 import BeautifulSoup


@dataclass
class HotelData:
    """Data structure for hotel information"""
    hotel_name: str = ""
    hotel_url: str = ""
    tripadvisor_id: str = ""
    city: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    official_star_rating: str = ""
    guest_star_rating: float = 0.0
    overall_rating_score: float = 0.0
    total_reviews: int = 0
    city_ranking: str = ""
    region_ranking: str = ""
    location_rating: float = 0.0
    cleanliness_rating: float = 0.0
    service_rating: float = 0.0
    value_rating: float = 0.0
    rooms_rating: float = 0.0
    sleep_quality_rating: float = 0.0
    has_management_response: bool = False
    management_response_date: str = ""
    management_response_text: str = ""
    competitor_hotels: List[str] = None
    scrape_timestamp: str = ""

    def __post_init__(self):
        if self.competitor_hotels is None:
            self.competitor_hotels = []


class TripAdvisorScraper:
    """TripAdvisor hotel scraper with proxy support"""
    
    def __init__(self, use_proxy: bool = True, proxy_config: Dict = None):
        self.use_proxy = use_proxy
        self.proxy_config = proxy_config or {}
        self.driver = None
        self.wait = None
        self.scraped_hotels = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tripadvisor_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """Setup Chrome driver with proxy configuration"""
        chrome_options = Options()
        
        # Basic Chrome options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Proxy configuration
        if self.use_proxy and self.proxy_config:
            if 'zyte_api_key' in self.proxy_config:
                # Zyte Proxy configuration
                chrome_options.add_argument(f'--proxy-server=http://proxy.zyte.com:8223')
                chrome_options.add_argument(f'--proxy-auth={self.proxy_config["zyte_api_key"]}:')
            elif 'proxy_host' in self.proxy_config:
                # Custom proxy configuration
                proxy_string = f"{self.proxy_config['proxy_host']}:{self.proxy_config['proxy_port']}"
                chrome_options.add_argument(f'--proxy-server=http://{proxy_string}')
                
                if 'proxy_username' in self.proxy_config:
                    chrome_options.add_argument(
                        f'--proxy-auth={self.proxy_config["proxy_username"]}:{self.proxy_config["proxy_password"]}'
                    )
        
        # Headless mode (optional)
        # chrome_options.add_argument('--headless')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def get_usa_cities_urls(self) -> List[str]:
        """Get URLs for all major USA cities from TripAdvisor with actual geo IDs"""
        
        # Dictionary of cities with their actual TripAdvisor geo IDs
        usa_cities = {
            # Alabama
            'Birmingham-Alabama': 'g30375',
            'Montgomery-Alabama': 'g30394',
            'Mobile-Alabama': 'g30392',
            'Huntsville-Alabama': 'g30384',
            
            # Alaska
            'Anchorage-Alaska': 'g60880',
            'Fairbanks-Alaska': 'g60966',
            'Juneau-Alaska': 'g60999',
            
            # Arizona
            'Phoenix-Arizona': 'g31310',
            'Tucson-Arizona': 'g31373',
            'Mesa-Arizona': 'g31335',
            'Chandler-Arizona': 'g31257',
            'Scottsdale-Arizona': 'g31357',
            'Glendale-Arizona': 'g31288',
            'Tempe-Arizona': 'g31366',
            'Peoria-Arizona': 'g31348',
            'Surprise-Arizona': 'g31362',
            'Yuma-Arizona': 'g31378',
            'Flagstaff-Arizona': 'g31281',
            'Sedona-Arizona': 'g31359',
            
            # Arkansas
            'Little-Rock-Arkansas': 'g31998',
            'Fort-Smith-Arkansas': 'g31977',
            'Fayetteville-Arkansas': 'g31974',
            'Springdale-Arkansas': 'g32026',
            'Jonesboro-Arkansas': 'g31990',
            
            # California
            'Los-Angeles-California': 'g32655',
            'San-Diego-California': 'g32838',
            'San-Jose-California': 'g32849',
            'San-Francisco-California': 'g32837',
            'Fresno-California': 'g32421',
            'Sacramento-California': 'g32824',
            'Long-Beach-California': 'g32648',
            'Oakland-California': 'g32781',
            'Bakersfield-California': 'g32209',
            'Anaheim-California': 'g32122',
            'Santa-Ana-California': 'g32902',
            'Riverside-California': 'g32823',
            'Stockton-California': 'g32946',
            'Irvine-California': 'g32525',
            'Chula-Vista-California': 'g32315',
            'Fremont-California': 'g32411',
            'San-Bernardino-California': 'g32835',
            'Modesto-California': 'g32721',
            'Oxnard-California': 'g32793',
            'Fontana-California': 'g32409',
            'Moreno-Valley-California': 'g32733',
            'Huntington-Beach-California': 'g32515',
            'Glendale-California': 'g32449',
            'Santa-Clarita-California': 'g32900',
            'Garden-Grove-California': 'g32441',
            'Oceanside-California': 'g32783',
            'Rancho-Cucamonga-California': 'g32816',
            'Santa-Rosa-California': 'g32905',
            'Ontario-California': 'g32787',
            'Lancaster-California': 'g32605',
            'Elk-Grove-California': 'g32375',
            'Corona-California': 'g32340',
            'Palmdale-California': 'g32798',
            'Salinas-California': 'g32833',
            'Pomona-California': 'g32806',
            'Hayward-California': 'g32486',
            'Escondido-California': 'g32382',
            'Torrance-California': 'g32970',
            'Sunnyvale-California': 'g32960',
            'Orange-California': 'g32790',
            'Fullerton-California': 'g32418',
            'Pasadena-California': 'g32800',
            'Thousand-Oaks-California': 'g32968',
            'Visalia-California': 'g32985',
            'Simi-Valley-California': 'g32930',
            'Concord-California': 'g32336',
            'Roseville-California': 'g32822',
            'Santa-Clara-California': 'g32903',
            'Vallejo-California': 'g32976',
            'Victorville-California': 'g32979',
            'El-Monte-California': 'g32373',
            'Berkeley-California': 'g32248',
            'Downey-California': 'g32358',
            'Costa-Mesa-California': 'g32344',
            'Inglewood-California': 'g32520',
            'San-Buenaventura-California': 'g32834',
            'West-Covina-California': 'g32990',
            'Richmond-California': 'g32820',
            'Norwalk-California': 'g32779',
            'Carlsbad-California': 'g32285',
            'Daly-City-California': 'g32347',
            'Temecula-California': 'g32964',
            'Santa-Maria-California': 'g32904',
            'El-Cajon-California': 'g32370',
            'Murrieta-California': 'g32739',
            'Burbank-California': 'g32275',
            'Santa-Monica-California': 'g32908',
            'Rialto-California': 'g32819',
            'Fairfield-California': 'g32386',
            'Antioch-California': 'g32136',
            'Chico-California': 'g32312',
            'Napa-California': 'g32766',
            'Redding-California': 'g32817',
            'Chino-California': 'g32313',
            'San-Mateo-California': 'g32850',
            'Reno-Nevada': 'g45963',
            'Las-Vegas-Nevada': 'g45963',
            
            # Colorado
            'Denver-Colorado': 'g33388',
            'Colorado-Springs-Colorado': 'g33364',
            'Aurora-Colorado': 'g33321',
            'Fort-Collins-Colorado': 'g33412',
            'Lakewood-Colorado': 'g33453',
            'Thornton-Colorado': 'g33533',
            'Arvada-Colorado': 'g33319',
            'Westminster-Colorado': 'g33544',
            'Pueblo-Colorado': 'g33501',
            'Centennial-Colorado': 'g33342',
            'Boulder-Colorado': 'g33330',
            'Greeley-Colorado': 'g33423',
            'Longmont-Colorado': 'g33462',
            'Loveland-Colorado': 'g33467',
            'Grand-Junction-Colorado': 'g33422',
            'Broomfield-Colorado': 'g33332',
            'Castle-Rock-Colorado': 'g33339',
            'Commerce-City-Colorado': 'g33362',
            'Northglenn-Colorado': 'g33490',
            'Brighton-Colorado': 'g33331',
            'Wheat-Ridge-Colorado': 'g33545',
            'Louisville-Colorado': 'g33468',
            'Littleton-Colorado': 'g33460',
            'Aspen-Colorado': 'g33320',
            'Vail-Colorado': 'g33540',
            'Steamboat-Springs-Colorado': 'g33524',
            'Breckenridge-Colorado': 'g33332',
            'Durango-Colorado': 'g33399',
            'Estes-Park-Colorado': 'g33405',
            
            # Connecticut
            'Bridgeport-Connecticut': 'g33774',
            'New-Haven-Connecticut': 'g33805',
            'Hartford-Connecticut': 'g33795',
            'Stamford-Connecticut': 'g33821',
            'Waterbury-Connecticut': 'g33841',
            'Norwalk-Connecticut': 'g33807',
            'Danbury-Connecticut': 'g33784',
            'New-Britain-Connecticut': 'g33802',
            'West-Hartford-Connecticut': 'g33844',
            'Greenwich-Connecticut': 'g33790',
            'Hamden-Connecticut': 'g33794',
            'Meriden-Connecticut': 'g33800',
            'Bristol-Connecticut': 'g33775',
            'West-Haven-Connecticut': 'g33845',
            'Milford-Connecticut': 'g33801',
            'Middletown-Connecticut': 'g33801',
            'Norwich-Connecticut': 'g33808',
            'Shelton-Connecticut': 'g33817',
            'Torrington-Connecticut': 'g33833',
            'New-London-Connecticut': 'g33804',
            'Ansonia-Connecticut': 'g33770',
            'Derby-Connecticut': 'g33785',
            'Groton-Connecticut': 'g33791',
            'Stratford-Connecticut': 'g33823',
            'Watertown-Connecticut': 'g33842',
            'New-Milford-Connecticut': 'g33803',
            'Trumbull-Connecticut': 'g33834',
            'East-Hartford-Connecticut': 'g33786',
            'Glastonbury-Connecticut': 'g33789',
            'Newington-Connecticut': 'g33806',
            'New-Canaan-Connecticut': 'g33802',
            'Mystic-Connecticut': 'g33802',
            
            # Delaware
            'Wilmington-Delaware': 'g34108',
            'Dover-Delaware': 'g34093',
            'Newark-Delaware': 'g34101',
            'Middletown-Delaware': 'g34098',
            'Smyrna-Delaware': 'g34105',
            'Milford-Delaware': 'g34099',
            'Seaford-Delaware': 'g34104',
            'Georgetown-Delaware': 'g34095',
            'Elsmere-Delaware': 'g34094',
            'New-Castle-Delaware': 'g34100',
            'Rehoboth-Beach-Delaware': 'g34103',
            'Bethany-Beach-Delaware': 'g34091',
            'Lewes-Delaware': 'g34097',
            'Dewey-Beach-Delaware': 'g34092',
            
            # Florida
            'Jacksonville-Florida': 'g34438',
            'Miami-Florida': 'g34438',
            'Tampa-Florida': 'g34678',
            'Orlando-Florida': 'g34515',
            'St-Petersburg-Florida': 'g34607',
            'Hialeah-Florida': 'g34404',
            'Tallahassee-Florida': 'g34679',
            'Fort-Lauderdale-Florida': 'g34227',
            'Port-St-Lucie-Florida': 'g34551',
            'Cape-Coral-Florida': 'g34140',
            'Pembroke-Pines-Florida': 'g34536',
            'Hollywood-Florida': 'g34413',
            'Gainesville-Florida': 'g34242',
            'Coral-Springs-Florida': 'g34191',
            'Clearwater-Florida': 'g34161',
            'Miami-Gardens-Florida': 'g34463',
            'Palm-Bay-Florida': 'g34529',
            'West-Palm-Beach-Florida': 'g34768',
            'Pompano-Beach-Florida': 'g34549',
            'Lakeland-Florida': 'g34457',
            'Davie-Florida': 'g34201',
            'Miami-Beach-Florida': 'g34439',
            'Sunrise-Florida': 'g34669',
            'Boca-Raton-Florida': 'g34086',
            'Deltona-Florida': 'g34204',
            'Plantation-Florida': 'g34548',
            'Palm-Coast-Florida': 'g34532',
            'Largo-Florida': 'g34458',
            'Melbourne-Florida': 'g34485',
            'Boynton-Beach-Florida': 'g34106',
            'Fort-Myers-Florida': 'g34230',
            'Kissimmee-Florida': 'g34452',
            'Homestead-Florida': 'g34414',
            'Delray-Beach-Florida': 'g34203',
            'Ocala-Florida': 'g34501',
            'Sarasota-Florida': 'g34635',
            'Daytona-Beach-Florida': 'g34198',
            'Port-Orange-Florida': 'g34550',
            'Poinciana-Florida': 'g34549',
            'Bradenton-Florida': 'g34108',
            'Palm-Beach-Gardens-Florida': 'g34531',
            'Pinellas-Park-Florida': 'g34545',
            'Lauderhill-Florida': 'g34461',
            'Weston-Florida': 'g34769',
            'Pensacola-Florida': 'g34538',
            'Deerfield-Beach-Florida': 'g34202',
            'Sanford-Florida': 'g34631',
            'North-Miami-Florida': 'g34496',
            'Jupiter-Florida': 'g34447',
            'Coconut-Creek-Florida': 'g34164',
            'Margate-Florida': 'g34476',
            'Wellington-Florida': 'g34760',
            'Tamarac-Florida': 'g34681',
            'North-Lauderdale-Florida': 'g34498',
            'Bonita-Springs-Florida': 'g34089',
            'Ocala-Florida': 'g34501',
            'Titusville-Florida': 'g34698',
            'Aventura-Florida': 'g34053',
            'Apopka-Florida': 'g34044',
            'Fort-Pierce-Florida': 'g34234',
            'North-Miami-Beach-Florida': 'g34497',
            'DeLand-Florida': 'g34203',
            'Ormond-Beach-Florida': 'g34518',
            'Panama-City-Florida': 'g34533',
            'North-Port-Florida': 'g34500',
            'Altamonte-Springs-Florida': 'g34036',
            'Greenacres-Florida': 'g34276',
            'Parkland-Florida': 'g34535',
            'Dunedin-Florida': 'g34211',
            'Sanford-Florida': 'g34631',
            'Winter-Haven-Florida': 'g34788',
            'Coral-Gables-Florida': 'g34190',
            'Lakewood-Ranch-Florida': 'g34458',
            'Clermont-Florida': 'g34162',
            'Sebastian-Florida': 'g34642',
            'Winter-Garden-Florida': 'g34789',
            'Royal-Palm-Beach-Florida': 'g34624',
            'Doral-Florida': 'g34208',
            'Pinecrest-Florida': 'g34544',
            'Cutler-Bay-Florida': 'g34196',
            'Winter-Park-Florida': 'g34790',
            'Casselberry-Florida': 'g34147',
            'Cooper-City-Florida': 'g34186',
            'Winter-Springs-Florida': 'g34791',
            'Safety-Harbor-Florida': 'g34625',
            'Ocoee-Florida': 'g34502',
            'Longwood-Florida': 'g34469',
            'Aventura-Florida': 'g34053',
            'Lighthouse-Point-Florida': 'g34464',
            'Maitland-Florida': 'g34475',
            'Oviedo-Florida': 'g34522',
            'Lauderdale-Lakes-Florida': 'g34460',
            'St-Cloud-Florida': 'g34612',
            'Crestview-Florida': 'g34194',
            'Venice-Florida': 'g34750',
            'Hallandale-Beach-Florida': 'g34287',
            'Haines-City-Florida': 'g34286',
            'Mount-Dora-Florida': 'g34491',
            'Key-West-Florida': 'g34451',
            'Naples-Florida': 'g34493',
            
            # Georgia
            'Atlanta-Georgia': 'g35805',
            'Columbus-Georgia': 'g35859',
            'Augusta-Georgia': 'g35814',
            'Savannah-Georgia': 'g35998',
            'Athens-Georgia': 'g35802',
            'Sandy-Springs-Georgia': 'g35993',
            'Roswell-Georgia': 'g35983',
            'Macon-Georgia': 'g35932',
            'Johns-Creek-Georgia': 'g35898',
            'Albany-Georgia': 'g35789',
            'Warner-Robins-Georgia': 'g36062',
            'Alpharetta-Georgia': 'g35794',
            'Marietta-Georgia': 'g35941',
            'Valdosta-Georgia': 'g36047',
            'Smyrna-Georgia': 'g36008',
            'Dunwoody-Georgia': 'g35869',
            'Rome-Georgia': 'g35981',
            'East-Point-Georgia': 'g35873',
            'Peachtree-Corners-Georgia': 'g35968',
            'Gainesville-Georgia': 'g35885',
            'Hinesville-Georgia': 'g35896',
            'Kennesaw-Georgia': 'g35906',
            'Newnan-Georgia': 'g35958',
            'Peachtree-City-Georgia': 'g35967',
            'Lawrenceville-Georgia': 'g35917',
            'Douglasville-Georgia': 'g35867',
            'Stockbridge-Georgia': 'g36020',
            'Carrollton-Georgia': 'g35846',
            'Dalton-Georgia': 'g35863',
            'Woodstock-Georgia': 'g36078',
            'Cartersville-Georgia': 'g35847',
            'Statesboro-Georgia': 'g36016',
            'Decatur-Georgia': 'g35865',
            'McDonough-Georgia': 'g35948',
            'Acworth-Georgia': 'g35784',
            'Powder-Springs-Georgia': 'g35976',
            'Canton-Georgia': 'g35844',
            'Pooler-Georgia': 'g35974',
            'St-Marys-Georgia': 'g36019',
            'Tifton-Georgia': 'g36033',
            'Griffin-Georgia': 'g35889',
            'Milledgeville-Georgia': 'g35953',
            'LaGrange-Georgia': 'g35914',
            'Thomasville-Georgia': 'g36029',
            'Union-City-Georgia': 'g36044',
            'Conyers-Georgia': 'g35861',
            'Covington-Georgia': 'g35862',
            'Fairburn-Georgia': 'g35878',
            'Americus-Georgia': 'g35796',
            'Kingsland-Georgia': 'g35909',
            'Cedartown-Georgia': 'g35851',
            'Toccoa-Georgia': 'g36034',
            'Moultrie-Georgia': 'g35956',
            'Bainbridge-Georgia': 'g35817',
            'Waycross-Georgia': 'g36067',
            'Commerce-Georgia': 'g35858',
            'Jefferson-Georgia': 'g35897',
            'Cordele-Georgia': 'g35861',
            'Dublin-Georgia': 'g35868',
            'Vidalia-Georgia': 'g36052',
            'Jesup-Georgia': 'g35899',
            'Fitzgerald-Georgia': 'g35882',
            'Thomaston-Georgia': 'g36030',
            'Cairo-Georgia': 'g35841',
            'Calhoun-Georgia': 'g35842',
            'Blue-Ridge-Georgia': 'g35830',
            'Helen-Georgia': 'g35894',
            'Dahlonega-Georgia': 'g35864',
            'Tybee-Island-Georgia': 'g36042',
            'Jekyll-Island-Georgia': 'g35898',
            'St-Simons-Island-Georgia': 'g36018',
            'Sea-Island-Georgia': 'g36001',
            
            # Hawaii
            'Honolulu-Hawaii': 'g60982',
            'Pearl-City-Hawaii': 'g61011',
            'Hilo-Hawaii': 'g60977',
            'Kailua-Kona-Hawaii': 'g60989',
            'Waipahu-Hawaii': 'g61044',
            'Kaneohe-Hawaii': 'g60993',
            'Mililani-Hawaii': 'g61003',
            'Kahului-Hawaii': 'g60986',
            'Ewa-Beach-Hawaii': 'g60967',
            'Kihei-Hawaii': 'g60998',
            'Mililani-Mauka-Hawaii': 'g61004',
            'Wahiawa-Hawaii': 'g61041',
            'Halawa-Hawaii': 'g60974',
            'Wailuku-Hawaii': 'g61045',
            'Kapaa-Hawaii': 'g60994',
            'Schofield-Barracks-Hawaii': 'g61020',
            'Kailua-Hawaii': 'g60988',
            'Lahaina-Hawaii': 'g61000',
            'Lihue-Hawaii': 'g61001',
            'Kaunakakai-Hawaii': 'g60997',
            'Hana-Hawaii': 'g60975',
            'Volcano-Hawaii': 'g61040',
            'Princeville-Hawaii': 'g61014',
            'Makawao-Hawaii': 'g61001',
            'Paia-Hawaii': 'g61010',
            'Koloa-Hawaii': 'g61000',
            'Hanapepe-Hawaii': 'g60975',
            'Waimea-Hawaii': 'g61046',
            'Kamuela-Hawaii': 'g60991',
            'Naalehu-Hawaii': 'g61007',
            'Captain-Cook-Hawaii': 'g60958',
            'Pahoa-Hawaii': 'g61009',
            'Kilauea-Hawaii': 'g60999',
            'Hanalei-Hawaii': 'g60975',
            'Kaanapali-Hawaii': 'g60983',
            'Wailea-Hawaii': 'g61043',
            'Kapalua-Hawaii': 'g60993',
            'Poipu-Hawaii': 'g61013',
            
            # Idaho
            'Boise-Idaho': 'g35394',
            'Meridian-Idaho': 'g35451',
            'Nampa-Idaho': 'g35465',
            'Idaho-Falls-Idaho': 'g35415',
            'Pocatello-Idaho': 'g35484',
            'Caldwell-Idaho': 'g35399',
            'Coeur-d-Alene-Idaho': 'g35408',
            'Twin-Falls-Idaho': 'g35524',
            'Lewiston-Idaho': 'g35441',
            'Post-Falls-Idaho': 'g35485',
            'Rexburg-Idaho': 'g35494',
            'Moscow-Idaho': 'g35460',
            'Eagle-Idaho': 'g35412',
            'Ketchum-Idaho': 'g35433',
            'Sandpoint-Idaho': 'g35502',
            'Chubbuck-Idaho': 'g35407',
            'Hayden-Idaho': 'g35414',
            'Mountain-Home-Idaho': 'g35462',
            'Burley-Idaho': 'g35398',
            'Ammon-Idaho': 'g35391',
            'Blackfoot-Idaho': 'g35395',
            'Garden-City-Idaho': 'g35413',
            'Jerome-Idaho': 'g35430',
            'Rathdrum-Idaho': 'g35492',
            'Payette-Idaho': 'g35481',
            'Hailey-Idaho': 'g35414',
            'Preston-Idaho': 'g35488',
            'Weiser-Idaho': 'g35531',
            'Rupert-Idaho': 'g35498',
            'Soda-Springs-Idaho': 'g35511',
            'Middleton-Idaho': 'g35452',
            'Fruitland-Idaho': 'g35412',
            'Rigby-Idaho': 'g35495',
            'Salmon-Idaho': 'g35501',
            'Driggs-Idaho': 'g35411',
            'Gooding-Idaho': 'g35413',
            'Sun-Valley-Idaho': 'g35518',
            'McCall-Idaho': 'g35450',
            
            # Illinois
            'Chicago-Illinois': 'g35805',
            'Aurora-Illinois': 'g35826',
            'Rockford-Illinois': 'g36072',
            'Joliet-Illinois': 'g36012',
            'Naperville-Illinois': 'g36049',
            'Springfield-Illinois': 'g36106',
            'Peoria-Illinois': 'g36058',
            'Elgin-Illinois': 'g35956',
            'Waukegan-Illinois': 'g36149',
            'Cicero-Illinois': 'g35871',
            'Champaign-Illinois': 'g35858',
            'Bloomington-Illinois': 'g35845',
            'Arlington-Heights-Illinois': 'g35823',
            'Evanston-Illinois': 'g35963',
            'Decatur-Illinois': 'g35923',
            'Schaumburg-Illinois': 'g36085',
            'Bolingbrook-Illinois': 'g35849',
            'Palatine-Illinois': 'g36053',
            'Skokie-Illinois': 'g36099',
            'Des-Plaines-Illinois': 'g35928',
            'Orland-Park-Illinois': 'g36052',
            'Tinley-Park-Illinois': 'g36139',
            'Oak-Lawn-Illinois': 'g36048',
            'Berwyn-Illinois': 'g35839',
            'Mount-Prospect-Illinois': 'g36042',
            'Normal-Illinois': 'g36047',
            'Wheaton-Illinois': 'g36161',
            'Hoffman-Estates-Illinois': 'g35994',
            'Oak-Park-Illinois': 'g36049',
            'Downers-Grove-Illinois': 'g35934',
            'Elmhurst-Illinois': 'g35960',
            'Glenview-Illinois': 'g35980',
            'DeKalb-Illinois': 'g35924',
            'Lombard-Illinois': 'g36028',
            'Belleville-Illinois': 'g35834',
            'Moline-Illinois': 'g36038',
            'Elmwood-Park-Illinois': 'g35961',
            'Niles-Illinois': 'g36046',
            'Buffalo-Grove-Illinois': 'g35854',
            'Wheeling-Illinois': 'g36159',
            'Park-Ridge-Illinois': 'g36055',
            'Addison-Illinois': 'g35813',
            'Calumet-City-Illinois': 'g35856',
            'Glendale-Heights-Illinois': 'g35979',
            'Northbrook-Illinois': 'g36047',
            'Urbana-Illinois': 'g36147',
            'Crystal-Lake-Illinois': 'g35921',
            'Quincy-Illinois': 'g36069',
            'Streamwood-Illinois': 'g36111',
            'Carol-Stream-Illinois': 'g35857',
            'Romeoville-Illinois': 'g36074',
            'Rock-Island-Illinois': 'g36071',
            'Plainfield-Illinois': 'g36062',
            'Carpentersville-Illinois': 'g35857',
            'Hanover-Park-Illinois': 'g35990',
            'Wheeling-Illinois': 'g36159',
            'Danville-Illinois': 'g35922',
            'Highland-Park-Illinois': 'g35993',
            'Blue-Island-Illinois': 'g35847',
            'Granite-City-Illinois': 'g35983',
            'Alton-Illinois': 'g35816',
            'North-Chicago-Illinois': 'g36047',
            'Gurnee-Illinois': 'g35986',
            'Mundelein-Illinois': 'g36043',
            'Dolton-Illinois': 'g35930',
            'Cahokia-Illinois': 'g35855',
            'Galesburg-Illinois': 'g35975',
            'Bartlett-Illinois': 'g35829',
            'Batavia-Illinois': 'g35831',
            'Geneva-Illinois': 'g35977',
            'Woodstock-Illinois': 'g36166',
        }
            

    def extract_hotel_urls_from_listing(self, listing_url: str) -> List[str]:
        """Extract individual hotel URLs from a city listing page"""
        hotel_urls = []
        page = 1
        max_pages = 50  # Limit to prevent infinite loops
        
        while page <= max_pages:
            try:
                if page == 1:
                    url = listing_url
                else:
                    # TripAdvisor pagination format
                    url = listing_url.replace('.html', f'-oa{(page-1)*30}.html')
                
                self.logger.info(f"Scraping hotel URLs from page {page}: {url}")
                self.driver.get(url)
                time.sleep(random.uniform(3, 7))
                
                # Wait for hotel listings to load
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-target='hotels-list']")))
                except TimeoutException:
                    self.logger.warning(f"No hotel listings found on page {page}")
                    break
                
                # Extract hotel URLs
                hotel_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/Hotel_Review-']")
                page_urls = []
                
                for element in hotel_elements:
                    href = element.get_attribute('href')
                    if href and '/Hotel_Review-' in href:
                        full_url = urljoin('https://www.tripadvisor.com', href)
                        if full_url not in hotel_urls:
                            hotel_urls.append(full_url)
                            page_urls.append(full_url)
                
                self.logger.info(f"Found {len(page_urls)} hotels on page {page}")
                
                # Check if there's a next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next page']")
                    if 'disabled' in next_button.get_attribute('class') or not next_button.is_enabled():
                        break
                except NoSuchElementException:
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error extracting URLs from page {page}: {e}")
                break
        
        self.logger.info(f"Total hotels found: {len(hotel_urls)}")
        return hotel_urls

    def extract_tripadvisor_id(self, url: str) -> str:
        """Extract TripAdvisor hotel ID from URL"""
        match = re.search(r'Hotel_Review-g\d+-d(\d+)', url)
        return match.group(1) if match else ""

    def extract_location_data(self) -> Dict:
        """Extract location information from hotel page"""
        location_data = {
            'city': '',
            'address': '',
            'latitude': 0.0,
            'longitude': 0.0
        }
        
        try:
            # Extract address
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-target='hotel-address']")
            if address_elements:
                location_data['address'] = address_elements[0].text.strip()
            
            # Extract city from breadcrumbs or address
            breadcrumb_elements = self.driver.find_elements(By.CSS_SELECTOR, ".breadcrumbs a")
            if len(breadcrumb_elements) >= 2:
                location_data['city'] = breadcrumb_elements[-2].text.strip()
            
            # Extract coordinates from page source or map data
            page_source = self.driver.page_source
            coord_match = re.search(r'"latitude":([-\d.]+),"longitude":([-\d.]+)', page_source)
            if coord_match:
                location_data['latitude'] = float(coord_match.group(1))
                location_data['longitude'] = float(coord_match.group(2))
                
        except Exception as e:
            self.logger.error(f"Error extracting location data: {e}")
            
        return location_data

    def extract_ratings_breakdown(self) -> Dict:
        """Extract detailed ratings breakdown"""
        ratings = {
            'location_rating': 0.0,
            'cleanliness_rating': 0.0,
            'service_rating': 0.0,
            'value_rating': 0.0,
            'rooms_rating': 0.0,
            'sleep_quality_rating': 0.0
        }
        
        try:
            # Look for ratings breakdown section
            rating_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-target='review-rating-filter']")
            
            rating_mapping = {
                'location': 'location_rating',
                'cleanliness': 'cleanliness_rating',
                'service': 'service_rating',
                'value': 'value_rating',
                'rooms': 'rooms_rating',
                'sleep quality': 'sleep_quality_rating'
            }
            
            for element in rating_elements:
                text = element.text.lower()
                for key, field in rating_mapping.items():
                    if key in text:
                        rating_match = re.search(r'(\d+\.?\d*)', text)
                        if rating_match:
                            ratings[field] = float(rating_match.group(1))
                            
        except Exception as e:
            self.logger.error(f"Error extracting ratings breakdown: {e}")
            
        return ratings

    def extract_management_responses(self) -> Dict:
        """Extract management response information"""
        response_data = {
            'has_management_response': False,
            'management_response_date': '',
            'management_response_text': ''
        }
        
        try:
            # Look for management responses in reviews
            management_responses = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-target='management-response']")
            
            if management_responses:
                response_data['has_management_response'] = True
                latest_response = management_responses[0]  # Get the most recent one
                
                # Extract date
                date_element = latest_response.find_elements(By.CSS_SELECTOR, ".date")
                if date_element:
                    response_data['management_response_date'] = date_element[0].text.strip()
                
                # Extract response text
                text_element = latest_response.find_elements(By.CSS_SELECTOR, ".response-text")
                if text_element:
                    response_data['management_response_text'] = text_element[0].text.strip()
                    
        except Exception as e:
            self.logger.error(f"Error extracting management responses: {e}")
            
        return response_data

    def extract_competitor_hotels(self) -> List[str]:
        """Extract competitor/similar hotels"""
        competitors = []
        
        try:
            # Look for "Similar Hotels" or "Hotels Nearby" section
            similar_hotel_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-target='similar-hotels'] a")
            
            for element in similar_hotel_elements:
                hotel_name = element.text.strip()
                if hotel_name and hotel_name not in competitors:
                    competitors.append(hotel_name)
                    
        except Exception as e:
            self.logger.error(f"Error extracting competitor hotels: {e}")
            
        return competitors

    def scrape_hotel_details(self, hotel_url: str) -> HotelData:
        """Scrape detailed information from a single hotel page"""
        hotel_data = HotelData()
        hotel_data.hotel_url = hotel_url
        hotel_data.tripadvisor_id = self.extract_tripadvisor_id(hotel_url)
        hotel_data.scrape_timestamp = datetime.now().isoformat()
        
        try:
            self.logger.info(f"Scraping hotel: {hotel_url}")
            self.driver.get(hotel_url)
            time.sleep(random.uniform(5, 10))
            
            # Wait for main content to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
            
            # Extract hotel name
            try:
                hotel_name_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                hotel_data.hotel_name = hotel_name_element.text.strip()
            except NoSuchElementException:
                self.logger.warning("Hotel name not found")
            
            # Extract location data
            location_data = self.extract_location_data()
            hotel_data.city = location_data['city']
            hotel_data.address = location_data['address']
            hotel_data.latitude = location_data['latitude']
            hotel_data.longitude = location_data['longitude']
            
            # Extract overall rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-target='review-rating'] span")
                rating_text = rating_element.get_attribute('class')
                # Parse rating from class name (e.g., "ui_bubble_rating bubble_45" means 4.5)
                rating_match = re.search(r'bubble_(\d+)', rating_text)
                if rating_match:
                    hotel_data.overall_rating_score = float(rating_match.group(1)) / 10
            except NoSuchElementException:
                pass
            
            # Extract total reviews
            try:
                reviews_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-target='review-count']")
                reviews_text = reviews_element.text
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    hotel_data.total_reviews = int(reviews_match.group(1).replace(',', ''))
            except NoSuchElementException:
                pass
            
            # Extract star rating
            try:
                star_elements = self.driver.find_elements(By.CSS_SELECTOR, ".hotels-hotel-review-about-addendum-stars")
                if star_elements:
                    star_text = star_elements[0].get_attribute('class')
                    star_match = re.search(r'star_(\d+)', star_text)
                    if star_match:
                        hotel_data.official_star_rating = f"{star_match.group(1)} stars"
            except Exception:
                pass
            
            # Extract ranking information
            try:
                ranking_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-target='hotel-ranking']")
                if ranking_elements:
                    ranking_text = ranking_elements[0].text
                    hotel_data.city_ranking = ranking_text
            except Exception:
                pass
            
            # Extract detailed ratings
            ratings_data = self.extract_ratings_breakdown()
            hotel_data.location_rating = ratings_data['location_rating']
            hotel_data.cleanliness_rating = ratings_data['cleanliness_rating']
            hotel_data.service_rating = ratings_data['service_rating']
            hotel_data.value_rating = ratings_data['value_rating']
            hotel_data.rooms_rating = ratings_data['rooms_rating']
            hotel_data.sleep_quality_rating = ratings_data['sleep_quality_rating']
            
            # Extract management response data
            management_data = self.extract_management_responses()
            hotel_data.has_management_response = management_data['has_management_response']
            hotel_data.management_response_date = management_data['management_response_date']
            hotel_data.management_response_text = management_data['management_response_text']
            
            # Extract competitor hotels
            hotel_data.competitor_hotels = self.extract_competitor_hotels()
            
        except Exception as e:
            self.logger.error(f"Error scraping hotel {hotel_url}: {e}")
            
        return hotel_data

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV file"""
        if not filename:
            filename = f"tripadvisor_hotels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.scraped_hotels:
            self.logger.warning("No data to save")
            return
        
        fieldnames = [
            'hotel_name', 'hotel_url', 'tripadvisor_id', 'city', 'address', 
            'latitude', 'longitude', 'official_star_rating', 'guest_star_rating',
            'overall_rating_score', 'total_reviews', 'city_ranking', 'region_ranking',
            'location_rating', 'cleanliness_rating', 'service_rating', 'value_rating',
            'rooms_rating', 'sleep_quality_rating', 'has_management_response',
            'management_response_date', 'management_response_text', 'competitor_hotels',
            'scrape_timestamp'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for hotel in self.scraped_hotels:
                row = asdict(hotel)
                row['competitor_hotels'] = '|'.join(row['competitor_hotels'])  # Join list items
                writer.writerow(row)
        
        self.logger.info(f"Data saved to {filename}")

    def save_to_json(self, filename: str = None):
        """Save scraped data to JSON file"""
        if not filename:
            filename = f"tripadvisor_hotels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not self.scraped_hotels:
            self.logger.warning("No data to save")
            return
        
        data = [asdict(hotel) for hotel in self.scraped_hotels]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Data saved to {filename}")

    def run_scraper(self, max_hotels: int = None):
        """Main scraper execution"""
        try:
            self.setup_driver()
            
            # Get city URLs
            city_urls = self.get_usa_cities_urls()
            
            total_scraped = 0
            
            for city_url in city_urls:
                try:
                    self.logger.info(f"Processing city: {city_url}")
                    
                    # Get hotel URLs from city listing
                    hotel_urls = self.extract_hotel_urls_from_listing(city_url)
                    
                    # Scrape individual hotels
                    for hotel_url in hotel_urls:
                        if max_hotels and total_scraped >= max_hotels:
                            self.logger.info(f"Reached maximum hotels limit: {max_hotels}")
                            break
                            
                        try:
                            hotel_data = self.scrape_hotel_details(hotel_url)
                            if hotel_data.hotel_name:  # Only add if we got valid data
                                self.scraped_hotels.append(hotel_data)
                                total_scraped += 1
                                self.logger.info(f"Scraped hotel {total_scraped}: {hotel_data.hotel_name}")
                            
                            # Random delay between requests
                            time.sleep(random.uniform(8, 15))
                            
                        except Exception as e:
                            self.logger.error(f"Error processing hotel {hotel_url}: {e}")
                            continue
                    
                    if max_hotels and total_scraped >= max_hotels:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error processing city {city_url}: {e}")
                    continue
            
            # Save results
            self.save_to_csv()
            self.save_to_json()
            
            self.logger.info(f"Scraping completed. Total hotels scraped: {len(self.scraped_hotels)}")
            
        except Exception as e:
            self.logger.error(f"Critical error in scraper: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main execution function"""
    
    # Proxy configuration examples:
    
    # Option 1: Zyte Proxy API
    zyte_proxy_config = {
        'zyte_api_key': 'YOUR_ZYTE_API_KEY_HERE'
    }
    
    # Option 2: Custom proxy
    custom_proxy_config = {
        'proxy_host': 'your.proxy.host',
        'proxy_port': '8080',
        'proxy_username': 'username',  # Optional
        'proxy_password': 'password'   # Optional
    }
    
    # Choose your proxy configuration
    proxy_config = zyte_proxy_config  # or custom_proxy_config
    
    # Initialize scraper
    scraper = TripAdvisorScraper(
        use_proxy=True,  # Set to False to disable proxy
        proxy_config=proxy_config
    )
    
    # Run scraper
    try:
        scraper.run_scraper(max_hotels=100)  # Set limit or None for all hotels
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        if scraper.scraped_hotels:
            scraper.save_to_csv()
            scraper.save_to_json()
    except Exception as e:
        print(f"Scraping failed: {e}")


if __name__ == "__main__":
    main()