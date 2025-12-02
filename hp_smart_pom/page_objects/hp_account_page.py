# page_objects/hp_account_page.py
from pywinauto import Desktop
import pyperclip
import time
from utils.logger import log_step
import config

class HpAccountPage:
    HP_ACCOUNT_WINDOW_RE = r".*HP account.*"
    FIRSTNAME_FIELD = dict(auto_id="firstName", control_type="Edit")
    LASTNAME_FIELD = dict(auto_id="lastName", control_type="Edit")
    EMAIL_FIELD = dict(auto_id="email", control_type="Edit")
    PASSWORD_FIELD = dict(auto_id="password", control_type="Edit")
    SIGNUP_BUTTON = dict(auto_id="sign-up-submit", control_type="Button")

    OTP_INPUT = dict(auto_id="code", control_type="Edit")
    OTP_SUBMIT_BUTTON = dict(auto_id="submit-code", control_type="Button")

    def __init__(self, timeout=config.DEFAULT_TIMEOUT):
        self.desktop = Desktop(backend="uia")
        self.timeout = timeout
        self.window = None

    def focus(self):
        try:
            self.window = self.desktop.window(title_re=self.HP_ACCOUNT_WINDOW_RE)
            self.window.wait('exists visible enabled ready', timeout=self.timeout)
            self.window.set_focus()
            log_step("Focused HP Account browser window.")
        except Exception as e:
            log_step(f"Failed to focus HP Account window: {e}", "FAIL")
            raise

    def fill_form(self, first_name, last_name, email, password):
        try:
            self.focus()
            self.window.child_window(**self.FIRSTNAME_FIELD).type_keys(first_name)
            self.window.child_window(**self.LASTNAME_FIELD).type_keys(last_name)
            self.window.child_window(**self.EMAIL_FIELD).type_keys(email)
            self.window.child_window(**self.PASSWORD_FIELD).type_keys(password)
            self.window.child_window(**self.SIGNUP_BUTTON).wait('visible enabled', timeout=5).click_input()
            log_step("Filled account form and clicked Create button.")
            time.sleep(3)
        except Exception as e:
            log_step(f"Failed to fill account form: {e}", "FAIL")
            raise

    def enter_otp_and_submit(self, otp):
        try:
            self.focus()
            otp_box = self.window.child_window(**self.OTP_INPUT)
            otp_box.wait('visible enabled', timeout=5)
            pyperclip.copy(otp)
            time.sleep(0.5)
            otp_box.click_input()
            otp_box.type_keys("^v")
            log_step("OTP pasted successfully.")
            self.window.child_window(**self.OTP_SUBMIT_BUTTON).wait('visible enabled', timeout=5).click_input()
            log_step("Clicked Verify button.")
            time.sleep(5)
        except Exception as e:
            log_step(f"OTP entry failed: {e}", "FAIL")
            raise
