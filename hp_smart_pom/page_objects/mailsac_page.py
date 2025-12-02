# page_objects/mailsac_page.py
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import log_step
import config

class MailsacPage:
    MAILSAC_URL = "https://mailsac.com"
    MAILBOX_PLACEHOLDER_XPATH = "//input[@placeholder='mailbox']"
    CHECK_MAIL_BTN_XPATH = "//button[normalize-space()='Check the mail!']"
    INBOX_ROW_XPATH = "//table[contains(@class,'inbox-table')]/tbody/tr[contains(@class,'clickable')][1]"
    EMAIL_BODY_CSS = "#emailBody"
    OTP_REGEX = r"\b(\d{4,8})\b"

    def __init__(self, headless=config.CHROME_HEADLESS, timeout=config.DEFAULT_TIMEOUT, poll_interval=config.POLL_INTERVAL, max_wait=config.OTP_MAX_WAIT):
        opts = webdriver.ChromeOptions()
        if headless:
            opts = webdriver.ChromeOptions()
        if headless:
           opts.add_argument('--headless=new')
        for arg in config.CHROME_BINARY_ARGS:
          opts.add_argument(arg)
        self.driver = webdriver.Chrome(options=opts)
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_wait = max_wait

    def open_mailsac(self):
        self.driver.get(self.MAILSAC_URL)
        log_step("Opened Mailsac website.")

    def fetch_otp(self, mailbox_local_part):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            mailbox_field = wait.until(EC.presence_of_element_located((By.XPATH, self.MAILBOX_PLACEHOLDER_XPATH)))
            mailbox_field.clear()
            mailbox_field.send_keys(mailbox_local_part)
            check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, self.CHECK_MAIL_BTN_XPATH)))
            check_btn.click()
            log_step("Opened Mailsac inbox.")
            start_time = time.time()

            while time.time() - start_time < self.max_wait:
                try:
                    email_row = WebDriverWait(self.driver, self.poll_interval).until(
                        EC.presence_of_element_located((By.XPATH, self.INBOX_ROW_XPATH))
                    )
                    email_row.click()
                    log_step("Clicked on first email row.")
                    break
                except:
                    self.driver.find_element(By.XPATH, self.CHECK_MAIL_BTN_XPATH).click()
                    log_step("Refreshed Mailsac inbox.", "INFO")
            body_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.EMAIL_BODY_CSS)))
            email_body = body_elem.text
            match = re.search(self.OTP_REGEX, email_body)
            if match:
                otp = match.group(1)
                log_step(f"Extracted OTP: {otp}")
                return otp
            else:
                log_step("OTP not found in email.", "FAIL")
                return None
        except Exception as e:
            log_step(f"Error fetching OTP: {e}", "FAIL")
            return None

    def quit(self):
        if self.driver:
            self.driver.quit()
            log_step("Closed Mailsac browser.")
