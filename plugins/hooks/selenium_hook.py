from airflow.hooks.base_hook import BaseHook
from airflow.providers.selenium.hooks.selenium import SeleniumHook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Any

class CustomSeleniumHook(SeleniumHook):
    def __init__(self, chrome_options: Any = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chrome_options = chrome_options or webdriver.ChromeOptions()

    def get_driver(self, driver: Any = None) -> Any:
        if driver is None:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        return driver
