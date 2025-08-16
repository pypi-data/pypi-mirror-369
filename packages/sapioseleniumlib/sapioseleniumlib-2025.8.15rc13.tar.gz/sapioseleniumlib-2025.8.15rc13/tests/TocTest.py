import logging
from datetime import datetime

from selenium.webdriver import Keys, ActionChains

from sapioseleniumlib.util.driver import BrowserType, SapioSeleniumDriver
from sapioseleniumlib.widgets.do import Do
from testconfig import username, password, headless, HOMEPAGE_URL

sapio_driver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, headless=headless)

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.INFO)

sapio_driver.selenium_driver.set_window_size(1920, 1080)
do = Do(sapio_driver, 30, username, password)

# make a new experiment
experiment = do.create_ad_hoc_experiment()

# add two additional tabs to the experiment
experiment.add_tab("Test Tab 2")
experiment.add_tab("Test Tab 3")

# add ten text entries to each tab
for i in range(3):
    for j in range(10):
        # add the entry
        experiment.add_entry_to_top(["Experiment Notes"])
        # wait half a second for it to render and focus
        sapio_driver.wait_seconds(0.5)
        # it already has focus, so just send some keys
        sapio_driver.send_keys("This is entry #" + str((i * 10) + j))
        # send a shift+tab so that we blur the entry
        ActionChains(sapio_driver.selenium_driver).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    if i < 2:
        # select the next tab (log the tab name first, though)
        logging.info("Selecting Test Tab " + str(i + 2))
        experiment.select_tab("Test Tab " + str(i + 2))
        # wait a second for it to render
        sapio_driver.wait_seconds(1)

# click on some entries and take screenshots
entry_numbers = [8, 18, 28]

for entry_number in entry_numbers:
    entry_text = f"This is entry #{entry_number}"
    got_text = f"got number {entry_number}"
    screenshot_name = f"screenshot-TocTest-{entry_number}-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.png"

    experiment.toc.click_entry_containing_text(entry_text)
    sapio_driver.wait_seconds(0.5)
    sapio_driver.send_keys(got_text)
    sapio_driver.wait_seconds(0.5)
    sapio_driver.take_screenshot(screenshot_name)


exit(0)
