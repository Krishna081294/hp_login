"""
hp_smart_automation.py

Robust automation for HP Smart app using pywinauto.

Requirements:
- pywinauto
- pyperclip (optional if you want clipboard paste)
Run:
    python hp_smart_automation.py
"""

import time
import sys
from pathlib import Path
from typing import Optional

from pywinauto import keyboard
from pywinauto import Desktop
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError, find_windows

# -------------------------
# Configuration
# -------------------------
class Config:
    START_MENU_SEARCH = "HP Smart"
    APP_TITLE_RE = r".*HP Smart.*"        # top-level app window regex
    BROWSER_TITLE_RE = r".*Chrome.*|.*Chromium.*|.*Microsoft Edge.*"  # popup browser
    LAUNCH_WAIT = 20
    DEFAULT_TIMEOUT = 30
    RETRY_INTERVAL = 1
    MAX_RETRIES = 30

    # Credentials used for the popup login (change safely)
    MAIL_USERNAME = "test1202@mailsac.com"
    MAIL_PASSWORD = "Ascendion@12345"


# -------------------------
# Simple logger
# -------------------------
def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


# -------------------------
# Utilities
# -------------------------
def connect_app_with_retry(title_re: str, timeout: int = Config.DEFAULT_TIMEOUT) -> Optional[Application]:
    """Try to connect to an application window by title regex with retries."""
    app = Application(backend="uia")
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            app.connect(title_re=title_re)
            log(f"Connected to app window matching: {title_re}")
            return app
        except ElementNotFoundError:
            time.sleep(Config.RETRY_INTERVAL)
    log(f"Failed to connect to any window matching: {title_re}")
    return None


def find_browser_window(desktop: Desktop, title_re: str = Config.BROWSER_TITLE_RE, timeout: int = Config.DEFAULT_TIMEOUT):
    """Return the first browser window desktop can find that matches title regex."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            win = desktop.window(title_re=title_re)
            # ensure window exists & is ready
            win.wait("exists ready visible enabled", timeout=2)
            log(f"Found browser window: {win.window_text()}")
            return win
        except Exception:
            # enumerate windows occasionally for debugging
            time.sleep(1)
    log("Browser window not found within timeout.")
    return None


def press_start_and_open_app(search_text: str = Config.START_MENU_SEARCH, initial_wait: int = Config.LAUNCH_WAIT):
    """Open Start menu, type the app name and press Enter to start the app."""
    log(f"Launching '{search_text}' via Start menu...")
    keyboard.send_keys("{VK_LWIN}")
    time.sleep(0.8)
    keyboard.send_keys(search_text)
    time.sleep(0.8)
    keyboard.send_keys("{ENTER}")
    log("Start command sent. Waiting for app to start...")
    time.sleep(initial_wait)


# -------------------------
# Page operations
# -------------------------
def click_manage_and_signin(main_win):
    """Click Manage HP Account and then click Sign in / Create account as available."""
    try:
        main_win.wait("exists visible enabled ready", timeout=Config.DEFAULT_TIMEOUT)
        main_win.set_focus()
        log("Main app window ready and focused.")

        # Manage HP Account
        manage_btn = main_win.child_window(title="Manage HP Account", control_type="Button")
        manage_btn.wait("visible enabled ready", timeout=10)
        manage_btn.click_input()
        log("Clicked 'Manage HP Account'.")
        time.sleep(2)

        # Sign in (there might be variation: 'Sign in' or 'Sign In' etc.)
        try:
            sign_btn = main_win.child_window(title_re="Sign in|Sign In|Sign", control_type="Button")
            sign_btn.wait("visible enabled ready", timeout=8)
            sign_btn.click_input()
            log("Clicked Sign in button inside app.")
        except Exception:
            # fallback: try a Create / Manage button if Sign in not found
            log("Sign in button not found by exact title. Attempting alternative Create button.")
            try:
                create_btn = main_win.child_window(control_type="Button", auto_id="HpcSignOutFlyout_CreateBtn")
                create_btn.wait("visible enabled ready", timeout=5)
                create_btn.click_input()
                log("Clicked Create Account fallback button.")
            except Exception:
                log("No Sign in/Create button found (non-fatal).")

        time.sleep(3)
    except Exception as e:
        log(f"Error clicking manage/signin: {e}")
        raise


def handle_browser_login_and_open(desktop: Desktop, username: str, password: str):
    """Find the browser popup and enter username/password, then click Open HP Smart."""
    browser = find_browser_window(desktop)
    if not browser:
        log("Browser popup window not located.")
        return False

    try:
        browser.set_focus()
        log("Browser focused for credential entry.")

        # try to find username field by control type 'Edit' and name/title attributes
        try:
            # prefer a child control named 'username' or with auto_id/title hints
            username_edit = browser.child_window(title_re="username|Email|email|email-address", control_type="Edit")
            username_edit.wait("visible enabled ready", timeout=8)
        except Exception:
            # fallback: choose first Edit control
            edits = browser.descendants(control_type="Edit")
            if not edits:
                raise RuntimeError("No Edit controls found in browser popup.")
            username_edit = edits[0]

        username_edit.set_focus()
        username_edit.type_keys("^a{BACKSPACE}", pause=0.05)  # clear
        username_edit.type_keys(username, with_spaces=True, pause=0.02)
        log("Entered username.")

        # Sometimes there is a 'Use password' button to reveal password field
        try:
            use_pw_btn = browser.child_window(title_re="Use password|Use your password", control_type="Button")
            if use_pw_btn.exists() and use_pw_btn.is_visible():
                use_pw_btn.click_input()
                log("Clicked 'Use password' if present.")
                time.sleep(1)
        except Exception:
            pass

        # Password field
        try:
            password_edit = browser.child_window(title_re="password|Password|passwd", control_type="Edit")
            password_edit.wait("visible enabled ready", timeout=8)
        except Exception:
            edits = browser.descendants(control_type="Edit")
            # choose second Edit if exists
            password_edit = edits[1] if len(edits) > 1 else edits[0]

        password_edit.set_focus()
        password_edit.type_keys("^a{BACKSPACE}", pause=0.05)
        password_edit.type_keys(password, with_spaces=True, pause=0.02)
        log("Entered password.")

        # Click submit
        try:
            submit_btn = browser.child_window(title_re="submit-button|Sign in|Sign In|Submit", control_type="Button")
            submit_btn.wait("visible enabled ready", timeout=8)
            submit_btn.click_input()
            log("Clicked submit on browser popup.")
        except Exception:
            # fallback: press Enter in password field to submit
            password_edit.type_keys("{ENTER}")
            log("Pressed Enter to submit credentials as fallback.")

        # Wait for 'Open HP Smart' button in that browser popup
        time.sleep(3)
        try:
            open_btn = browser.child_window(title_re="Open HP Smart|Open HP Smart App", control_type="Button")
            open_btn.wait("visible enabled ready", timeout=15)
            open_btn.click_input()
            log("Clicked 'Open HP Smart' in browser popup.")
        except Exception:
            # as a reliable fallback, press ENTER a few times to accept any OS-level prompt
            log("'Open HP Smart' button not found — sending Enter key fallback (3 attempts).")
            for _ in range(3):
                keyboard.send_keys("{ENTER}")
                time.sleep(1)

        # allow app to regain focus
        time.sleep(5)
        return True

    except Exception as e:
        log(f"Error during browser login: {e}")
        return False


def open_app_settings_and_verify(main_win):
    """Navigate App Settings -> Privacy Settings and verify Terms of Use link."""
    try:
        # Click App Settings (ListItem)
        app_settings = main_win.child_window(title="App Settings", control_type="ListItem")
        app_settings.wait("visible enabled ready", timeout=10)
        app_settings.click_input()
        log("Clicked 'App Settings'.")
        time.sleep(1.5)

        # Click Privacy Settings (Text control)
        privacy_text = main_win.child_window(title="Privacy Settings", control_type="Text")
        privacy_text.wait("visible enabled ready", timeout=8)
        privacy_text.click_input()
        log("Clicked 'Privacy Settings'.")
        time.sleep(1.5)

        # Verify title text
        privacy_title = main_win.child_window(title="Privacy Settings", control_type="Text")
        privacy_title.wait("visible ready", timeout=6)
        current_title = privacy_title.window_text()
        if current_title.strip() == "Privacy Settings":
            log(f"Privacy Settings title verified: '{current_title}'")
        else:
            log(f"Privacy Settings title mismatch. Got: '{current_title}'")

        # Verify Terms of Use hyperlink
        terms_link = main_win.child_window(title="HP Smart Terms of Use", control_type="Hyperlink")
        if terms_link.exists() and terms_link.is_visible():
            log("HP Smart Terms of Use link is present and visible.")
        else:
            log("HP Smart Terms of Use link is NOT visible.")

        return True

    except Exception as e:
        log(f"Error verifying privacy settings: {e}")
        return False


# -------------------------
# Main flow
# -------------------------
def main():
    log("=== HP Smart automation started ===")
    try:
        # Step 1: Launch app (Start menu)
        press_start_and_open_app()

        # Step 2: Connect to the app
        app = connect_app_with_retry(Config.APP_TITLE_RE, timeout=Config.MAX_RETRIES)
        if not app:
            log("Could not connect to HP Smart app. Exiting.")
            return 1

        # Get the top-level main window
        try:
            main_win = app.window(title_re=Config.APP_TITLE_RE, control_type="Window")
            main_win.wait("exists ready visible enabled", timeout=10)
            main_win.set_focus()
            log(f"Main window detected: '{main_win.window_text()}'")
            main_win.maximize()
        except Exception as e:
            log(f"Failed to prepare main window: {e}")
            return 1

        # Step 3: Click Manage Account and Sign in
        click_manage_and_signin(main_win)

        # Step 4: Find browser popup and login
        desktop = Desktop(backend="uia")
        ok = handle_browser_login_and_open(desktop, Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        if not ok:
            log("Browser login/open step did not complete successfully (continuing to try app actions).")

        # Step 5: After returning to app, open App Settings and verify Privacy Settings
        open_app_settings_and_verify(main_win)

        log("=== HP Smart automation finished ===")
        return 0

    except Exception as ex:
        log(f"Unexpected error in main: {ex}")
        return 2


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
