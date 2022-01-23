import os
import sys
import time
import traceback
import random
import string
from datetime import datetime
from pprint import pprint

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
    if os.environ.get('HEADLESS') == '1':
        options.add_argument('--headless')

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
    if not val:
        return

    if val.lower() == 'no likes':
        return 0

    try:
        valid_val = int(''.join([x for x in val if x.isdigit()]))
        return valid_val
    except ValueError:
        print(f'like parse error, wrong value: {val}')


def parse_date(val):
    import re
    regex = re.compile(r'^.*(\w{3})\s(\d+),\s(\d{4})$')
    match = regex.match(val)
    if match:
        date_str = '-'.join([match.group(1), match.group(2), match.group(3)])
        date_valid = datetime.strptime(date_str, '%b-%d-%Y').strftime('%d-%m-%Y')
        return date_valid


def click_filter_button(driver):
    filter_button_selector = 'ytd-toggle-button-renderer.ytd-search-sub-menu-renderer'
    get_element(filter_button_selector, driver, click=True)  # click on filters button


def apply_filter_sort(driver):
    filter_selector = 'ytd-search-filter-group-renderer.ytd-search-sub-menu-renderer'
    filter_item_selector = 'yt-formatted-string.ytd-search-filter-renderer'

    click_filter_button(driver)
    filter_type = driver.find_elements_by_css_selector(filter_selector)[-4] # filter type row
    random_delay()
    filter_type.find_elements_by_css_selector(filter_item_selector)[0].click() # type video
    random_delay()

    click_filter_button(driver)
    filter_sort = driver.find_elements_by_css_selector(filter_selector)[-1] # filter sort row
    random_delay()
    filter_sort.find_elements_by_css_selector(filter_item_selector)[-2].click() # view count
    random_delay()


def parse(driver, scroll_count=3):
    result = []

    driver.get('https://youtube.com')

    search_input = get_element('input#search', driver)
    search_input.send_keys(SEARCH_Q)
    search_ok = get_element('button#search-icon-legacy', driver, click=True) # click on search button

    apply_filter_sort(driver)

    video_url_list = []
    video_selector = 'ytd-video-renderer .ytd-video-renderer a#video-title'

    for i in range(1, scroll_count + 1): # scroll page
        scroll_val = i * random.randint(1200, 1800)
        print(f'scroll page to {scroll_val}')
        driver.execute_script(f'window.scrollTo(0, {scroll_val})')
        random_delay()

        for x in driver.find_elements_by_css_selector(video_selector):
            data = dict(title=x.get_attribute('title'), url=x.get_attribute('href'))
            if data not in video_url_list:
                video_url_list.append(data)

    random.shuffle(video_url_list)
    for i in video_url_list:
        print(f'processing {i["url"]}')
        driver.get(i['url'])

        # skip_premium_button = get_element('div.ytd-mealbar-promo-renderer a.yt-simple-endpoint #button[aria-label="Skip trial"]', driver, click=True)
        stat = {}
        stat.update(i)

        like_dislike_btn_row = [(x.text, x.get_attribute('aria-label')) for x in driver.find_elements_by_css_selector('div#info yt-formatted-string#text')]
        raw_like = [x[1] for x in like_dislike_btn_row if x[1] and 'like' in x[1]][0]
        like = parse_like(raw_like)
        stat.update(dict(like=like, raw_like=raw_like))

        info_row = driver.find_element_by_css_selector('div#info-text')

        raw_view = info_row.find_element_by_css_selector('div#count').text
        stat['raw_view'] = raw_view
        stat['view'] = int(''.join([x for x in raw_view if x in string.digits]))

        raw_pub_date = info_row.find_element_by_css_selector('div#info-strings yt-formatted-string').text
        stat['raw_pub_date'] = raw_pub_date
        stat['pub_date'] = parse_date(raw_pub_date)

        print(stat)
        result.append(stat)
    return result


try:
    data = parse(driver)
    pprint(data)
except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    driver.quit()
