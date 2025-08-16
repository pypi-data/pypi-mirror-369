from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
import logging
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException
)

class coin:
    def __init__(self, link):
        self.link = link
        options = Options()
        service = Service(log_path="NUL")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-logging-redirect")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-features=TranslateUI,Notification,MediaRouter,OptimizationHints")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--safebrowsing-disable-download-protection")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--remote-debugging-port=0")

        options.set_capability("pageLoadStrategy", "eager")

        os.environ["WDM_LOG_LEVEL"] = "0"
        os.environ["CHROME_LOG_FILE"] = os.devnull
        os.environ["PYTHONWARNINGS"] = "ignore"

        try:
            self.web = web = webdriver.Edge(options=options, service=service)
            self.wait = WebDriverWait(web, 10)
        except WebDriverException as e:
            logging.error(f"WebDriver initialization failed: {e}")
            self.web = None
            self.wait = None

    def get_text_with_retry(self, driver, by, value, wait, retries=3):
        for _ in range(retries):
            try:
                elem = wait.until(EC.visibility_of_element_located((by, value)))
                return elem.text
            except StaleElementReferenceException:
                time.sleep(0.5)
            except TimeoutException:
                break
            except Exception as e:
                logging.error(f"Error getting element text: {e}")
                break
        raise Exception("Element is persistently stale or not found")

    def give_price(self):
        if not self.web or not self.wait:
            return "WebDriver not initialized. Please check your browser setup."

        try:
            self.web.get(f"https://coinmarketcap.com/currencies/{self.link}/")
        except WebDriverException as e:
            return f"Failed to load CoinMarketCap page: {e}"

        wait = self.wait
        try:
            symbol = self.get_text_with_retry(self.web, By.XPATH, '//*[@id="section-coin-overview"]/div[1]/h1/div[1]/span', wait)
            price = self.get_text_with_retry(self.web, By.XPATH, '//*[@id="section-coin-overview"]/div[2]/span', wait)
            span_elem = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="section-coin-overview"]/div[2]/div/div/p')))
            span = span_elem.text
            arrow_color = span_elem.get_attribute("color")
            arrow_d = "↗️" if arrow_color == "green" else "↘️"
        except TimeoutException:
            return "Coin not found or page structure changed. Please check the coin name."
        except Exception as e:
            return f"Error extracting coin data: {e}"

        try:
            self.web.get(f"https://www.coinbase.com/en-gb/price/{self.link}")
            cap_elem = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div/div/main/section[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[2]/p')
                )
            )
            cap = cap_elem.text
            return f"{symbol} {price} {arrow_d} {span.replace('(1d)', '').strip()} Market Cap: {cap}"
        except TimeoutException:
            logging.warning("Could not find the market cap element. The page structure may have changed or it took too long to load.")
            return f"{symbol} {price} {arrow_d} {span.replace('(1d)', '').strip()} (Market Cap unavailable)"
        except Exception as e:
            return f"{symbol} {price} {arrow_d} {span.replace('(1d)', '').strip()} (Market Cap error: {e})"

if __name__ == "__main__":
    coin_name = "fdsfdf"
    coin_instance = coin(coin_name)
    print(coin_instance.give_price())