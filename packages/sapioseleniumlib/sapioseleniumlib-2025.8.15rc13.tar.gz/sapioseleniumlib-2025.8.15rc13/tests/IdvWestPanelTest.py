import logging
import sys

from sapioseleniumlib.util.driver import SapioSeleniumDriver, BrowserType
from sapioseleniumlib.widgets import pages
from sapioseleniumlib.widgets import panels
from sapioseleniumlib.widgets.do import Do
from testconfig import username, password, HOMEPAGE_URL, headless

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logging.getLogger().setLevel(logging.DEBUG)

sapio_driver.selenium_driver.maximize_window()
do = Do(sapio_driver, 30, username, password)


def directory_test_suite():
    do.navigate_to("#dataType=Directory;recordId=1;view=dataRecord")
    sapio_driver.wait_seconds(3)
    main_page = pages.MainPage(sapio_driver)
    main_idv: panels.IntegratedDataView = main_page.integrated_data_view
    has_west_panel: bool = main_idv.has_west_panel
    if not has_west_panel:
        raise ValueError("Directory type IDV should have west panel")
    west_panel = main_idv.west_panel
    if west_panel.can_add_linked_record:
        # click add link then hide add links menu
        west_panel.click_add_link_record()
        sapio_driver.wait_seconds(.5)
        west_panel.click_add_link_record()
        sapio_driver.wait_seconds(.5)
    if west_panel.can_add_linked_record_of_type("Studies"):
        west_panel.click_add_linked_record_of_type("Studies")
    sapio_driver.wait_seconds(2)


do.main_view()
directory_test_suite()
