import logging
import sys
from datetime import datetime

from sapioseleniumlib.util.driver import SapioSeleniumDriver, BrowserType
from sapioseleniumlib.widgets.do import Do
from sapioseleniumlib.widgets.eln import ElnExperimentPage
from testconfig import username, password, HOMEPAGE_URL, headless

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logging.getLogger().setLevel(logging.DEBUG)

sapio_driver.selenium_driver.maximize_window()
do = Do(sapio_driver, 30, username, password)

ad_hoc_experiment: ElnExperimentPage = do.create_ad_hoc_experiment()
tab_name = "Tab " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

ad_hoc_experiment.add_tab(tab_name)
sapio_driver.wait_seconds(2)

ad_hoc_experiment.select_tab(tab_name)
sapio_driver.wait_seconds(2)

# Select back default tab.
ad_hoc_experiment.select_tab("Procedure Details")
sapio_driver.wait_seconds(2)

ad_hoc_experiment.select_tab(tab_name)
sapio_driver.wait_seconds(2)
