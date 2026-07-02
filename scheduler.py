from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_image(phone, image_path, caption=""):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)

    driver.get(f"https://web.whatsapp.com/send?phone={phone}")

    input("Scan QR & press Enter...")

    attach = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@title="Attach"]')))
    attach.click()

    file_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@type="file"]')))
    file_input.send_keys(image_path)

    time.sleep(3)

    if caption:
        caption_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        caption_box.send_keys(caption)

    send_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//span[@data-icon="send"]')))
    send_btn.click()

    print("✅ Sent")
    time.sleep(5)
    driver.quit()