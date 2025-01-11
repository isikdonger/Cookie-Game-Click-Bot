import os

import keyboard
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time


# Optional - Keep the browser open (helps diagnose issues if the script crashes)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

driver.get("http://orteil.dashnet.org/experiments/cookie/")

# Get cookie to click on.
cookie = driver.find_element(by=By.ID, value="cookie")

# Get upgrade item ids.
items = driver.find_elements(by=By.CSS_SELECTOR, value="#store div")
item_ids = [item.get_attribute("id") for item in items]

import_button = driver.find_element(By.ID, "importSave")
import_button.click()
time.sleep(0.5)
alert = driver.switch_to.alert
with open("save_hash.txt", "r") as file:
    save_hash_from_file = file.read()
    alert.send_keys(save_hash_from_file)
alert.accept()

timeout = time.time() + 5

cookie_upgrades = {}
item_prices = []
cookie_count = 0


def update_upgrades():
    # Get all upgrade <b> tags
    all_prices = driver.find_elements(by=By.CSS_SELECTOR, value="#store b")
    item_prices = []

    # Convert <b> text into an integer price.
    for price in all_prices:
        element_text = price.text
        if element_text != "":
            cost = int(element_text.split("-")[1].strip().replace(",", ""))
            item_prices.append(cost)

    # Store items and prices in a dictionary
    for n in range(len(item_prices)):
        cookie_upgrades[item_prices[n]] = item_ids[n]


# The logic to check for window close or ESC key press
def is_window_open(driver):
    try:
        # Check if the current window handle is still valid
        driver.current_window_handle
        return True
    except:
        return False


while True:
    cookie.click()

    # Every 5 seconds:
    if time.time() > timeout:
        update_upgrades()

        # Get current cookie count
        money_element = driver.find_element(by=By.ID, value="money").text
        if "," in money_element:
            money_element = money_element.replace(",", "")
        cookie_count = int(money_element)

        # Find upgrades that we can currently afford
        affordable_upgrades = {}
        for cost, id in cookie_upgrades.items():
            if cookie_count > cost:
                affordable_upgrades[cost] = id

        # Purchase the most expensive affordable upgrade
        highest_price_affordable_upgrade = max(affordable_upgrades)
        to_purchase_id = affordable_upgrades[highest_price_affordable_upgrade]

        driver.find_element(by=By.ID, value=to_purchase_id).click()

        # Add another 5 seconds until the next check
        timeout = time.time() + 5

    # After 5 minutes stop the bot and check the cookies per second count.
    if not is_window_open(driver) or keyboard.is_pressed("esc"):
        time.sleep(1)
        update_upgrades()
        save_hash = f"0.1251|{cookie_count}"
        index = 0
        amounts = driver.find_elements(By.CLASS_NAME, "amount")
        for key, value in cookie_upgrades.items():
            amount = "0"
            if index < len(amounts):
                amount = amounts[index].text
                index += 1
            save_hash += f"|{amount}|{key}"
        with open("save_hash.txt", "w") as file:
            file.write(save_hash)
        driver.find_element(By.ID, "exportSave").click()
        break


driver.quit()
