import json
import re
import scrapy
import urllib.parse

from urllib3 import HTTPResponse

from siox_hotel_scraper.utils.selenium_handler import SeleniumHandler

class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    # start_urls = ["https://www.tripadvisor.com/Hotels-g28931-Georgia-Hotels.html"]
    # start_urls = ["https://www.tripadvisor.com/Hotel_Review-g60814-d7216821-Reviews-Homewood_Suites_By_Hilton_Savannah_Historic_District_Riverfront-Savannah_Georgia.html"]

    start_urls = [
    "https://www.tripadvisor.com/Hotels-g29161-Altamonte_Springs_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g29171-Apopka_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g29180-Aventura_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34088-Boca_Raton_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34091-Bonita_Springs_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34094-Boynton_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g60786-Bradenton_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34118-Cape_Coral_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34125-Casselberry_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34141-Clearwater_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34142-Clermont_Lake_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34146-Coconut_Creek_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34150-Cooper_City_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34152-Coral_Gables_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34153-Coral_Springs_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34159-Crestview_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g1940088-Cutler_Bay_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34170-Davie_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34172-Daytona_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34178-DeLand_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34176-Deerfield_Beach_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34179-Delray_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34180-Deltona_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g680222-Doral_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34187-Dunedin_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34227-Fort_Lauderdale_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34230-Fort_Myers_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34233-Fort_Pierce_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34242-Gainesville_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34262-Greenacres_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34273-Haines_City_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34275-Hallandale_Beach_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34284-Hialeah_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34296-Hollywood_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g60739-Homestead_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g60805-Jacksonville_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34335-Jupiter_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34345-Key_West_Florida_Keys_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34352-Kissimmee_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g1497911-Lakewood_Ranch_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34373-Lakeland_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34380-Lauderdale_Lakes_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34382-Lauderhill_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34379-Largo_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34391-Lighthouse_Point_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34400-Longwood_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34412-Maitland_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34421-Margate_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34433-Melbourne_Brevard_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34438-Miami_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34439-Miami_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34440-Miami_Gardens_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34461-Mount_Dora_Lake_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34467-Naples_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34484-North_Lauderdale_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34485-North_Miami_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34486-North_Miami_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34488-North_Port_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34496-Ocala_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34499-Ocoee_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34515-Orlando_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34517-Ormond_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34521-Oviedo_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34528-Palm_Bay_Brevard_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34531-Palm_Beach_Gardens_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34534-Palm_Coast_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34542-Panama_City_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34544-Parkland_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34548-Pembroke_Pines_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34550-Pensacola_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34559-Pinecrest_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34561-Pinellas_Park_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34565-Plantation_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34567-Poinciana_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34571-Pompano_Beach_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34576-Port_Orange_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34580-Port_Saint_Lucie_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34596-Royal_Palm_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34598-Safety_Harbor_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34615-Sanford_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34618-Sarasota_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34625-Sebastian_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34601-Saint_Cloud_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34607-St_Petersburg_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34667-Sunrise_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34675-Tallahassee_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34677-Tamarac_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34678-Tampa_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g60751-Titusville_Brevard_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34705-Venice_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34727-Wellington_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34731-West_Palm_Beach_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34733-Weston_Broward_County_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34745-Winter_Garden_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34746-Winter_Haven_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34747-Winter_Park_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34748-Winter_Springs_Florida-Hotels.html",
    "https://www.tripadvisor.com/Hotels-g34495-Oakland_Park_Broward_County_Florida-Hotels.html"
    ]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Set headless=False to see the browser
    #     self.selenium_handler = SeleniumHandler(headless=False)

    
    # calstart_urls = [
    #     "https://www.tripadvisor.com/Hotels-g28926-California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32655-Los_Angeles_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60750-San_Diego_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33020-San_Jose_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60713-San_Francisco_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32414-Fresno_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32999-Sacramento_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32648-Long_Beach_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32810-Oakland_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32037-Bakersfield_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29092-Anaheim_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33043-Santa_Ana_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32978-Riverside_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33130-Stockton_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32530-Irvine_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32210-Chula_Vista_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32411-Fremont_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33009-San_Bernardino_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32724-Modesto_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32837-Oxnard_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32390-Fontana_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32743-Moreno_Valley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32513-Huntington_Beach_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32431-Glendale_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33047-Santa_Clarita_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32420-Garden_Grove_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32815-Oceanside_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32940-Rancho_Cucamonga_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33055-Santa_Rosa_Sonoma_County_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32607-Lancaster_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32349-Elk_Grove_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32248-Corona_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32848-Palmdale_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33002-Salinas_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32911-Pomona_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32480-Hayward_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32358-Escondido_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33182-Torrance_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33146-Sunnyvale_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32825-Orange_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32416-Fullerton_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32859-Pasadena_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60959-Thousand_Oaks_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33230-Visalia_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33093-Simi_Valley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32243-Concord_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32988-Roseville_Placer_County_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33046-Santa_Clara_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33212-Vallejo_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33224-Victorville_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32338-El_Monte_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32066-Berkeley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32308-Downey_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32253-Costa_Mesa_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32525-Inglewood_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33052-Santa_Monica_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32123-Burbank_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32764-Murrieta_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32962-Rialto_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33165-Temecula_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33051-Santa_Maria_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32331-El_Cajon_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32367-Fairfield_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29099-Antioch_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32201-Chico_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32952-Redding_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32205-Chino_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33031-San_Mateo_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32766-Napa_Napa_Valley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32952-Redding_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32819-Old_Station_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29091-American_Canyon_Napa_Valley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29093-Anderson_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32055-Bell_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32283-Davis_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32452-Greenfield_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32469-Half_Moon_Bay_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32523-Indian_Wells_Greater_Palm_Springs_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32242-Compton_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32846-Palm_Desert_Greater_Palm_Springs_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32627-Lincoln_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32196-Cerritos_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32923-Poway_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32107-Brea_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32656-Los_Banos_Merced_County_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32744-Morgan_Hill_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32847-Palm_Springs_Greater_Palm_Springs_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32645-Lompoc_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32982-Rohnert_Park_Sonoma_County_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32332-El_Centro_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32154-Campbell_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33010-San_Bruno_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32811-Oakley_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32057-Bell_Gardens_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32498-Hollister_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32842-Pacifica_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60868-Martinez_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g32215-Claremont_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33166-Temple_City_California-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g33252-West_Hollywood_California-Hotels.html"
    # ]

    # start_urls = [
    #     "https://www.tripadvisor.com/Hotels-g29161-Altamonte_Springs_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29171-Apopka_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g29180-Aventura_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34088-Boca_Raton_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34091-Bonita_Springs_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34094-Boynton_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60786-Bradenton_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34118-Cape_Coral_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34125-Casselberry_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34141-Clearwater_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34142-Clermont_Lake_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34146-Coconut_Creek_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34150-Cooper_City_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34152-Coral_Gables_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34153-Coral_Springs_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34159-Crestview_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g1940088-Cutler_Bay_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34170-Davie_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34172-Daytona_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34178-DeLand_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34176-Deerfield_Beach_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34179-Delray_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34180-Deltona_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g680222-Doral_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34187-Dunedin_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34227-Fort_Lauderdale_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34230-Fort_Myers_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34233-Fort_Pierce_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34242-Gainesville_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34262-Greenacres_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34273-Haines_City_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34275-Hallandale_Beach_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34284-Hialeah_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34296-Hollywood_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60739-Homestead_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60805-Jacksonville_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34335-Jupiter_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34345-Key_West_Florida_Keys_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34352-Kissimmee_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g1497911-Lakewood_Ranch_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34373-Lakeland_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34380-Lauderdale_Lakes_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34382-Lauderhill_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34379-Largo_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34391-Lighthouse_Point_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34400-Longwood_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34412-Maitland_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34421-Margate_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34433-Melbourne_Brevard_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34438-Miami_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34439-Miami_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34440-Miami_Gardens_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34461-Mount_Dora_Lake_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34467-Naples_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34484-North_Lauderdale_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34485-North_Miami_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34486-North_Miami_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34488-North_Port_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34496-Ocala_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34499-Ocoee_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34515-Orlando_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34517-Ormond_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34521-Oviedo_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34528-Palm_Bay_Brevard_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34531-Palm_Beach_Gardens_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34534-Palm_Coast_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34542-Panama_City_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34544-Parkland_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34548-Pembroke_Pines_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34550-Pensacola_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34559-Pinecrest_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34561-Pinellas_Park_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34565-Plantation_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34567-Poinciana_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34571-Pompano_Beach_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34576-Port_Orange_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34580-Port_Saint_Lucie_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34596-Royal_Palm_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34598-Safety_Harbor_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34615-Sanford_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34618-Sarasota_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34625-Sebastian_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34601-Saint_Cloud_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34607-St_Petersburg_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34667-Sunrise_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34675-Tallahassee_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34677-Tamarac_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34678-Tampa_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g60751-Titusville_Brevard_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34705-Venice_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34727-Wellington_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34731-West_Palm_Beach_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34733-Weston_Broward_County_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34745-Winter_Garden_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34746-Winter_Haven_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34747-Winter_Park_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34748-Winter_Springs_Florida-Hotels.html",
    #     "https://www.tripadvisor.com/Hotels-g34495-Oakland_Park_Broward_County_Florida-Hotels.html"
    # ]


    start_urls=["https://www.tripadvisor.com/Hotel_Review-g60814-d7216821-Reviews-Homewood_Suites_By_Hilton_Savannah_Historic_District_Riverfront-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d89754-Reviews-River_Street_Inn-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d564608-Reviews-Hilton_Garden_Inn_Savannah_Historic_District-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d123182-Reviews-The_Starling_Atlanta_Midtown_Curio_Collection_by_Hilton-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d240109-Reviews-DoubleTree_by_Hilton_Hotel_Savannah_Historic_District-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d16859065-Reviews-The_Candler_Hotel_Atlanta_Curio_Collection_by_Hilton-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d86238-Reviews-Courtland_Grand_Hotel-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d4191854-Reviews-Embassy_Suites_by_Hilton_Savannah_Historic_District-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d111340-Reviews-Embassy_Suites_by_Hilton_Atlanta_at_Centennial_Olympic_Park-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d18902571-Reviews-Hampton_Inn_Suites_Atlanta_Midtown-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g34792-d120635-Reviews-Chateau_Elan-Braselton_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d86777-Reviews-Hyatt_Regency_Savannah-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d13451617-Reviews-SpringHill_Suites_Atlanta_Downtown-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60898-d111374-Reviews-The_American_Hotel_Atlanta_Downtown_Tapestry_Collection_by_Hilton-Atlanta_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d89767-Reviews-Marriott_Savannah_Riverfront-Savannah_Georgia.html",
"https://www.tripadvisor.com/Hotel_Review-g60814-d86792-Reviews-The_DeSoto-Savannah_Georgia.html",]
    scrapped_urls = []
    try:
        with open('data/georgia.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            scrapped_urls = [x['tripadvisor_id'] for x in data]
    except FileNotFoundError:
        print("No previous data found, starting fresh.")




    try:
        with open('data/florida.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            scrapped_urls = [x['tripadvisor_id'] for x in data]
    except Exception as e:
        print(e)

    # def parse(self, response):
        
    #     hotel_list = response.xpath('//div[@data-automation="hotel-card-title"]//a/@href').getall()

    #     for hotel_link in hotel_list:
    #         tripadvisor_id = None  
    #         trpadv_id_match = re.search(r'd\d+', hotel_link)
    #         if trpadv_id_match:
    #             tripadvisor_id = trpadv_id_match.group()  
    #         if tripadvisor_id not in self.scrapped_urls:
    #             yield scrapy.Request(
    #                 response.urljoin(hotel_link),
    #                 self.parse_hotel,   
    #             )
    #         else:
    #             print('------------------------')
    #             print('Avoiding the link as scrapped once.')
    #             print('------------------------')

    #     next_page = response.xpath(
    #         '//a[@aria-label="Next page"]/@href'
    #     ).get()
    #     if next_page:
    #         yield response.follow(next_page, callback=self.parse) 

    # def parse_hotel(self, response):
    def parse(self, response):
        
        hotel_list = response.xpath('//div[@data-automation="hotel-card-title"]//a/@href').getall()

        for hotel_link in hotel_list:
            tripadvisor_id = None  
            trpadv_id_match = re.search(r'd\d+', hotel_link)
            if trpadv_id_match:
                tripadvisor_id = trpadv_id_match.group()  

            if tripadvisor_id not in self.scrapped_urls:
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
        # yield {
        #     'hotel_name': hotel_name,
        #     'hotel_url': hotel_url,
        #     'tripadvisor_id': tripadvisor_id,
        #     'address': address,
        #     'city': city,
        #     'state': state,
        #     'zip_code': zip_code,
        #     'region_rank': region_rank,
        #     'overall_rating': overall_rating,
        #     'latitude': latitude,
        #     'longitude': longitude,
        #     'total_reviews': total_reviews,
        #     'number_of_rooms': number_of_rooms,
        #     **ratings_dict,
        # }

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
            meta=meta
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

