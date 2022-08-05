from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
import base64
from tnpb.ocr import get_verify_code
from tnpb.logger import error_logger, logger
import tnpb
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TNPv2Bot:
    def __init__(self):
        self._url = "https://npm.cpami.gov.tw"
        
        self._chrome = webdriver.Remote(
            os.getenv("CHROME_REMOTE_URL"),
            desired_capabilities=DesiredCapabilities.CHROME)

        # ## for screen display
        # _chrome_opt = Options()
        # _chrome_opt.add_argument("--disable-notifications")
        # # _chrome_opt.add_argument('--headless')  # enable headless mode
        # _chrome_opt.add_argument('--disable-gpu') # disable GPU, avoid system error or web error
        # self._chrome = webdriver.Chrome(
        #     './chromedriver', chrome_options=_chrome_opt)

    def wait_loading(self, wait_sec: float = 2.0):
        # Wait for the page to load
        time.sleep(wait_sec)
    
    def capture_screen(self, screen_path):
        if screen_path is not None:
            from pathlib import Path
            screen_path = Path(screen_path)

            if screen_path.is_dir():
                screen_path = screen_path / 'screen.png'
            
            screen_path = screen_path.with_suffix('.png')
            
            self._chrome.save_screenshot(f'{screen_path}')

    def get_verify_image(self, xpath="//*[@id='ContentPlaceHolder1_imgcode']"):
        return self._chrome.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = ele.width; cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, self._chrome.find_element_by_xpath(xpath))

    def renew_verify_image(self, xpath="//*[@id='ContentPlaceHolder1_imgcode']"):
        self._chrome.find_element_by_xpath(xpath).click()

    def search_draft(self, sid: str = "", email: str = "", retry_limit: int = 10):
        # only support ROC

        self._chrome.get(f"{self._url}/apply_2_1.aspx")
        self.wait_loading()

        _nation = Select(self._chrome.find_element_by_id(
            "ContentPlaceHolder1_apply_nation"))
        _nation.select_by_visible_text(u"中華民國")
        # select nation action will change sid and email DOM, so wait for loading DOM
        self.wait_loading(0.5)

        _sid = self._chrome.find_element_by_id("ContentPlaceHolder1_apply_sid")
        _email = self._chrome.find_element_by_id(
            "ContentPlaceHolder1_apply_email")
        _sid.send_keys(sid)
        _email.send_keys(email)

        for i in range(retry_limit):
            logger.info(f'Try {i+1} times')

            self.wait_loading()
            _vcode = self._chrome.find_element_by_id(
                "ContentPlaceHolder1_vcode")
            _enter = self._chrome.find_element_by_id(
                "ContentPlaceHolder1_btnappok")

            _vcode.clear()
            img_base64 = self.get_verify_image()
            verify_code = get_verify_code(base64.b64decode(img_base64))
            _vcode.send_keys(verify_code)
            _enter.click()

            if self.handle_alert():
                break

            self.renew_verify_image(
                xpath="//*[@id='ContentPlaceHolder1_imgcode']")

    def handle_alert(self) -> bool:
        ret = True
        self.wait_loading(0.5)
        # offine_msg = "系統開放申請時間為07:00-23:00，請您於07:00手動重新整理頁面，輸入驗證碼後執行”確認送出”鈕即可將申請案送出。草稿資訊僅保留30日，30日內未異動資料或送出申請，草稿將被移除。"
        # duplicate_msg = "重覆申請，無法申請入園"
        error_verify_code_msg = "驗證碼錯誤"
        try:
            alert_text = self._chrome.switch_to.alert.text

            if len(alert_text):
                logger.info(alert_text)
                self._chrome.switch_to.alert.accept()
                if alert_text.startswith(error_verify_code_msg):
                    ret = False
        except Exception as e:
            pass

        self.wait_loading()

        # if has //*[@id="form1"]/div[4]/div[3]/div[2]/div[2]/ul/li[1]/font
        return ret

    def send_draft(self, retry_limit: int = 100):
        self._chrome.get("https://npm.cpami.gov.tw/apply_2_3.aspx")
        self.handle_alert()

        self._chrome.find_element_by_id(
            "ContentPlaceHolder1_New_List_btnupd_0").click()
        self.handle_alert()
        
        utc_now = datetime.utcnow()
        logger.info(f"1 utc_now: {utc_now}")
        utc_now += relativedelta(months=2, hours=8)
        logger.info(f"2 utc_now: {utc_now}")
        date_time = utc_now.strftime("%Y-%m-%d")
        logger.info(f"3 date_time: {date_time}")
        Select(self._chrome.find_element_by_id("ContentPlaceHolder1_applystart")).select_by_visible_text(date_time)

        self._chrome.find_element_by_id(
            "ContentPlaceHolder1_btnsetpup").click()
        
        #TODO if member > 1 
        try:
            self._chrome.find_element_by_id("lineonechk").click()
        except Exception as e:
            logger.info("member > 1")
            pass
        self._chrome.find_element_by_id(
            "ContentPlaceHolder1_btnsetp2upnext").click()

        for i in range(retry_limit):
            if not (7 <= (datetime.utcnow() + relativedelta(hours=8)).hour < 23):
                logger.info("can not send resquest time")
                return

            logger.info(f'Try {i+1} times')
            self.wait_loading()
            vcode = self._chrome.find_element_by_id(
                "ContentPlaceHolder1_vcode")
            
            try:
                save = self._chrome.find_element_by_id(
                    "ContentPlaceHolder1_btnsave")
            except Exception as e:
                self._chrome.refresh()
                logger.info(f'Try {i+1} times: {e}')
                self.wait_loading()
                continue         

            vcode.clear()
            img_base64 = self.get_verify_image(
                xpath='//*[@id="ContentPlaceHolder1_imgcode"]')
            verify_code = get_verify_code(base64.b64decode(img_base64))
            vcode.send_keys(verify_code)

            save.click()
            if self.handle_alert():
                break

            self.renew_verify_image(
                xpath="//*[@id='ContentPlaceHolder1_imgcode']")

    def run(self, sid: str, email: str, final_screen_path: str):
        logger.info("1. search draft")
        self.search_draft(sid=sid, email=email)
        logger.info("2. send draft")
        self.send_draft()
        self.capture_screen(final_screen_path)
        logger.info("Done !!")

    def teardown(self):
        if self._chrome is not None:
            self._chrome.quit()


def main():
    sid = os.getenv("ID")
    email = os.getenv("EMAIL")
    final_screen_path = os.getenv("FINAL_SCREEN_PATH")

    logger.info(f'sid:   {sid}')
    logger.info(f'email: {email}')
    logger.info(f'commit hash: {tnpb.__commit_hash__}')

    bot = TNPv2Bot()
    try:
        bot.run(sid, email, final_screen_path)
    except Exception as e:
        error_logger.error(f"Failed to run bot: {e}")
        raise e
    finally:
        bot.teardown()
    
if __name__ == "__main__":    
    main()
