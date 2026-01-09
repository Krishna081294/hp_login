from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
import allure
import pytest
from allure_commons.types import AttachmentType
from selenium.common.exceptions import NoSuchElementException

@pytest.fixture(scope="session")
def driver():
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
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def attach_screenshot(driver, name):
    try:
        screenshot = driver.get_screenshot_as_png()
        allure.attach(screenshot, name, AttachmentType.PNG)
    except:
        pass

@allure.feature("Inshorts App Navigation")
@allure.story("Complete App Flow Testing")
@allure.title("Inshorts App End-to-End Flow")
def test_inshorts_flow(driver):
    try:
        with allure.step("Launch app and click Predicted app: inshorts"):
            attach_screenshot(driver, "predicted_app_screen")
            predicted_app_element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Predicted app: inshorts")
            predicted_app_element.click()
            time.sleep(3)
            attach_screenshot(driver, "after_predicted_app_click")
        
        with allure.step("Verify home page loaded"):
            home_root = driver.find_element(AppiumBy.ID, "com.nis.app:id/action_bar_root")
            assert home_root.is_displayed()
            allure.attach(f"Home page loaded. Root element visible: {home_root.is_displayed()}", "home_verification", AttachmentType.TEXT)
        
        with allure.step("Verify news content and click news title"):
            news_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_title")
            news_text = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_text")
            allure.attach(f"News Title: {news_title.text}", "news_title", AttachmentType.TEXT)
            allure.attach(f"News Text: {news_text.text}", "news_text", AttachmentType.TEXT)
            news_title.click()
            time.sleep(2)
            attach_screenshot(driver, "after_news_click")
        
        with allure.step("Verify story number or handle absence"):
            try:
                story_number = driver.find_element(AppiumBy.ID, "story_number_1")
                allure.attach(f"Story number: {story_number.text}", "story_number", AttachmentType.TEXT)
            except NoSuchElementException:
                allure.attach("story_number_1 not visible", "story_number_missing", AttachmentType.TEXT)
        
        with allure.step("Navigate back from story view"):
            try:
                toolbar_back = driver.find_element(AppiumBy.ID, "com.nis.app:id/toolbar_back")
                toolbar_back.click()
                time.sleep(2)
                allure.attach("Clicked toolbar back successfully", "back_navigation", AttachmentType.TEXT)
            except NoSuchElementException:
                allure.attach("Toolbar back not found, continuing...", "back_skip", AttachmentType.TEXT)
        
        with allure.step("Test all bottom navigation tabs"):
            tabs = ["Finance", "Timelines", "Videos", "Insights", "Good News"]
            for tab_text in tabs:
                safe_click_tab_with_allure(driver, tab_text)
                if safe_click_tab_with_allure(driver, tab_text):
                    attach_screenshot(driver, f"{tab_text}_tab")
        
        with allure.step("Test search functionality"):
            search_icon = driver.find_elements(AppiumBy.ID, "com.nis.app:id/navigation_bar_item_icon_view")[0]
            search_icon.click()
            time.sleep(2)
            search_suggestion = driver.find_element(AppiumBy.ID, "com.nis.app:id/txt_search_suggestion")
            assert search_suggestion.text == "Search for news"
            allure.attach("Search suggestion verified: Search for news", "search_verification", AttachmentType.TEXT)
        
        with allure.step("Test Notifications section"):
            notif_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_title")
            view_all_notifications = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_view_all")
            allure.attach(f"Notif Title: {notif_title.text}", "notifications_title", AttachmentType.TEXT)
            allure.attach(f"View All: {view_all_notifications.text}", "view_all_notifications", AttachmentType.TEXT)
            view_all_notifications.click()
            click_back_button_with_allure(driver)
        
        with allure.step("Test Insights section"):
            insights_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_title")
            view_all_insights = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_view_all")
            allure.attach(f"Insights Title: {insights_title.text}", "insights_title", AttachmentType.TEXT)
            allure.attach(f"View All Insights: {view_all_insights.text}", "view_all_insights", AttachmentType.TEXT)
            view_all_insights.click()
            click_back_button_with_allure(driver)
        
        with allure.step("Perform long press gesture test"):
            long_press_at_coordinates_with_allure(driver, x=100, y=100, duration_ms=1000)
            attach_screenshot(driver, "after_long_press")
            
    except AssertionError as ae:
        attach_screenshot(driver, "test_failure")
        raise
    except Exception as e:
        attach_screenshot(driver, "test_exception")
        raise

def safe_click_tab_with_allure(driver, tab_text):
    try:
        tab = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{tab_text}")')
        tab.click()
        time.sleep(1)
        return True
    except:
        allure.attach(f"{tab_text} tab not found", f"{tab_text}_tab_error", AttachmentType.TEXT)
        return False

def click_back_button_with_allure(driver):
    try:
        back_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Back")
        back_button.click()
        time.sleep(2)
    except:
        pass

def long_press_at_coordinates_with_allure(driver, x=100, y=100, duration_ms=1000):
    try:
        driver.execute_script("mobile: longClickGesture", {"x": x, "y": y, "duration": duration_ms})
    except:
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--alluredir=allure-results", "--clean-alluredir"])
