from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
import pytest
import allure
from allure_commons.types import AttachmentType
import os

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

def long_press_at_coordinates(driver, x=100, y=100, duration_ms=1000):
    driver.execute_script("mobile: longClickGesture", {"x": x, "y": y, "duration": duration_ms})

def click_back_button(driver):
    try:
        back_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Back")
        back_button.click()
        time.sleep(2)
        allure.attach("Clicked back button", name="Back Button Action", attachment_type=AttachmentType.TEXT)
        return True
    except Exception as e:
        allure.attach(f"Back button not found: {str(e)}", name="Back Button Error", attachment_type=AttachmentType.TEXT)
        return False

def safe_click_tab(driver, tab_text):
    try:
        tab = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{tab_text}")')
        tab.click()
        time.sleep(1)
        allure.attach(f"Clicked {tab_text} tab", name=f"{tab_text} Tab Clicked", attachment_type=AttachmentType.TEXT)
        return True
    except Exception as e:
        allure.attach(f"{tab_text} tab not found: {str(e)}", name=f"{tab_text} Tab Error", attachment_type=AttachmentType.TEXT)
        return False

@allure.feature("Inshorts App Automation")
@allure.story("Complete App Flow Testing")
def test_inshorts_flow(driver):
    allure.attach("Test started", name="Test Start", attachment_type=AttachmentType.TEXT)
    
    predicted_app = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Predicted app: inshorts")
    predicted_app.click()
    allure.attach("Clicked Predicted app: inshorts", name="Predicted App Click", attachment_type=AttachmentType.TEXT)
    time.sleep(3)
    
    home_root = driver.find_element(AppiumBy.ID, "com.nis.app:id/action_bar_root")
    allure.attach("Home page loaded successfully", name="Home Page Verification", attachment_type=AttachmentType.TEXT)
    
    news_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_title")
    news_text = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_text")
    
    title_text = news_title.text
    text_content = news_text.text
    allure.attach(f"Title: {title_text}\nText: {text_content}", name="News Content", attachment_type=AttachmentType.TEXT)
    
    news_title.click()
    allure.attach("Clicked news title", name="News Title Click", attachment_type=AttachmentType.TEXT)
    time.sleep(2)
    
    try:
        story_number = driver.find_element(AppiumBy.ID, "story_number_1")
        story_text = story_number.text
        allure.attach(f"Story number: {story_text}", name="Story Number", attachment_type=AttachmentType.TEXT)
    except Exception as e:
        allure.attach("story_number_1 not visible", name="Story Number Missing", attachment_type=AttachmentType.TEXT)
    
    try:
        toolbar_back = driver.find_element(AppiumBy.ID, "com.nis.app:id/toolbar_back")
        toolbar_back.click()
        allure.attach("Clicked toolbar back", name="Toolbar Back Click", attachment_type=AttachmentType.TEXT)
        time.sleep(2)
    except Exception as e:
        allure.attach(f"Toolbar back not found: {str(e)}", name="Toolbar Back Missing", attachment_type=AttachmentType.TEXT)
    
    tabs = ["Finance", "Timelines", "Videos", "Insights", "Good News"]
    for tab in tabs:
        success = safe_click_tab(driver, tab)
        assert success, f"Failed to click {tab} tab"
    
    search_icon = driver.find_elements(AppiumBy.ID, "com.nis.app:id/navigation_bar_item_icon_view")[0]
    search_icon.click()
    allure.attach("Clicked search icon", name="Search Icon Click", attachment_type=AttachmentType.TEXT)
    time.sleep(2)
    
    search_suggestion = driver.find_element(AppiumBy.ID, "com.nis.app:id/txt_search_suggestion")
    assert search_suggestion.text == "Search for news"
    allure.attach("Search suggestion verified: Search for news", name="Search Verification", attachment_type=AttachmentType.TEXT)
    
    notif_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_title")
    allure.attach(f"Notifications: {notif_title.text}", name="Notifications Title", attachment_type=AttachmentType.TEXT)
    
    view_all_notifications = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_view_all")
    allure.attach(f"View All: {view_all_notifications.text}", name="View All Notifications", attachment_type=AttachmentType.TEXT)
    view_all_notifications.click()
    click_back_button(driver)
    
    insights_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_title")
    allure.attach(f"Insights: {insights_title.text}", name="Insights Title", attachment_type=AttachmentType.TEXT)
    
    view_all_insights = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_view_all")
    allure.attach(f"View All Insights: {view_all_insights.text}", name="View All Insights", attachment_type=AttachmentType.TEXT)
    view_all_insights.click()
    click_back_button(driver)
    
    long_press_at_coordinates(driver, x=100, y=100, duration_ms=1000)
    allure.attach("Long press gesture performed at (100,100)", name="Long Press Gesture", attachment_type=AttachmentType.TEXT)
    
    allure.attach("Test completed successfully", name="Test Completion", attachment_type=AttachmentType.TEXT)

if __name__ == "__main__":
    os.makedirs("allure-results", exist_ok=True)
    pytest.main(["-v", "--alluredir=allure-results", "-s", __file__])
    print("Allure results generated in 'allure-results' folder.")
    print("Run: allure generate allure-results -o allure-report --clean")
    print("Then: allure open allure-report")
