from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def upload_culture(name, by, description, file_path, thumbnail_path):
    driver = webdriver.Edge()
    driver.get("https://culturovaultignicion.pythonanywhere.com/")

    driver.find_element(By.NAME, "name").send_keys(name)
    driver.find_element(By.NAME, "by").send_keys(by)
    driver.find_element(By.NAME, "description").send_keys(description)
    driver.find_element(By.NAME, "file").send_keys(file_path)
    driver.find_element(By.NAME, "thumbnail").send_keys(thumbnail_path)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)
    driver.quit()
    print(f"✅ Uploaded '{name}' by {by}")
