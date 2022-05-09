# from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
from twilio_utils import send_message, send_email
from constant import username, password, url_id
from bs4 import BeautifulSoup
import json

CURRENT_INTERVIEW_DATE = '2022-08-24'

def run_visa_scraper(url, interview_date_url):

    def get_earlier_appointment():
        '''Checks for changes in the site. Returns True if a change was found.'''
        # Getting the website to check
        driver.get(url)

        # Checking if website is still logged
        if driver.current_url == 'https://ais.usvisa-info.com/en-ca/niv/users/sign_in':
            print('Logging in.')
            # Clicking the first prompt, if there is one
            try:
                driver.find_element(by=By.XPATH, value='/html/body/div[6]/div[3]/div/button').click()
            except:
                pass
            # Filling the user and password
            user_box = driver.find_element(by=By.NAME, value='user[email]')
            user_box.send_keys(username)
            password_box = driver.find_element(by=By.NAME, value='user[password]')
            password_box.send_keys(password)
            # Clicking the checkbox
            driver.find_element(by=By.XPATH, value='//*[@id="new_user"]/div[3]/label/div').click()
            # Clicking 'Sign in'
            driver.find_element(by=By.XPATH, value='//*[@id="new_user"]/p[1]/input').click()
            
            # Waiting for the page to load.
            # 5 seconds may be ok for a computer, but it doesn't seem enough for the Raspberry Pi 4.
            time.sleep(10)

            # Logging to screen
            print('Logged in.')
        else:
            print('Already logged.')

        # Getting the website to check again
        # in case it was redirected to another website and
        # avoid using a timer for waiting for the login redirect. DIDN'T WORK
        driver.get(interview_date_url)
        date_list_json_str = BeautifulSoup(driver.page_source, 'html.parser').text
        date_list = json.loads(date_list_json_str)
        if len(date_list) > 0: 
            print('Earliest date: {interview_date}'.format(interview_date = date_list[0]))
        for interview_date_dic in date_list:
            if interview_date_dic['date'] < CURRENT_INTERVIEW_DATE:
                return interview_date_dic['date']

        return None

    # To run Chrome in a virtual display with xvfb (just in Linux)
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    seconds_between_checks = 10 * 60

    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless") # Comment for visualy debugging

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    while True:
        current_time = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        print(f'Starting a new check at {current_time}.')
        earlier_date = get_earlier_appointment()
        if earlier_date is not None:
            print('Earlier appointment date available. Notifying it.')
            send_message(earlier_date)
            send_email(earlier_date)
            # Closing the driver before quicking the script.
            driver.close()
            exit()
        else:
            # print(f'No change was found. Checking again in {seconds_between_checks} seconds.')
            # time.sleep(seconds_between_checks)
            for seconds_remaining in range(int(seconds_between_checks), 0, -1):
                sys.stdout.write('\r')
                sys.stdout.write(
                    f'No available slot is found. Checking again in {seconds_remaining} seconds.')
                sys.stdout.flush()
                time.sleep(1)
            print('\n')


def main():
    url = f'https://ais.usvisa-info.com/en-ca/niv/schedule/{url_id}/appointment'
    interview_date_url = f'https://ais.usvisa-info.com/en-ca/niv/schedule/{url_id}/appointment/days/95.json?appointments[expedite]=false'

    run_visa_scraper(url, interview_date_url)

if __name__ == "__main__":
    main()
