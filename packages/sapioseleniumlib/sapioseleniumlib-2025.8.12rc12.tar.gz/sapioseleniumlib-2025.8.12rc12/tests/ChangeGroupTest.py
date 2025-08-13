import logging
import sys

from sapioseleniumlib.util.driver import SapioSeleniumDriver, BrowserType
from sapioseleniumlib.widgets import pages
from sapioseleniumlib.widgets.do import Do
from testconfig import username, password, headless, HOMEPAGE_URL

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

sapio_driver.selenium_driver.set_window_size(1920, 1080)
do = Do(sapio_driver, 30, username, password)
do.home_page()


def other_group(group: str):
    if "Lab Techs" == group:
        return "Sapio Admin"
    return "Lab Techs"


current_group = pages.MainPage(sapio_driver).west_panel.quick_access_toolbar.current_group
logging.info(current_group)

next_group = other_group(current_group)
logging.info("Switching to: " + next_group)
do.switch_group(next_group)

next_group = other_group(next_group)
logging.info("Switching to: " + next_group)
do.switch_group(next_group)

sapio_driver.wait(3)
exit(0)
