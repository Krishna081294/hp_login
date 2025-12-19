# updated_privacy_settings_script.py

from pywinauto import keyboard
from pywinauto import Application, Desktop
from pywinauto.findwindows import find_elements, ElementAmbiguousError
from pywinauto.timings import wait_until_passes
import time

# Launch HP Smart App
keyboard.send_keys("{VK_LWIN}")
keyboard.send_keys("HP Smart")
keyboard.send_keys("{ENTER}")
time.sleep(15)

# Connect to HP Smart Main Window
app = Application(backend="uia").connect(title_re="HP Smart")
main = app.window(title_re="HP Smart", control_type="Window")

main.wait("visible", timeout=40)
main.set_focus()
main.maximize()
print("HP Smart main window ready")

# Manage HP Account Button
manage_account_btn = main.child_window(
    title="Manage HP Account",
    control_type="Button"
)
manage_account_btn.wait("ready", timeout=30)
manage_account_btn.click_input()
time.sleep(3)  
print("Manage HP Account clicked")

# Sign Up Button
Sign_in_btn = main.child_window(
    title="Sign in",
    control_type="Button"
)
Sign_in_btn.wait("ready", timeout=30)
Sign_in_btn.click_input()
time.sleep(3)  
print("Sign in button clicked")

time.sleep(10)

# --- FIX: Robust Chrome window selection to avoid ElementAmbiguousError ---
# The previous code used Application.connect(title_re=".*Chrome.*"), which fails if multiple Chrome windows are open.
# Now, we enumerate all Chrome windows and select the most recent one.

def get_latest_chrome_window():
    # Find all Chrome windows matching the regex
    chrome_windows = find_elements(title_re=".*Chrome.*", backend="uia", visible_only=False)
    if not chrome_windows:
        raise RuntimeError("No Chrome windows found.")
    # Select the last (most recent) window
    return chrome_windows[-1]

try:
    # Retry mechanism to handle dynamic loading times and ambiguous element errors
    def connect_chrome():
        chrome_elem = get_latest_chrome_window()
        chrome_app = Application(backend="uia").connect(process=chrome_elem.process_id)
        browser_win = chrome_app.window(handle=chrome_elem.handle)
        browser_win.wait("exists ready", timeout=20)
        browser_win.set_focus()
        print("Chrome window focused successfully!")
        print(f"Chrome window title: {browser_win.window_text()}")
        return browser_win

    browser_win = wait_until_passes(10, 1, connect_chrome)
except ElementAmbiguousError as e:
    print("Ambiguous Chrome window selection. Please close unused Chrome windows and retry.")
    raise
except Exception as e:
    print(f"Failed to connect to Chrome window: {e}")
    raise

# Username field
username_Text = browser_win.window(
    title="username",  
    control_type="Edit"
)
username_Text.wait("visible enabled ready", timeout=30).type_keys("test1202@mailsac.com")
print("Username entered successfully!")
time.sleep(2)

# Use password button
use_password_btn = browser_win.window(title="Use password", control_type="Button")
use_password_btn.wait("visible enabled ready", timeout=10)
use_password_btn.click_input()
time.sleep(2)
print("Use password button clicked")

# Password field
password_Text = browser_win.window(
    title="password",  
    control_type="Edit"
)
password_Text.wait("visible enabled ready", timeout=30).type_keys("Ascendion@12345")
print("Password entered successfully!")
time.sleep(2)

# Sign in button
sign_in_btn = browser_win.window(title="submit-button", control_type="Button")
sign_in_btn.wait("visible enabled ready", timeout=10)
sign_in_btn.click_input()
print("Sign in button clicked")
time.sleep(15)

# Verify Button (Open HP Smart)
verify_btn = browser_win.window(title="Open HP Smart", control_type="Button")
verify_btn.wait("visible enabled ready", timeout=10)
verify_btn.click_input()
print("Open HP Smart button clicked")
time.sleep(20)

# ========================================================
# CLICK "App Settings"  
# ========================================================
app_settings = main.child_window(
    title="App Settings",
    control_type="ListItem")
app_settings.wait("ready", timeout=30)
app_settings.click_input()
print("App Settings clicked")
time.sleep(3)

# ========================================================
# CLICK "Privacy Settings" 
# ========================================================
privacy_text = main.child_window(
    title="Privacy Settings",
    control_type="Text"
)
privacy_text.wait("ready", timeout=30)
privacy_text.click_input()
print("Privacy Settings clicked")
time.sleep(3)

# Verify Privacy Settings title
privacy_title = main.child_window(
    title="Privacy Settings",
    control_type="Text"
)
privacy_title.wait("ready", timeout=30)
current_title = privacy_title.window_text()
expected_title = "Privacy Settings"
if current_title == expected_title:
    print("Privacy Settings title verified:", current_title)
else:
    print("Title verification failed. Expected:", expected_title, "Got:", current_title)

# ========================================================
# HP Smart terms of use link verification
# ========================================================  
terms_link = main.child_window(
    title="HP Smart Terms of Use",
    control_type="Hyperlink",
    class_name="Hyperlink"
)

terms_link.wait("visible", timeout=30)

if terms_link.exists() and terms_link.is_visible():
    print("HP Smart Terms of Use link is present and visible.")
    terms_link.click_input()
    print("HP Smart Terms of Use link clicked successfully!")
    time.sleep(3)
else:
    print("Verification failed: Link not visible.")

print("Script completed successfully!")

# ----------------------------------------------------------------------
# CHANGES MADE:
# - Added robust Chrome window selection using find_elements and process_id to avoid ElementAmbiguousError.
# - Implemented a retry mechanism (wait_until_passes) for dynamic loading and ambiguous element errors.
# - Ensured Pywinauto Application.connect() uses process_id for precise window targeting.
# - Added inline comments explaining the changes and their purpose.
# ----------------------------------------------------------------------