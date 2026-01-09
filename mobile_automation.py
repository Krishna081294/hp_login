from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time


def create_driver():
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
    return driver


def long_press_at_coordinates(driver, x=100, y=100, duration_ms=1000):
    driver.execute_script(
        "mobile: longClickGesture",
        {"x": x, "y": y, "duration": duration_ms}
    )


def click_back_button(driver):
    try:
        back_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Back")
        back_button.click()
        time.sleep(2)
        print("Clicked back button")
    except Exception:
        print("Back button not found")


def safe_click_tab(driver, tab_text):
    try:
        tab = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{tab_text}")')
        tab.click()
        time.sleep(1)
        print(f"Clicked {tab_text} tab")
        return True
    except Exception:
        print(f"{tab_text} tab not found")
        return False


def test_inshorts_flow():
    driver = create_driver()
    try:
        print("Starting Inshorts automation...")
        
        predicted_app = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Predicted app: inshorts")
        predicted_app.click()
        print("Clicked Predicted app: inshorts")
        time.sleep(3)

        home_root = driver.find_element(AppiumBy.ID, "com.nis.app:id/action_bar_root")
        print("Home page loaded")

        news_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_title")
        news_text = driver.find_element(AppiumBy.ID, "com.nis.app:id/news_text")

        print("News title:", news_title.text)
        print("News text:", news_text.text)

        news_title.click()
        print("Clicked news title")
        time.sleep(2)

        try:
            story_number = driver.find_element(AppiumBy.ID, "story_number_1")
            print("Story number text:", story_number.text)
        except Exception:
            print("story_number_1 not visible on this screen")

        try:
            toolbar_back = driver.find_element(AppiumBy.ID, "com.nis.app:id/toolbar_back")
            toolbar_back.click()
            print("Clicked toolbar back")
            time.sleep(2)
        except Exception:
            print("Toolbar back not found, continuing...")

        print("Testing tabs:")
        safe_click_tab(driver, "Finance")
        safe_click_tab(driver, "Timelines")
        safe_click_tab(driver, "Videos")
        safe_click_tab(driver, "Insights")
        safe_click_tab(driver, "Good News")

        search_icon = driver.find_elements(AppiumBy.ID, "com.nis.app:id/navigation_bar_item_icon_view")[0]
        search_icon.click()
        print("Clicked search icon")
        time.sleep(2)

        search_suggestion = driver.find_element(AppiumBy.ID, "com.nis.app:id/txt_search_suggestion")
        assert search_suggestion.text == "Search for news"
        print("Verified search suggestion text")

        notif_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_title")
        print("Notifications label:", notif_title.text)

        view_all_notifications = driver.find_element(AppiumBy.ID, "com.nis.app:id/notif_view_all")
        print("View All Notifications label:", view_all_notifications.text)
        view_all_notifications.click()
        print("Clicked View All Notifications")
        click_back_button(driver)

        insights_title = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_title")
        print("Insights label:", insights_title.text)

        view_all_insights = driver.find_element(AppiumBy.ID, "com.nis.app:id/insights_view_all")
        print("View All Insights label:", view_all_insights.text)
        view_all_insights.click()
        print("Clicked View All Insights")
        click_back_button(driver)

        print("Performing long press gesture...")
        long_press_at_coordinates(driver, x=100, y=100, duration_ms=1000)
        print("Long press gesture completed")

        print("Test completed successfully!")
        time.sleep(3)

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
    finally:
        print("Closing driver...")
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    test_inshorts_flow()
