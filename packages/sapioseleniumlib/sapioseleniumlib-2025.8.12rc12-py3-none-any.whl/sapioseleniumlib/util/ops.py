from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from sapioseleniumlib.util.driver import SapioSeleniumDriver


def choose_item_from_popup_list(item: str, sapio_driver: SapioSeleniumDriver) -> None:
    def condition(dummy: WebDriver):
        # popup will be last div of the body
        popup = sapio_driver.wait_for(lambda x: sapio_driver.selenium_driver.find_element(
            By.XPATH, "//body/div[last()]"
        ))
        scroller = sapio_driver.wait_for(lambda x: popup.find_element(
            By.XPATH, "./div/div"
        ))
        at_max_bottom = False
        while not at_max_bottom:
            # Keep scrolling until we find the item or hit the end.
            at_max_bottom = sapio_driver.at_max_scroll_bottom(scroller)
            list_items = sapio_driver.wait_for_many(lambda d: scroller.find_elements(
                By.XPATH, "./div"
            ))
            for cur_item in list_items:
                if item.lower() == cur_item.text.lower():
                    cur_item.click()
                    sapio_driver.wait(3)
                    return True
            sapio_driver.scroll_down(scroller)
        # hit the end and didn't find the item.
        return True

    sapio_driver.stale_wait().until(condition)


def choose_index_from_popup_list(index: int, sapio_driver: SapioSeleniumDriver) -> None:
    # If we need to scroll the list, keep track of how many items we already saw.
    # Pick lists/selection lists for dropdown fields get deduplicated, so we can use a set to track
    # what has already been accounted for.
    seen: set[str] = set()

    def condition(dummy: WebDriver):
        nonlocal seen
        # Popup will be last div of the body.
        popup = sapio_driver.wait_for(lambda x: sapio_driver.selenium_driver.find_element(
            By.XPATH, "//body/div[last()]"
        ))
        scroller = sapio_driver.wait_for(lambda x: popup.find_element(
            By.XPATH, "./div/div"
        ))
        at_max_bottom = False
        while not at_max_bottom:
            # Keep scrolling until we find the index or hit the end.
            at_max_bottom = sapio_driver.at_max_scroll_bottom(scroller)
            list_items = sapio_driver.wait_for_many(lambda d: scroller.find_elements(
                By.XPATH, "./div"
            ))
            # Which items exist on screen that don't exist in the list of seen items? These are the new
            # items revealed by scrolling.
            visible: list[str] = [x.text.lower() for x in list_items]
            new_strings: set[str] = set(visible).difference(seen)
            # If the total number of items seen or new is greater than the index to click on, then that
            # index is currently clickable.
            if len(seen) + len(new_strings) > index:
                # We need to offset the index to click on by the number of items that aren't visible. Those items that
                # aren't visible are the ones that we've seen but which aren't currently on screen.
                index_offset = len(seen.difference(visible))
                list_items[index - index_offset].click()
                sapio_driver.wait(3)
                return True
            # Track the new items currently on screen and scroll down to reveal more.
            seen.update(new_strings)
            sapio_driver.scroll_down(scroller)
        # Hit the end and didn't find the item.
        return True

    sapio_driver.stale_wait().until(condition)
