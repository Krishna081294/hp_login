# page_objects/hp_smart_app.py
from pywinauto import Desktop, keyboard
import time
from utils.logger import log_step
import config

class HpSmartApp:
    APP_LAUNCH_COMMAND = "{VK_LWIN}HP Smart{ENTER}"
    HP_SMART_WINDOW_RE = r".*HP Smart.*"
    MANAGE_ACCOUNT_BTN = dict(title="Manage HP Account", auto_id="HpcSignedOutIcon", control_type="Button")
    CREATE_ACCOUNT_BTN = dict(auto_id="HpcSignOutFlyout_CreateBtn", control_type="Button")

    def __init__(self, timeout=config.DEFAULT_TIMEOUT):
        self.desktop = Desktop(backend="uia")
        self.timeout = timeout
        self.main_win = None

    def launch(self):
        try:
            keyboard.send_keys(self.APP_LAUNCH_COMMAND)
            log_step("Sent keys to launch HP Smart app.")
            self.main_win = self.desktop.window(title_re=self.HP_SMART_WINDOW_RE)
            self.main_win.wait('exists visible enabled ready', timeout=self.timeout)
            self.main_win.set_focus()
            log_step("Focused HP Smart main window.")
        except Exception as e:
            log_step(f"Failed to launch/focus HP Smart window: {e}", "FAIL")
            raise

    def open_create_account(self):
        try:
            self.main_win.child_window(**self.MANAGE_ACCOUNT_BTN).wait('visible enabled ready', timeout=5).click_input()
            log_step("Clicked Manage HP Account button.")
            self.main_win.child_window(**self.CREATE_ACCOUNT_BTN).wait('visible enabled ready', timeout=5).click_input()
            log_step("Clicked Create Account button.")
            time.sleep(1)
        except Exception as e:
            log_step(f"Failed to open create account page: {e}", "FAIL")
            raise
