import time
from asyncio import sleep
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from xync_schema.models import PmAgent


async def login(agent: PmAgent):
    driver = uc.Chrome(no_sandbox=True)
    # driver.implicitly_wait(10)
    driver.get("https://payeer.com/ru/auth")
    try:
        time.sleep(5)
        driver.find_element(By.CLASS_NAME, "button.button_empty").click()
        driver.find_element(By.NAME, "email").send_keys(agent.auth.get("email"))
        driver.find_element(By.NAME, "password").send_keys(agent.auth.get("password"))
        driver.find_element(By.CLASS_NAME, "login-form__login-btn.step1").click()
        await sleep(5)
        driver.find_element(By.CLASS_NAME, "login-form__login-btn.step1").click()
        await sleep(1)
        if (v := driver.find_elements(By.CLASS_NAME, "form-input-top")) and v[0].text == "Введите проверочный код":
            code = input("Email code: ")
            actions = ActionChains(driver)
            for char in code:
                actions.send_keys(char)
                actions.perform()
            driver.find_element(By.CLASS_NAME, "login-form__login-btn.step2").click()

        agent.state = {"cookies": driver.get_cookies()}
        await agent.save()
    finally:
        driver.quit()
