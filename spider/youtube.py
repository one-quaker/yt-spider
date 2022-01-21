import os
import sys
import time
import traceback
import random
import string
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_driver():
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True

    options = Options()
    options.binary_location = os.environ['FIREFOX_BIN']
    if os.environ.get("HEADLESS") == "1":
        options.add_argument("--headless")

    firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    firefox_capabilities['binary'] = os.environ['FIREFOX_BIN']
    firefox_capabilities['acceptSslCerts'] = True

    driver_init = dict(
        executable_path=os.environ.get('GECKODRIVER_BIN'),
        desired_capabilities=firefox_capabilities,
        firefox_profile=profile,
        options=options,
    )
    if sys.platform == 'darwin':
        driver_init.pop('executable_path')
    driver = webdriver.Firefox(**driver_init)
    return driver


driver = get_driver()
driver.set_page_load_timeout(10)
driver.implicitly_wait(5)


def random_delay():
    delay = random.randint(200, 350) / 100.
    print(f'sleep {delay} seconds...')
    time.sleep(delay)


def get_element(selector, driver, wait=10, click=False):
    print(f'waiting for {selector}')
    # element = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    if click:
        random_delay()
        print(f'click on {selector}')
        element.click()
    return element


def parse(driver):
    driver.get('https://youtube.com')

    search_input = get_element('input#search', driver)
    search_input.send_keys('rasperry pi')
    search_ok = get_element('button#search-icon-legacy', driver, click=True)

    video_selector = 'ytd-video-renderer .ytd-video-renderer a#video-title'
    get_element(video_selector, driver)

    video_url_list = [
        dict(title=x.get_attribute('title'), url=x.get_attribute('href'))
        for x in driver.find_elements_by_css_selector(video_selector)
    ]

    for i in video_url_list:
        print(f'processing {i["url"]}')
        driver.get(i['url'])
        # skip_premium_button = get_element('div.ytd-mealbar-promo-renderer a.yt-simple-endpoint #button[aria-label="Skip trial"]', driver, click=True)
        like_dislike_btn_row = [(x.text, x.get_attribute('aria-label')) for x in driver.find_elements_by_css_selector('div#info yt-formatted-string#text')]
        stat = {'like': x[0] for x in like_dislike_btn_row if x[1] and 'like' in x[1]}

        info_row = driver.find_element_by_css_selector('div#info-text')
        stat['view'] = int(''.join([x for x in info_row.find_element_by_css_selector('div#count').text if x in string.digits]))
        raw_pub_date = datetime.strptime(info_row.find_element_by_css_selector('div#info-strings yt-formatted-string').text, '%b %d, %Y').isoformat()
        stat['pub_date'] = raw_pub_date.split('T')[0]
        print(stat)


try:
    parse(driver)
except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    driver.quit()
