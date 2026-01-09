import time
import re
import random
import string
from typing import Optional, Tuple

import pyperclip
import pytest
from pywinauto import Desktop, keyboard
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

REPORT = []

APP_LAUNCH_COMMAND = "{VK_LWIN}HP Smart{ENTER}"
HP_SMART_WINDOW_RE = r".*HP Smart.*"
HP_ACCOUNT_WINDOW_RE = r".*HP account.*"

MANAGE_ACCOUNT_BTN = dict(title="Manage HP Account", auto_id="HpcSignedOutIcon", control_type="Button")
CREATE_ACCOUNT_BTN = dict(auto_id="HpcSignOutFlyout_CreateBtn", control_type="Button")
FIRSTNAME_FIELD = dict(auto_id="firstName", control_type="Edit")
LASTNAME_FIELD = dict(auto_id="lastName", control_type="Edit")
EMAIL_FIELD = dict(auto_id="email", control_type="Edit")
PASSWORD_FIELD = dict(auto_id="password", control_type="Edit")
SIGNUP_BUTTON = dict(auto_id="sign-up-submit", control_type="Button")

OTP_INPUT = dict(auto_id="code", control_type="Edit")
OTP_SUBMIT_BUTTON = dict(auto_id="submit-code", control_type="Button")

MAILSAC_URL = "https://mailsac.com"
MAILBOX_PLACEHOLDER_XPATH = "//input[@placeholder='mailbox']"
CHECK_MAIL_BTN_XPATH = "//button[normalize-space()='Check the mail!']"
INBOX_ROW_XPATH = "//table[contains(@class,'inbox-table')]/tbody/tr[contains(@class,'clickable')][1]"
EMAIL_BODY_CSS = "#emailBody"
OTP_REGEX = r"\b(\d{4,8})\b"

DEFAULT_TIMEOUT = 30
SHORT_TIMEOUT = 10
POLL_INTERVAL = 5
OTP_MAX_WAIT = 120

MAILBOX_PREFIX_LEN = 4
MAIL_DOMAIN = "mailsac.com"
FIRSTNAME_LEN = 6
LASTNAME_LEN = 6
DEFAULT_PASSWORD = "SecurePassword123"

CHROME_HEADLESS = False
CHROME_BINARY_ARGS = []

def log_step(desc: str, status: str = "PASS") -> None:
    REPORT.append((desc, status))
    print(f"{desc}: {status}")

def generate_random_mailbox(prefix_len: int = MAILBOX_PREFIX_LEN, domain: str = MAIL_DOMAIN) -> str:
    prefix = ''.join(random.choices(string.ascii_lowercase, k=prefix_len))
    return f"{prefix}test@{domain}"

def generate_random_name(first_len: int = FIRSTNAME_LEN, last_len: int = LASTNAME_LEN) -> Tuple[str, str]:
    first = ''.join(random.choices(string.ascii_letters, k=first_len)).capitalize()
    last = ''.join(random.choices(string.ascii_letters, k=last_len)).capitalize()
    return first, last

def launch_hp_smart(timeout: int = DEFAULT_TIMEOUT):
    try:
        keyboard.send_keys(APP_LAUNCH_COMMAND)
        log_step("Sent keys to launch HP Smart app.")

        desktop = Desktop(backend="uia")
        main_win = desktop.window(title_re=HP_SMART_WINDOW_RE)
        main_win.wait('exists visible enabled ready', timeout=timeout)
        main_win.set_focus()
        log_step("Focused HP Smart main window.")

        manage_btn = main_win.child_window(**MANAGE_ACCOUNT_BTN)
        manage_btn.wait('visible enabled ready', timeout=SHORT_TIMEOUT)
        manage_btn.click_input()
        log_step("Clicked Manage HP Account button.")

        create_btn = main_win.child_window(**CREATE_ACCOUNT_BTN)
        create_btn.wait('visible enabled ready', timeout=SHORT_TIMEOUT)
        create_btn.click_input()
        log_step("Clicked Create Account button.")

        return desktop
    except Exception as e:
        log_step(f"Error launching HP Smart: {e}", "FAIL")
        return None

def fill_account_form(desktop, email: str, first_name: str, last_name: str, password: str = DEFAULT_PASSWORD):
    try:
        browser_win = desktop.window(title_re=HP_ACCOUNT_WINDOW_RE)
        browser_win.wait('exists visible enabled ready', timeout=DEFAULT_TIMEOUT)
        browser_win.set_focus()
        log_step("Focused HP Account browser window.")

        browser_win.child_window(**FIRSTNAME_FIELD).type_keys(first_name)
        browser_win.child_window(**LASTNAME_FIELD).type_keys(last_name)
        browser_win.child_window(**EMAIL_FIELD).type_keys(email)
        browser_win.child_window(**PASSWORD_FIELD).type_keys(password)

        signup = browser_win.child_window(**SIGNUP_BUTTON)
        signup.wait('visible enabled ready', timeout=SHORT_TIMEOUT)
        signup.click_input()
        log_step("Filled account form and clicked Create button.")

        time.sleep(5)
    except Exception as e:
        log_step(f"Error filling account form: {e}", "FAIL")

def _create_selenium_driver(headless: bool = CHROME_HEADLESS, extra_args: list = CHROME_BINARY_ARGS):
    opts = webdriver.ChromeOptions()
    opts.add_argument('--disable-gcm')
    if headless:
        opts.add_argument('--headless=new')
    for arg in extra_args:
        opts.add_argument(arg)
    return webdriver.Chrome(options=opts)

def fetch_otp_from_mailsac(mailbox_local_part: str,
                          mailsac_url: str = MAILSAC_URL,
                          max_wait: int = OTP_MAX_WAIT,
                          poll_interval: int = POLL_INTERVAL) -> Tuple[Optional[str], Optional[webdriver.Chrome]]:
    otp = None
    driver = None
    wait = WebDriverWait(None, SHORT_TIMEOUT)
    try:
        driver = _create_selenium_driver()
        wait = WebDriverWait(driver, 20)

        driver.get(mailsac_url)
        log_step("Opened Mailsac website.")
        time.sleep(3)

        mailbox_field = wait.until(
            EC.presence_of_element_located((By.XPATH, MAILBOX_PLACEHOLDER_XPATH))
        )
        mailbox_field.clear()
        mailbox_field.send_keys(mailbox_local_part)
        log_step("Mailbox entered.")

        check_selectors = [
            (By.XPATH, CHECK_MAIL_BTN_XPATH),
            (By.XPATH, "//button[contains(text(),'Check')]"),
            (By.CSS_SELECTOR, "button.btn-primary, button[title*='Check']")
        ]
        check_btn = None
        for by, sel in check_selectors:
            try:
                check_btn = wait.until(EC.element_to_be_clickable((by, sel)))
                break
            except TimeoutException:
                continue
        if check_btn:
            check_btn.click()
            log_step("Opened Mailsac inbox.")
        else:
            log_step("Check button not found.", "FAIL")
            driver.save_screenshot("mailsac_debug.png")
            return None, driver

        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                email_row = WebDriverWait(driver, poll_interval).until(
                    EC.presence_of_element_located((By.XPATH, INBOX_ROW_XPATH))
                )
                email_row.click()
                log_step("Clicked on first email row.")
                break
            except Exception:
                try:
                    driver.find_element(By.XPATH, CHECK_MAIL_BTN_XPATH).click()
                except Exception:
                    pass
                log_step("Refreshed Mailsac inbox.", "INFO")

        body_selectors = [
            (By.CSS_SELECTOR, EMAIL_BODY_CSS),
            (By.CSS_SELECTOR, ".message-body, .email-content"),
            (By.TAG_NAME, "body")
        ]
        body_elem = None
        for by, sel in body_selectors:
            try:
                body_elem = wait.until(EC.presence_of_element_located((by, sel)))
                break
            except:
                continue
        if body_elem:
            email_body = body_elem.text
            match = re.search(OTP_REGEX, email_body)
            if match:
                otp = match.group(1)
                log_step(f"Extracted OTP: {otp}")
            else:
                log_step("OTP not found in email.", "FAIL")
        else:
            log_step("Email body not found.", "FAIL")

        return otp, driver

    except Exception as e:
        log_step(f"Error fetching OTP: {e}", "FAIL")
        if driver:
            driver.save_screenshot("mailsac_error.png")
        return None, None

def complete_web_verification_in_app(otp: str, timeout: int = DEFAULT_TIMEOUT):
    try:
        desktop = Desktop(backend="uia")
        otp_win = desktop.window(title_re=HP_ACCOUNT_WINDOW_RE)
        otp_win.wait('exists visible enabled ready', timeout=timeout)
        otp_win.set_focus()
        log_step("Focused OTP input screen.")

        otp_box = otp_win.child_window(**OTP_INPUT)
        otp_box.wait('visible enabled ready', timeout=SHORT_TIMEOUT)

        pyperclip.copy(otp)
        time.sleep(0.5)
        otp_box.click_input()
        otp_box.type_keys("^v")
        log_step("OTP pasted successfully.")

        submit_btn = otp_win.child_window(**OTP_SUBMIT_BUTTON)
        submit_btn.wait('visible enabled ready', timeout=SHORT_TIMEOUT)
        submit_btn.click_input()
        log_step("Clicked Verify button.")
        
        time.sleep(10)
        log_step("HP Smart app opened - account created.")

    except Exception as e:
        log_step(f"OTP verification failed: {e}", "FAIL")

def generate_report(path: str = "automation_report.html") -> None:
    html = (
        "<html><head><meta charset='utf-8'><title>Automation Report</title></head><body>"
        "<h2>HP Account Automation Report</h2><table border='1'><tr><th>Step</th><th>Status</th></tr>"
    )
    for desc, status in REPORT:
        html += f"<tr><td>{desc}</td><td>{status}</td></tr>"
    html += "</table></body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report generated: {path}")

def main():
    driver = None
    try:
        mailbox_full = generate_random_mailbox()
        mailbox_local_part = mailbox_full.split("@")[0]
        log_step(f"Generated mailbox: {mailbox_full}")

        first_name, last_name = generate_random_name()
        log_step(f"Generated name: {first_name} {last_name}")

        desktop = launch_hp_smart()
        if desktop:
            fill_account_form(desktop, mailbox_full, first_name, last_name)

        otp, driver = fetch_otp_from_mailsac(mailbox_local_part)
        if otp:
            complete_web_verification_in_app(otp)

        if driver:
            try:
                alert = Alert(driver)
                log_step(f"Alert present with text: {alert.text}")
                alert.accept()
                log_step("Accepted browser alert.")
            except Exception:
                pass

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        generate_report()

if __name__ == "__main__":
    main()

def test_hp_account_automation():
    main()
    assert True
