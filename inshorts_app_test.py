from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_inshorts_complete_flow():
    caps = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": "Android Emulator",
        "appium:platformVersion": "16",
        "appium:udid": "emulator-5554",
        "appium:appPackage": "com.nis.app",
        "appium:appActivity": "com.nis.app.ui.activities.HomeActivity",
        "appium:noReset": True,
        "appium:newCommandTimeout": 300
    }
    
    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Waiting for action bar root")
        action_bar = wait.until(EC.presence_of_element_located(
            (AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.nis.app:id/action_bar_root']")
        ))
        print("Action bar root found")
        
        print("Clicking My Feed tab")
        my_feed = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, "My Feed tab")
        ))
        my_feed.click()
        print("My Feed tab clicked")
        time.sleep(3)
        
        print("Waiting for first news title")
        news_titles = driver.find_elements(AppiumBy.ID, "com.nis.app:id/news_title")
        if news_titles:
            news_title = news_titles[0]
            news_title.click()
            print("First news title clicked")
        else:
            print("No news titles found, trying news image")
            news_image = wait.until(EC.element_to_be_clickable(
                (AppiumBy.ID, "com.nis.app:id/news_image")
            ))
            news_image.click()
            print("News image clicked")
        
        time.sleep(2)
        
        print("Clicking toolbar back immediately")
        toolbar_back = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ID, "com.nis.app:id/toolbar_back")
        ))
        toolbar_back.click()
        print("Toolbar back clicked")
        time.sleep(3)
        
        print("Clicking Profile")
        profile_btn = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, "Profile")
        ))
        profile_btn.click()
        print("Profile opened")
        
    except Exception as e:
        print("Test failed:", str(e))
        print("Current page source length:", len(driver.page_source))
    
    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    test_inshorts_complete_flow()
