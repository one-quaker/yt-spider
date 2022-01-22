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


try:
    SEARCH_Q = sys.argv[1]
    print(f'{SEARCH_Q}')
except (Exception, ):
    print(f'Example: python {os.path.abspath(__file__).split(os.path.sep)[-1]} "rasperry pi"')
    sys.exit(1)


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


def get_element(selector, driver, click=False):
    print(f'waiting for {selector}')
    # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    if click:
        random_delay()
        print(f'click on {selector}')
        element.click()
    return element


def parse_like(val):
    valid_val = int(''.join([x for x in val if x.isdigit()]))
    return valid_val


def parse_date(val):
    import re
    regex = re.compile(r'^.*(\w{3})\s(\d{2}),\s(\d{4})$')
    match = regex.match(val)
    if match:
        date_str = '-'.join([match.group(1), match.group(2), match.group(3)])
        date_iso = datetime.strptime(date_str, '%b-%d-%Y').date().isoformat()
        return date_iso


def parse(driver):
    driver.get('https://youtube.com')

    search_input = get_element('input#search', driver)
    search_input.send_keys(SEARCH_Q)
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
        stat = {'like': parse_like(x[1]) for x in like_dislike_btn_row if x[1] and 'like' in x[1]}
        stat.update(i)

        info_row = driver.find_element_by_css_selector('div#info-text')
        stat['view'] = int(''.join([x for x in info_row.find_element_by_css_selector('div#count').text if x in string.digits]))
        raw_pub_date = info_row.find_element_by_css_selector('div#info-strings yt-formatted-string').text
        stat['pub_date'] = parse_date(raw_pub_date)
        print(stat)


try:
    parse(driver)
except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    driver.quit()
