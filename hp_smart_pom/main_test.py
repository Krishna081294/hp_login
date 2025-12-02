from page_objects.hp_smart_app import HpSmartApp
from page_objects.hp_account_page import HpAccountPage
from page_objects.mailsac_page import MailsacPage
from utils.helpers import generate_random_mailbox, generate_random_name
from utils.logger import log_step, generate_report, REPORT
from utils import click_open_hp_smart

def main():
    REPORT.clear()

    mailbox_full = generate_random_mailbox()
    mailbox_local_part = mailbox_full.split("@")[0]
    log_step(f"Generated mailbox: {mailbox_full}")

    first_name, last_name = generate_random_name()
    log_step(f"Generated name: {first_name} {last_name}")

    hp_app = HpSmartApp()
    hp_account = HpAccountPage()
    mailsac = MailsacPage()

    try:
        hp_app.launch()
        hp_app.open_create_account()
        hp_account.fill_form(first_name, last_name, mailbox_full, "SecurePassword123")
        mailsac.open_mailsac()
        otp = mailsac.fetch_otp(mailbox_local_part)

        if otp:
            log_step(f"OTP received: {otp}")
            hp_account.enter_otp_and_submit(otp)

            # Use fallback after OTP submission, in case popup appears
            try:
                click_open_hp_smart()
            except:
                log_step("Fallback popup handling failed", "FAIL")
        else:
            log_step("Failed to receive OTP", "FAIL")
    finally:
        mailsac.quit()
        generate_report()

if __name__ == "__main__":
    main()