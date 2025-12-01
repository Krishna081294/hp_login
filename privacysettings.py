from pywinauto import Desktop, keyboard, timings
import time

def launch_hp_smart_app():
    keyboard.send_keys("{VK_LWIN}HP Smart{ENTER}")
    print("Launched HP Smart app.")
    desktop = Desktop(backend="uia")
    main_win = desktop.window(title_re=".*HP Smart.*")
    print("Waiting for HP Smart main window to be fully ready...")
    main_win.wait("exists visible enabled ready", timeout=60)
    time.sleep(10)  # Extra wait for UI stabilization
    print("HP Smart main window ready.")
    return main_win

def wait_for_view_change_settings_button(main_win, timeout=60, retry_interval=2):
    elapsed = 0
    while elapsed < timeout:
        try:
            settings_btn = main_win.child_window(title_re="View and change app settings.", control_type="Button")
            settings_btn.wait("exists enabled visible ready", timeout=retry_interval)
            return settings_btn
        except timings.TimeoutError:
            print(f"'View and change app settings.' button not ready yet, retrying... {elapsed + retry_interval}/{timeout} sec elapsed")
            elapsed += retry_interval
            time.sleep(retry_interval)
    raise RuntimeError("Timeout waiting for 'View and change app settings.' button.")

def click_back_button(main_win):
    back_btn = main_win.child_window(title="Back", control_type="Button")
    back_btn.wait("exists enabled visible ready", timeout=20)
    back_btn.click_input()
    print("Clicked Back button.")
    time.sleep(3)

def click_item(main_win, title, control_type="ListItem", class_name=None, double_click=False):
    kwargs = {"title": title, "control_type": control_type}
    if class_name:
        kwargs["class_name"] = class_name

    ctrl = main_win.child_window(**kwargs)
    ctrl.wait("exists enabled visible ready", timeout=20)
    if double_click:
        ctrl.double_click_input()
        print(f"Double clicked '{title}'.")
    else:
        ctrl.click_input()
        print(f"Clicked '{title}'.")
    time.sleep(3)

def main():
    main_win = launch_hp_smart_app()

    # Step 3: click on "View and change app settings" button
    settings_btn = wait_for_view_change_settings_button(main_win)
    settings_btn.click_input()
    print("Clicked 'View and change app settings.' button.")
    time.sleep(3)

    # Step 4: Add Back button click after App Settings screen shows
    click_back_button(main_win)

    # Step 5-10: Click items sequentially under App Settings screen
    items_to_click = [
        ("App Settings", "ListItem", "ListViewItem", True),  # double click App Settings
        ("Personalize Tiles", "Button", None, False),
        ("Pin HP Smart to Start", "Button", None, False),
        ("Send Feedback", "Button", None, False),
        ("Privacy Settings", "Button", None, False),
        ("About", "Button", None, False)
    ]

    for title, control_type, class_name, dbl_click in items_to_click:
        try:
            click_item(main_win, title, control_type, class_name, dbl_click)
            # After each button except Privacy Settings, click Back to return
            if title != "Privacy Settings":
                click_back_button(main_win)
        except Exception as e:
            print(f"Failed to click {title}: {e}")

    # Continue with remaining steps per your earlier described flows...
    # For example: click_privacy_settings(), show_privacy_description(), show_terms_and_agreements(), click_terms_links(), etc.

if __name__ == "__main__":
    main()
