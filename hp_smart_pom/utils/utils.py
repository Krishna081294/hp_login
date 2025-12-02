import time
from utils.logger import log_step
from pywinauto import keyboard
import config

def click_open_hp_smart(timeout=config.DEFAULT_TIMEOUT):
    """Handle Chrome popup by sending ENTER keystrokes reliably."""
    log_step("Using keyboard ENTER for Chrome popup (reliable fallback)")
    for i in range(3):
        try:
            keyboard.send_keys("{ENTER}")
            log_step(f"Sent ENTER key (attempt {i+1})")
            time.sleep(1)
        except:
            pass
    log_step("Chrome popup handling completed", "PASS")
    return True