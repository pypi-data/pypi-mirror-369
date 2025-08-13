import logging

from sapioseleniumlib.util.driver import BrowserType, SapioSeleniumDriver
from sapioseleniumlib.widgets import pages
from sapioseleniumlib.widgets.do import Do
from testconfig import username, password, headless, HOMEPAGE_URL

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.DEBUG)

sapio_driver.selenium_driver.set_window_size(1920, 1080)
do = Do(sapio_driver, 30, username, password)
do.home_page()

current_group = pages.MainPage(sapio_driver).west_panel.quick_access_toolbar.current_group
print("Current Group is: " + current_group)
exit(0)
