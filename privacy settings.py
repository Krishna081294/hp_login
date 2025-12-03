from pywinauto import keyboard
from pywinauto import Application,Desktop
import time
import selenium.webdriver as driver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
 
# from rework import log_step
# Launch HP Smart App
keyboard.send_keys("{VK_LWIN}")
keyboard.send_keys("HP Smart")
keyboard.send_keys("{ENTER}")
time.sleep(15)
 
# Connect to HP Smart Main Window
app = Application(backend="uia").connect(title_re="HP Smart")
 
# Get TOP-LEVEL window only
main = app.window(title_re="HP Smart", control_type="Window")
 
main.wait("visible", timeout=40)
main.set_focus()
main.maximize()
 
# Manage HP Account Button
manage_account_btn = main.child_window(
    title="Manage HP Account",
    control_type="Button"
)
manage_account_btn.wait("ready", timeout=30)
manage_account_btn.click_input()
time.sleep(3)  
# Sign Up Button
Sign_in_btn = main.child_window(
    title="Sign in",
    control_type="Button"
 
)
Sign_in_btn.wait("ready", timeout=30)
Sign_in_btn.click_input()
time.sleep(3)  
 
# driver = driver.Chrome()
# driver.switch_to.window(driver.window_handles[-1])
 
 
time.sleep(10)
 
browser_win = Desktop(backend="uia").window(title_re=".*Chrome.*")
browser_win.wait("exists ready", timeout=20)
browser_win.set_focus()
 
 
 
 
username_Text = browser_win.window(
    title="username",  # text shown in your screenshot
    control_type="Edit"
)
 
# Set text
username_Text.wait("visible enabled ready", timeout=30).type_keys("test1202@mailsac.com")
 
# OR: send_keys("testqama24+test2911@gmail.com")
 
print("Username entered successfully!")
time.sleep(2)
use_password_btn = browser_win.window(title="Use password", control_type="Button")
use_password_btn.click_input()
time.sleep(2)
 
 
 
password_Text = browser_win.window(
    title="password",  # text shown in your screenshot  
    control_type="Edit"
)
# Set text
password_Text.wait("visible enabled ready", timeout=30).type_keys("Ascendion@12345")
print("Password entered successfully!")
time.sleep(2)
sign_in_btn = browser_win.window(title="submit-button", control_type="Button")
sign_in_btn.click_input()
time.sleep(15)
 
# Verify Button
verify_btn = browser_win.window(title="Open HP Smart", control_type="Button")
verify_btn.click_input()
time.sleep(20)
 
# ========================================================
# CLICK "App Settings"  (Correct)
# ========================================================
app_settings = main.child_window(
    title="App Settings",
    control_type="ListItem"
)
 
app_settings.wait("ready", timeout=30)
app_settings.click_input()
time.sleep(3)
 
# ========================================================
# CLICK "Privacy Settings"
# (Click the TEXT child)
# ========================================================
privacy_text = main.child_window(
    title="Privacy Settings",
    control_type="Text"
)
 
privacy_text.wait("ready", timeout=30)
privacy_text.click_input()
time.sleep(3)
 
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
else:
    print("Verification failed: Link not visible.")
 
terms_link.click_input()
time.sleep(3)