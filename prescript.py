from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


def generate_prescript():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get("https://nyos.dev/prescript")

        time.sleep(2)

        button = driver.find_element(By.ID, "prescript")
        button.click()

        time.sleep(2)

        return button.text

    finally:
        driver.quit()