import logging
import sys

from selenium.webdriver.remote.webelement import WebElement

from sapioseleniumlib.util.driver import SapioSeleniumDriver, BrowserType
from sapioseleniumlib.widgets import windowobj
from sapioseleniumlib.widgets.do import Do
from sapioseleniumlib.widgets.eln import ElnExperimentPage
from sapioseleniumlib.widgets.pages import BasePage
from sapioseleniumlib.widgets.toolbars import ElnToolbar
from testconfig import username, password, HOMEPAGE_URL, headless

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)
cancel_exp_text = "Cancel Experiment"


def get_button_with_text_with_new_line(p: BasePage):
    cancel_experiment = windowobj.VeloxButton.get_button_with_text("Cancel\nExperiment", p)
    logging.info("button text is: " + cancel_experiment.button_text)
    cancel_experiment = windowobj.VeloxButton.get_button_with_text(cancel_exp_text, p)
    logging.info("button text is: " + cancel_experiment.button_text)


def get_button_with_text_element(element: WebElement):
    cancel_experiment = windowobj.VeloxButton.get_button_with_text_in_element(cancel_exp_text, sapio_driver, element)
    logging.info("button text is: " + cancel_experiment.button_text)


def get_button_with_nothing():
    cancel_experiment = windowobj.VeloxButton.get_button_with_text_in_element(cancel_exp_text, sapio_driver)
    logging.info("button text is: " + cancel_experiment.button_text)


sapio_driver.selenium_driver.maximize_window()
do = Do(sapio_driver, 30, username, password)

do.switch_group("Seamless LIMS")
ad_hoc_experiment: ElnExperimentPage = do.create_ad_hoc_experiment()
eln_toolbar: ElnToolbar = ad_hoc_experiment.eln_toolbar
get_button_with_text_with_new_line(eln_toolbar)
get_button_with_text_element(ad_hoc_experiment.main_element)
get_button_with_text_with_new_line(ad_hoc_experiment)
get_button_with_nothing()
sapio_driver.wait(3)
