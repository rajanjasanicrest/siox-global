# utils/selenium_handler.py
 
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class SeleniumHandler:
    def __init__(self, headless=False):
        chrome_options = uc.ChromeOptions()

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--lang=en-US,en")

        width = random.choice([1920, 1366, 1600, 1440])
        height = random.choice([1080, 768, 900])
        chrome_options.add_argument(f"--window-size={width},{height}")

        # Set a common, realistic user-agent
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
 
        self.driver = uc.Chrome(options=chrome_options, version_main=137)

        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
        """)

    def simulate_user_behavior(self):
        actions = ActionChains(self.driver)
        # Simulate mouse movement
        try:
            actions.move_by_offset(random.randint(5, 100), random.randint(5, 100)).perform()
            self.driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
            time.sleep(random.uniform(1.5, 3.5))
        except:
            pass  # safe fallback

    def get_rendered_html(self, url, wait_time=3):
        self.driver.get(url)
        time.sleep(wait_time)  # optionally wait for JS to render
        self.simulate_user_behavior()
        html = self.driver.page_source
        return html

    def quit(self):
        self.driver.quit()