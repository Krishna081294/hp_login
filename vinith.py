import time
import re
import requests
from pywinauto import Desktop, keyboard

REPORT = []

def log_step(desc, status="PASS"):
    REPORT.append((desc, status))
    print(f"{desc}: {status}")

# ------------------------------------------------------
# PART 1 — Launch HP Smart and navigate to Create Account
# ------------------------------------------------------

def launch_hp_smart_and_navigate():
    try:
        keyboard.send_keys("{VK_LWIN}")
        time.sleep(1)
        keyboard.send_keys("HP Smart")
        time.sleep(1)
        keyboard.send_keys("{ENTER}")
        log_step("Launched HP Smart app.")
        time.sleep(6)

        desktop = Desktop(backend="uia")
        main_win = desktop.window(title_re=".*HP Smart.*")
        main_win.wait('visible enabled ready', timeout=15)
        main_win.set_focus()
        log_step("Focused HP Smart main window.")

        manage_account_btn = main_win.child_window(
            title="Manage HP Account",
            auto_id="HpcSignedOutIcon",
            control_type="Button"
        )
        manage_account_btn.wait('visible enabled ready', timeout=15)
        manage_account_btn.click_input()
        log_step("Clicked Manage HP Account button.")
        time.sleep(3)

        create_account_btn = main_win.child_window(
            auto_id="HpcSignOutFlyout_CreateBtn",
            control_type="Button"
        )
        create_account_btn.wait('visible enabled ready', timeout=15)
        create_account_btn.click_input()
        log_step("Clicked Create Account button.")
        time.sleep(8)

        return desktop

    except Exception as e:
        log_step(f"Error launching or navigating HP Smart: {e}", "FAIL")
        return None


# ------------------------------------------------------
# PART 2 — Fill HP Account form
# ------------------------------------------------------

def fill_account_form_and_create(desktop, email_id):
    try:
        browser = desktop.window(title_re=".*HP account.*")
        browser.wait("ready", timeout=30)
 
        # browser.child_window(title="Create account", control_type="Button").click_input()
 
        browser.child_window(auto_id="firstName", control_type="Edit").type_keys("Test")
        browser.child_window(auto_id="lastName", control_type="Edit").type_keys("User")
        browser.child_window(auto_id="email", control_type="Edit").type_keys("test241120@mailsac.com")
        browser.child_window(auto_id="password", control_type="Edit").type_keys("Ascendion@12345")
 
        browser.child_window(auto_id="sign-up-submit", control_type="Button").click_input()
 
        log_step(f"Account Created: {email_id}")
 
    except Exception as e:
        log_step(f"Failed to fill HP account form: {e}", "FAIL")
 
 
# ---------------------------------------------------------
# FETCH MAILSAC MAIL
# ---------------------------------------------------------
def get_mailsac_email(mailbox):
    try:
        url = f"https://mailsac.com/api/addresses/{mailbox}/messages"
        headers = {"Mailsac-Key": "YOUR_MAILSAC_API_KEY"}
 
        r = requests.get(url, headers=headers)
 
        if r.status_code != 200:
            log_step("Failed to retrieve Mailsac inbox", "FAIL")
            return None
 
        messages = r.json()
        if not messages:
            log_step("No emails found yet.", "FAIL")
            return None
 
        msg_id = messages[0]["_id"]
 
        full_mail = requests.get(f"https://mailsac.com/api/text/{msg_id}", headers=headers)
        return full_mail.text
 
    except Exception as e:
        log_step(f"Error fetching Mailsac email: {e}", "FAIL")
        return None
 
 
# ---------------------------------------------------------
# EXTRACT OTP & VERIFICATION LINK
# ---------------------------------------------------------
def extract_otp_and_link(email_body):
    try:
        otp_search = re.search(r"\b(\d{6})\b", email_body)
        link_search = re.search(r"(https://[^\s]+)", email_body)
 
        otp = otp_search.group(1) if otp_search else None
        link = link_search.group(1) if link_search else None
 
        return otp, link
 
    except Exception:
        return None, None
 
 
# ---------------------------------------------------------
# OPEN LINK
# ---------------------------------------------------------
def open_verification_link(link):
    try:
        keyboard.send_keys("{VK_LWIN}+r")
        time.sleep(1)
        keyboard.send_keys(f'"{link}"{{ENTER}}')
        time.sleep(6)
        log_step("Opened verification link")
    except Exception as e:
        log_step(f"Link open failed: {e}", "FAIL")
 
 
# ---------------------------------------------------------
# ENTER OTP
# ---------------------------------------------------------
def handle_popups_and_verify(desktop, otp):
    try:
        browser = desktop.window(title_re=".*HP.*")
        browser.wait('visible enabled ready', timeout=20)
        browser.set_focus()
 
        otp_box = browser.child_window(auto_id="verificationCode", control_type="Edit")
        otp_box.set_edit_text(otp)
 
        verify_btn = browser.child_window(auto_id="buttonVerify", control_type="Button")
        verify_btn.click_input()
 
        log_step("OTP Submitted")
 
        time.sleep(5)
 
    except Exception as e:
        log_step(f"OTP verification failed: {e}", "FAIL")
 
 
# ---------------------------------------------------------
# HTML REPORT
# ---------------------------------------------------------
def generate_html_report():
    html = """
    <html><body>
    <h2>HP Account Creation Report</h2>
    <table border='1' cellpadding='4' cellspacing='0'>
    <tr><th>Step</th><th>Status</th></tr>
    """
 
    for step, status in REPORT:
        color = "green" if status == "PASS" else "red"
        html += f"<tr><td>{step}</td><td style='color:{color}'>{status}</td></tr>"
 
    html += "</table></body></html>"
 
    with open("HP_Account_Creation_Report.html", "w") as f:
        f.write(html)
 
    log_step("HTML report generated")
 
 
# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    mailbox = "testcc"
    email_id = f"{mailbox}@mailsac.com"
 
    desktop = launch_hp_smart_and_navigate()
    if not desktop:
        return
 
    fill_account_form_and_create(desktop, email_id)
 
    log_step("Waiting for email...")
    time.sleep(10)
 
    mail_body = get_mailsac_email(mailbox)
    if not mail_body:
        generate_html_report()
        return
 
    otp, link = extract_otp_and_link(mail_body)
 
    if link:
        open_verification_link(link)
    if otp:
        handle_popups_and_verify(desktop, otp)
 
    generate_html_report()
 
 
if __name__ == "__main__":
    main()
 