from __future__ import annotations

import random
from typing import List, Optional

from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from sapioseleniumlib.util.driver import SapioSeleniumDriver, SapioVersion
from sapioseleniumlib.widgets import windowobj


class LocationPickerDialog(windowobj.VeloxDialog):
    @staticmethod
    def get_location_picker_dialog(title: str, sapio_driver: SapioSeleniumDriver):
        """
        Get a location picker for an ELN notebook experiment.
        """
        dialog = windowobj.VeloxDialog.get_dialog_with_title_containing(title, sapio_driver)
        return LocationPickerDialog(dialog, dialog.main_element)

    def select_first_location(self) -> None:
        """
        In the dialog pick the first location in the dialog result as where my experiment will go and close.
        """
        self.sapio_driver.click(self.body.find_element(By.XPATH, "./div[2]//td/div"))

    def make_default(self) -> None:
        self.click_bottom_dialog_button("Make this my default location")


class IconPickerDialog(windowobj.VeloxDialog):
    @staticmethod
    def get_icon_picker_dialog(sapio_driver: SapioSeleniumDriver):
        """
        Get a dialog to pick icons that is currently being displayed.
        """
        dialog = windowobj.VeloxDialog.get_dialog_with_title_containing("Choose the Icon", sapio_driver)
        return IconPickerDialog(dialog, dialog.main_element)

    def pick_random_icon(self):
        """
        Select an arbitrary icon in the dialog and close.
        """
        icons = self.wait_for_many(
            lambda d: self.main_element.find_elements(By.CSS_SELECTOR, ".velox-listview-listview-cell")
        )
        icon = icons[0]
        actions = ActionChains(self.sapio_driver.selenium_driver)
        rect = windowobj.Rectangle(icon.rect)
        actions.move_to_element_with_offset(icon, 0, (rect.height//-2)+1)
        actions.double_click()
        actions.perform()


class StorageDialog(windowobj.VeloxDialog):
    @staticmethod
    def get_storage_dialog_with_title(title: str, sapio_driver: SapioSeleniumDriver):
        """
        Returns the storage dialog object that currently has the provided dialog title.
        """
        return StorageDialog(None,
                             windowobj.VeloxDialog.get_dialog_with_title(title, sapio_driver).main_element,
                             driver=sapio_driver)

    @property
    def _right_side(self) -> WebElement:
        if self.sapio_driver.target_sapio_version == SapioVersion.V23_12:
            return self.body.find_element(By.XPATH, "./div/div/div[1]")
        return self.body.find_elements(By.XPATH, "./div/div/div[1]")[1]

    @property
    def _storage_units_panel(self) -> WebElement:

        # self.sapio_driver.highlight(self._right_side, False)

        if self.sapio_driver.target_sapio_version in [SapioVersion.V23_12, SapioVersion.V24_12]:
            return self.wait_for(
                lambda d: self._right_side.find_element(By.XPATH, "./div/div[2]/div[1]/div/div[2]/div[3]/div/div/div")
            )
        else:
            return self.wait_for(
                lambda d: (
                    # there may be a div with a warning message in it -- so check for a fourth div first; if there's
                    # only three divs then the warning message is not present, and we can use the third div
                    self._try_find_element_on_right_side("./div/div[2]/div[1]/div/div[2]/div[4]/div/div/div") or
                    self._try_find_element_on_right_side("./div/div[2]/div[1]/div/div[2]/div[3]/div/div/div")
                )
            )

    def _try_find_element_on_right_side(self, xpath: str) -> Optional[WebElement]:
        try:
            return self._right_side.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    @property
    def _storage_units(self) -> List[WebElement]:
        return self.wait_for_many(
            lambda d: self._storage_units_panel.find_elements(By.XPATH, "./div[contains(@class,\"nodeHtmlOverlay\")]")
        )

    @property
    def _empty_storage_units(self) -> List[WebElement]:
        return self.wait_for_many(
            lambda d: self._storage_units_panel.find_elements(
                By.XPATH, "./div[contains(@class,\"nodeHtmlOverlay\")][not(p)]"
            )
        )

    def get_empty_storage_unit(self) -> Optional[WebElement]:

        # in cases where the storage unit has no defined dimensions, there will be a single storage unit and it will
        # always appear occupied.  If we detect only a single unit, just return it.
        units = self._storage_units
        if len(units) == 1:
            return units[0]

        # more than one unit was found, so look for empty ones
        units = self._empty_storage_units
        if units:
            # return a random storage unit (this helps defeat contention when running scale tests)
            return random.choice(units)

        return None

    @property
    def _left_side(self):
        return self.wait_for(
            lambda d: self.body.find_element(By.XPATH, "./div/div/div[2]")
        )

    @property
    def grid(self) -> windowobj.VeloxGrid:
        """
        The table grid of items to store.
        """
        ele: WebElement = self.wait_for(
            lambda d: self._left_side.find_element(
                By.XPATH, "./div[2]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div")
        )
        return windowobj.VeloxGrid(self, ele)

    def place_all_into_storage(self):
        """
        Place all items in GUI into storage towards all empty spots. This won't place items that overflows the storage.
        """
        # select all in grid
        grid = self.grid
        grid.select_all()

        # drag from row 1 to empty storage container
        rect: windowobj.Rectangle = windowobj.Rectangle(self.grid.body.rect)
        storage_units_panel_rect = windowobj.Rectangle(self._storage_units_panel.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(grid.body, rect.width // -2 + 5, rect.height // -2 + 5)
        actions.click_and_hold().move_to_element(self._storage_units_panel).pause(.5)
        actions.move_to_element_with_offset(self._storage_units_panel, storage_units_panel_rect.width // -2 + 5,
                                            storage_units_panel_rect.height // -2 + 5)
        actions.move_to_element(self.get_empty_storage_unit()).pause(1).release()
        actions.pause(1.5)
        actions.perform()
