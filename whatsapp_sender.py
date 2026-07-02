import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WhatsAppSender:
    def __init__(self, profile_dir="chrome_profile"):
        self.profile_dir = os.path.abspath(profile_dir)
        os.makedirs(self.profile_dir, exist_ok=True)
        self.driver = None
        self.wait = None

    def start(self):
        print("🚀 Launching Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 180)

        print("🌐 Opening WhatsApp Web (scan QR if first time)...")
        self.driver.get("https://web.whatsapp.com/")
        self.wait.until(EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']")),
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chat list']")),
        ))
        print("✅ WhatsApp loaded")
        time.sleep(3)

    # ===== NEW METHOD: SEND TEXT FIRST =====
    def send_text(self, phone, message):
        if self.driver is None:
            self.start()

        driver, wait = self.driver, self.wait

        print(f"💬 Opening chat for text {phone}...")
        driver.get(f"https://web.whatsapp.com/send?phone={phone}")

        box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//footer//div[@contenteditable='true']")
        ))

        time.sleep(3)

        try:
            driver.execute_script("arguments[0].click();", box)
            time.sleep(1)

            box.send_keys(message)
            time.sleep(1)

            # press ENTER to send
            box.send_keys("\n")

            print(f"✅ Text sent to {phone}")

        except Exception as e:
            try:
                driver.save_screenshot(f"text_error_{phone}.png")
            except:
                pass
            raise Exception(f"Text send failed: {e}")

    def send_image(self, phone, image_path, caption=""):
        if self.driver is None:
            self.start()

        image_path = os.path.abspath(image_path)
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        driver, wait = self.driver, self.wait

        print(f"📞 Opening chat with {phone}...")
        driver.get(f"https://web.whatsapp.com/send?phone={phone}")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//footer//div[@contenteditable='true']")
        ))
        time.sleep(4)

        # Upload image
        file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        if not file_inputs:
            raise Exception("No file input element found")

        target_input = None
        for fi in file_inputs:
            accept = (fi.get_attribute("accept") or "").lower()
            if "image" in accept or "video" in accept or accept == "":
                target_input = fi
                break
        if not target_input:
            target_input = file_inputs[0]

        target_input.send_keys(image_path)
        print("📂 Image uploaded, waiting preview...")
        time.sleep(7)

        # Caption
        if caption:
            try:
                boxes = driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
                if boxes:
                    cap = boxes[-1]
                    driver.execute_script("arguments[0].click();", cap)
                    time.sleep(1)
                    cap.send_keys(caption)
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ Caption skip: {e}")

        # Send
        send_xpaths = [
            "//div[@role='button'][@aria-label='Send']",
            "//span[@data-icon='send']",
            "//span[@data-icon='wds-ic-send-filled']",
            "//button[@aria-label='Send']",
            "//div[@aria-label='Send']",
        ]
        sent = False
        for xp in send_xpaths:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                driver.execute_script("arguments[0].click();", btn)
                sent = True
                break
            except:
                continue

        if not sent:
            try:
                driver.save_screenshot(f"error_{phone}.png")
            except:
                pass
            raise Exception("Send button not found")

        print("⏳ Waiting upload to finish...")
        time.sleep(10)
        print(f"✅ Sent to {phone}")

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None


# ===== TEST =====
if __name__ == "__main__":
    s = WhatsAppSender()
    try:
        s.start()
        s.send_text("+919391187938", "HI FIRST MESSAGE")
        time.sleep(2)
        s.send_image("+919391187938", "img.jpg")
    finally:
        s.quit()