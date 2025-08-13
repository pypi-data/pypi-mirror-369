import logging
import sys

from sapioseleniumlib.util.driver import SapioSeleniumDriver, BrowserType
from sapioseleniumlib.widgets.do import Do
from sapioseleniumlib.widgets.eln import ElnExperimentPage
from testconfig import HOMEPAGE_URL, username, password

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=False)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

sapio_driver.selenium_driver.set_window_size(1920, 1080)
do = Do(sapio_driver, 30, username, password)

do.login()

do.navigate_to('#experimentEntryId=817910;group=18;notebookExperimentId=817905;view=eln')

exp = ElnExperimentPage(sapio_driver)

# exp.get_eln_table_entry_with_title('Samples').grid.scroll_column_into_view("Collaborator")
exp.get_eln_table_entry_with_title('Samples').grid.set_value(1, "Collaborator", "test again")

sapio_driver.wait_seconds(5)
