"""
This module holds Sapio standard dialog object POSM classes.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Dict, Tuple, Optional, List, Callable

from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.relative_locator import locate_with

from sapioseleniumlib.util.driver import SapioSeleniumDriver, TOASTR_XPATH, BrowserType
from sapioseleniumlib.util.ops import choose_item_from_popup_list
from sapioseleniumlib.widgets.pagedef import BasePageObject, PageElementSearchMethod, BasePage


class TextSearchType(Enum):
    EXACT = 0
    CONTAINS = 1
    STARTS_WITH = 2


class VeloxButton(BasePageObject):
    XPATH = ".//div[div/div[contains(@class,'veloxButtonFrameTemplate')]]"
    OVERFLOW_XPATH = XPATH + "[*//div[contains(@class,'velox-cached-icon')][contains(@style,'Lz48L3N2Zz4')]]"
    PLUS_XPATH = ".//div[contains(@class,'velox-cached-icon')][contains(@style," \
                 "'OEwgMTguOTk5NCwxMi45OTggWiAiLz48L3N2Zz4')]"

    @classmethod
    def get_object_elements(cls) -> Dict[str, Tuple[PageElementSearchMethod, str]]:
        return dict()

    @property
    def icon_name(self) -> Optional[str]:
        return self.get_icon_name()

    def get_icon_name(self) -> Optional[str]:
        """
        Returns the class name that specifies the icon being used.  Will likely start with something like "svg-native-".
        """
        if not self.sapio_driver.exists_in_element(self.main_element, By.CLASS_NAME, "velox-cached-icon"):
            return None
        icon_container: Optional[WebElement] = self.parent.find_element(By.CLASS_NAME, "velox-cached-icon")
        if icon_container is None:
            return None
        splits: List[str] = icon_container.get_attribute("className").split(" ")
        for split in splits:
            if "velox-cached-icon" != split:
                return split
        return None

    @property
    def button_text(self) -> str:
        return self.get_button_text()

    def get_button_text(self):
        """
        Return the text of the button.
        """
        return self.parent.text

    @property
    def is_plus_button(self) -> bool:
        return self.sapio_driver.exists_in_element(self.main_element, By.XPATH, VeloxButton.PLUS_XPATH)

    @staticmethod
    def get_buttons_with_text(text: str, parent_page: BasePage,
                              timeout_seconds: float | None = None,
                              search_type: TextSearchType = TextSearchType.EXACT) -> List[VeloxButton]:
        """
        Get all buttons under parent element
        """

        if timeout_seconds is None:
            timeout_seconds = parent_page.timeout_seconds

        normalized_text: str = SapioSeleniumDriver.normalize_text(text)
        element = parent_page.main_element
        button_elements: List[WebElement] = parent_page.sapio_driver.wait_for_many(
            lambda d: element.find_elements(By.XPATH, VeloxButton.XPATH), timeout_seconds)
        ret: List[VeloxButton] = []
        for button_element in button_elements:
            if not button_element.is_displayed():
                continue
            button = VeloxButton(parent_page, button_element)
            to_add: bool
            cur_button_text: str = SapioSeleniumDriver.normalize_text(button.get_button_text())
            if search_type == TextSearchType.EXACT:
                to_add = cur_button_text == normalized_text
            elif search_type == TextSearchType.STARTS_WITH:
                to_add = cur_button_text.startswith(normalized_text)
            elif search_type == TextSearchType.CONTAINS:
                to_add = normalized_text in cur_button_text
            else:
                raise ValueError("Invalid search type: " + str(search_type))
            if to_add:
                ret.append(button)
        return ret

    @staticmethod
    def get_button_with_text(text: str, parent_page: BasePage,
                             timeout_seconds: float | None = None,
                             search_type: TextSearchType = TextSearchType.EXACT) -> Optional[VeloxButton]:

        if timeout_seconds is None:
            timeout_seconds = parent_page.timeout_seconds

        ret: List[VeloxButton] = VeloxButton.get_buttons_with_text(text, parent_page, timeout_seconds, search_type)
        if not ret:
            return None
        return ret[0]

    @staticmethod
    def _get_button_with_icon(icon_text: str, parent_page: BasePage, timeout_seconds: float | None = None) -> \
            List[VeloxButton]:
        """
        Get all buttons with given icon name.
        """

        if timeout_seconds is None:
            timeout_seconds = parent_page.timeout_seconds

        element = parent_page.main_element
        button_elements = parent_page.sapio_driver.wait_for_many(
            lambda d: element.find_elements(By.XPATH, VeloxButton.XPATH), timeout_seconds)
        ret: List[VeloxButton] = []
        for button_element in button_elements:
            # Could be hidden under "..." hamburger menu.
            # if not button_element.is_displayed():
            #     continue
            button = VeloxButton(parent_page, button_element)
            icon_name = button.get_icon_name()
            if not icon_name:
                continue
            if icon_text.lower() in icon_name.lower():
                ret.append(button)
        return ret

    @staticmethod
    def get_button_with_icon(icon_text: str, parent_page: BasePage, timeout_seconds: float | None = None) \
            -> Optional[VeloxButton]:

        if timeout_seconds is None:
            timeout_seconds = parent_page.timeout_seconds

        ret: List[VeloxButton] = VeloxButton._get_button_with_icon(icon_text, parent_page, timeout_seconds)
        if not ret:
            return None
        return ret[0]

    @staticmethod
    def get_buttons_by_element(element: WebElement, sapio_driver: SapioSeleniumDriver):
        """
        In this case we don't have a parent base object to get element from.
        """
        button_elements: List[WebElement] = sapio_driver.wait_for_many(
            lambda d: element.find_elements(By.XPATH, VeloxButton.XPATH)
        )
        ret: List[VeloxButton] = []
        for e in button_elements:
            if e.is_displayed():
                b = VeloxButton(parent_page=None, main_element=e, driver=sapio_driver)
                ret.append(b)
        return ret

    @staticmethod
    def get_button_with_text_in_element(text: str, sapio_driver: SapioSeleniumDriver,
                                        element: Optional[WebElement] = None) \
            -> Optional[VeloxButton]:
        """
        Calls get_buttons_by_element then filter on the text.
        """
        if element is None:
            element = sapio_driver.selenium_driver.find_element(By.TAG_NAME, "body")
        normalized_text = sapio_driver.normalize_text(text)
        buttons = VeloxButton.get_buttons_by_element(element, sapio_driver)
        for button in buttons:
            if normalized_text.lower() == sapio_driver.normalize_text(button.text).lower():
                return button
        return None


class VeloxPanel(BasePageObject):
    """
    A VeloxPanel, really.
    """

    @property
    def header(self) -> WebElement:
        """
        Header of the panel.
        """
        return self.main_element.find_element(By.CSS_SELECTOR, "[data-panel-header]")

    @property
    def header_text_normalized(self) -> str:
        """
        Normalized header text of the panel.
        """
        header: WebElement = self.header
        return self.sapio_driver.normalize_text(header.find_element(By.XPATH, "./table/tr/td[2]/table/tr/td[1]").text)

    @property
    def body(self) -> WebElement:
        """
        Body of the panel.
        """
        return self.main_element.find_element(By.CSS_SELECTOR, "[data-panel-body]")

    @property
    def component_panels(self) -> List[VeloxPanel]:
        """
        Get all panels within this panel.
        """
        component_divs: List[WebElement] = self.wait_for_many(lambda d: self.body.find_elements(
            By.XPATH, "./div/div/div/div[@data-component-type]"))
        ret: List[VeloxPanel] = list()
        for div in component_divs:
            div = self.wait_for(lambda d: div)
            if div:
                ret.append(VeloxPanel(self, div))
        return ret

    @property
    def form(self) -> VeloxForm:
        return VeloxForm(self, self.body)

    def get_component_with_title(self, title: str) -> Optional[VeloxPanel]:
        panels = self.component_panels
        normalized_title = self.sapio_driver.normalize_text(title)
        for panel in panels:
            if panel.header_text_normalized == normalized_title:
                return panel
        return None


class VeloxMenuItem(BasePageObject):
    """
    A choice in one of the menus.
    """
    X_PATH: str = "./div/div/div[.//a]"

    def has_icon(self, icon_name: str):
        """
        See if the icon name for this menu selection is of a specific name.
        """
        icon_divs = self.main_element.find_elements(By.XPATH, "./a/div")
        if not icon_divs:
            return False
        class_name = icon_divs[0].get_attribute("className")
        if not class_name:
            return False
        return icon_name.lower() in class_name.lower()


class VeloxMenu(BasePageObject):
    """
    A menu can be a overflow menu in a toolbar. Note this is NOT the main menu in the GUI snapped on the left.
    """
    X_PATH: str = './div[contains(@class,"menu-menu")]'

    @property
    def menu_items(self) -> List[VeloxMenuItem]:
        """
        menu items returned here will not be dynamic, as there is nothing that can be used to re-identify them
        """
        divs = self.wait_for_many(lambda d: self.main_element.find_elements(By.XPATH, VeloxMenuItem.X_PATH))
        return [VeloxMenuItem(self, main_element=x) for x in divs]

    @staticmethod
    def get_top_most_menu(sapio_driver: SapioSeleniumDriver, timeout_seconds: float | None = None) -> Optional[VeloxMenu]:
        """
        Returns the floating menu that was most recently added to the DOM.
        """

        if timeout_seconds is None:
            timeout_seconds = sapio_driver.default_timeout

        def supplier(driver: WebDriver):
            elements = driver.find_elements(By.XPATH, "//body/" + VeloxMenu.X_PATH)
            if not elements:
                return None
            return elements[-1]

        element: Optional[WebElement] = sapio_driver.wait(timeout_seconds).until(supplier)
        if element is None:
            return None
        return VeloxMenu(main_element=element, driver=sapio_driver)

    def get_menu_item_containing_text(self, text: str) -> Optional[VeloxMenuItem]:
        items = self.menu_items
        for item in items:
            if item.text and text.upper() in item.text.upper():
                return item
        return None

    def get_menu_item_with_text_equal_to(self, text: str) -> Optional[VeloxMenuItem]:
        items = self.menu_items
        for item in items:
            if item.text and text.upper() == item.text.upper():
                return item
        return None

    def click_menu_items(self, texts_to_click: List[str]):
        """
        Click through a series of nested floating menus starting from the current menu.
        As we know, when we select a menu item that pops up a sub-category, it will float another menu.
        This is a series to click from the first one until the last one.
        e.g.: Administration => Upgraders => Upgrader 1
        """
        first_run: bool = True
        for text in texts_to_click:
            if first_run:
                try:
                    self.get_menu_item_with_text_equal_to(text).click()
                except Exception as e:
                    self.get_menu_item_containing_text(text).click()
            else:
                VeloxMenu.get_top_most_menu(self.sapio_driver).click_menu_items([text])
            first_run = False


class VeloxToolbar(BasePageObject):
    CSS_CLASS: str = ".x-toolbar"

    @property
    def buttons(self):
        return self.get_buttons()

    def get_buttons(self) -> List[VeloxButton]:
        return VeloxButton.get_buttons_by_element(self.main_element, self.sapio_driver)

    def get_button_with_icon(self, icon_text: str) -> Optional[VeloxButton]:
        return VeloxButton.get_button_with_icon(icon_text, self)

    def get_button_contains_text(self, text_to_search: str):
        return VeloxButton.get_button_with_text(text_to_search, self, search_type=TextSearchType.CONTAINS)

    def get_button_containing_regex(self, pattern: str) -> Optional[VeloxButton]:
        regex: re.Pattern = re.compile(pattern)
        buttons = self.get_buttons()
        for button in buttons:
            text = self.sapio_driver.normalize_text(button.text)
            if not text:
                continue
            match = regex.match(text)
            if match:
                return button
        return None

    def get_button_or_menu_item_containing_text(self, text: str) -> Optional[VeloxButton]:
        """
        It's possible for a button to either appear directly in a toolbar or being overflowed into hamburger menu.
        Regardless, select the toolbar button with this text.
        """
        # Do I need to wait again or no? right now i am not. but it's already waiting in get_buttons()?
        buttons: List[VeloxButton] = self.get_buttons()
        normalized_text = self.sapio_driver.normalize_text(text)
        for button in buttons:
            if normalized_text in self.sapio_driver.normalize_text(button.get_button_text()):
                return button
        return None

    def click_auto_fill(self):
        auto_fill_button = self.get_button_with_icon("autofill")
        auto_fill_button.click()


class DialogExistsSearchType(Enum):
    EXACT = 0
    CONTAINS = 1
    STARTS_WITH = 2


class VeloxDialog(BasePageObject):
    BY_XPATH: str = "//div" + SapioSeleniumDriver.x_path_contains_class("velox-dialog-velox-panel-panel-body") + \
                    "[div[contains(@class,'velox-dialog-velox-panel-panel-header')]]"

    @property
    def button_strip(self) -> WebElement:
        return self._load_cached_element(
            "_button_strip", By.XPATH, "./div[2]/div/div/div/div[2]/div/div")

    @property
    def body(self) -> WebElement:
        return self._load_cached_element(
            "_body", By.XPATH, "./div[2]/div/div/div/div[1]/div")

    @property
    def button_strip_toolbar(self) -> VeloxToolbar:
        return VeloxToolbar(self, self.button_strip)

    @property
    def header_text(self) -> str:
        return self.wait_for(lambda d: self.main_element.find_element(
            By.CSS_SELECTOR, "[data-dialog-header]")).text

    @property
    def grid(self) -> VeloxGrid:
        return VeloxGrid(self, main_element=self.wait.until(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS)))

    def filter(self, text: str):
        filter_editor = self.wait_for(lambda d: self.main_element.find_element(By.TAG_NAME, "input"))
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(filter_editor)
        actions.click()
        actions.send_keys(Keys.CONTROL + "a" + Keys.CONTROL + Keys.BACKSPACE)
        actions.pause(.25)
        actions.send_keys(text)
        actions.pause(.25)
        actions.perform()

    def filter_and_select(self, text: str):
        """
        This assumes the dialog simply contains a filter and a grid and not much else. Will filter down the grid
        using the given text and then double-click the first grid cell it can find that is equal to the text.
        """
        self.filter(text)
        grid_ele: WebElement = self.wait.until(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS)
        )
        grid: VeloxGrid = VeloxGrid(self, grid_ele)
        cell: WebElement = self.wait_for(
            lambda d: grid.main_element.find_element(By.XPATH, ".//*" + self.sapio_driver.x_path_ci_text_equals(text))
        )
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.double_click(cell).perform()

    def filter_and_select_containing(self, text: str):
        """
        This assumes the dialog simply contains a filter and a grid and not much else. Will filter down the grid
        using the given text and then double-click the first grid cell it can find that contains the text.
        """
        self.filter(text)
        grid_ele: WebElement = self.wait.until(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS)
        )
        grid: VeloxGrid = VeloxGrid(self, grid_ele)
        cell: WebElement = self.wait_for(
            lambda d: grid.main_element.find_element(By.XPATH, ".//*" + self.sapio_driver.x_path_ci_contains(text))
        )
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.double_click(cell).perform()

    def click_bottom_dialog_button(self, button_text: str):
        """
        Click a button at the bottom of the dialog (OK/Cancel only usually)
        """
        # Firefox has the stupid tooltip blocking the click for a few seconds...
        # Unblock my toolbar from possible tooltip blocks.
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(self.body).perform()
        self.sapio_driver.wait_until_clickable(lambda d: self.button_strip_toolbar.
                                               get_button_contains_text(button_text).main_element)
        self.button_strip_toolbar.get_button_contains_text(button_text).main_element.click()

    def click_button_with_text(self, button_text: str, index: int = 0):
        """
        Find button within a dialog and click it.
        """
        VeloxButton.get_buttons_with_text(button_text, self)[index].click()

    def double_click_text(self, text: str):
        """
        Looks for an element in the dialog body with the given text and double-clicks it.
        """
        ele: WebElement = self.wait_for(
            lambda d: self.body.find_element(By.XPATH, ".//*" + self.sapio_driver.x_path_ci_text_equals(text))
        )
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.double_click(ele).pause(.1).perform()

    def get_form(self) -> VeloxForm:
        return VeloxForm(self, self.body)

    @staticmethod
    def get_top_most_dialog(sapio_driver: SapioSeleniumDriver, timeout_seconds: float | None = None) -> \
            Optional[VeloxDialog]:

        if timeout_seconds is None:
            timeout_seconds = sapio_driver.default_timeout

        wait = sapio_driver.wait(timeout_seconds)

        def supplier(driver: WebDriver) -> WebElement:
            dialogs = driver.find_elements(By.XPATH, VeloxDialog.BY_XPATH)

            max_z_index: int = -1
            top_most_dialog = None
            for dialog in dialogs:
                if not dialog.is_displayed():
                    continue
                z_index = int(dialog.value_of_css_property("z-index"))
                if z_index > max_z_index:
                    max_z_index = z_index
                    top_most_dialog = dialog
            return top_most_dialog

        element: WebElement = wait.until(supplier)
        if not element:
            return None
        return VeloxDialog(main_element=element, driver=sapio_driver, timeout_seconds=timeout_seconds)

    @staticmethod
    def get_dialog_with_title_containing(title: str, sapio_driver: SapioSeleniumDriver,
                                         timeout_seconds: float | None = None) -> Optional[VeloxDialog]:
        """
        Keep waiting until the top-most dialog has the expected window title.
        """

        if timeout_seconds is None:
            timeout_seconds = sapio_driver.default_timeout

        wait = sapio_driver.wait(timeout_seconds)

        def supplier(driver: WebDriver) -> Optional[VeloxDialog]:
            top_most_dialog = VeloxDialog.get_top_most_dialog(sapio_driver, timeout_seconds)
            if not top_most_dialog:
                return None
            top_most_header: str = top_most_dialog.header_text
            if title.upper() in top_most_header.upper():
                return top_most_dialog
            return None

        return wait.until(supplier)

    @staticmethod
    def get_dialog_with_title(title: str, sapio_driver: SapioSeleniumDriver, timeout_seconds: float | None = None) \
            -> Optional[VeloxDialog]:

        if timeout_seconds is None:
            timeout_seconds = sapio_driver.default_timeout

        wait = sapio_driver.wait(timeout_seconds, [NoSuchElementException, StaleElementReferenceException])

        def supplier(driver: WebDriver) -> Optional[VeloxDialog]:
            top_most_dialog = VeloxDialog.get_top_most_dialog(sapio_driver, timeout_seconds)
            if not top_most_dialog:
                return None
            if title.upper() == top_most_dialog.header_text.upper():
                return top_most_dialog
            return None

        return wait.until(supplier)

    @staticmethod
    def get_dialog_with_title_if_exists(title: str, sapio_driver: SapioSeleniumDriver) -> Optional[VeloxDialog]:
        # noinspection PyBroadException
        try:
            return VeloxDialog.get_dialog_with_title(title, sapio_driver, 0)
        except Exception as e:
            return None

    @staticmethod
    def get_dialog_with_title_starts_with(title: str, sapio_driver: SapioSeleniumDriver,
                                          timeout_seconds: float | None = None) -> Optional[VeloxDialog]:

        if timeout_seconds is None:
            timeout_seconds = sapio_driver.default_timeout

        wait = sapio_driver.wait(timeout_seconds)

        def supplier(driver: WebDriver) -> Optional[VeloxDialog]:
            top_most_dialog = VeloxDialog.get_top_most_dialog(sapio_driver, timeout_seconds)
            if not top_most_dialog:
                return None
            if top_most_dialog.header_text.upper().startswith(title.upper()):
                return top_most_dialog
            return None

        return wait.until(supplier)

    @staticmethod
    def dialog_exists(title: str, search_type: DialogExistsSearchType, sapio_driver: SapioSeleniumDriver,
                      timeout_seconds: float = 1) -> bool:
        """
        Returns true if a dialog is found matching the criteria.
        """
        if search_type == DialogExistsSearchType.EXACT:
            return sapio_driver.exists_by_supplier(
                lambda d: VeloxDialog.get_dialog_with_title(title, sapio_driver, timeout_seconds).main_element)
        elif search_type == DialogExistsSearchType.CONTAINS:
            return sapio_driver.exists_by_supplier(
                lambda d: VeloxDialog.get_dialog_with_title_containing(
                    title, sapio_driver, timeout_seconds).main_element)
        elif search_type == DialogExistsSearchType.STARTS_WITH:
            return sapio_driver.exists_by_supplier(
                lambda d: VeloxDialog.get_dialog_with_title_starts_with(
                    title, sapio_driver, timeout_seconds).main_element)
        return False

    def close(self):
        self.sapio_driver.click(self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[1]//div[contains(@class,\"velox-cached-icon\") and contains(" +
                          "@style,\"NDEsMTJMIDE5LDYuNDEgWiAiLz48L3N2Zz4=\")]")
        ))


class VeloxTabPanel(BasePageObject):
    CSS_SELECTOR: str = "[data-tab-panel]"

    @property
    def tab_list(self) -> List[WebElement]:
        tab_elements = self.wait_for_many(
            lambda d: self.main_element.find_elements(By.XPATH, "./div[1]/div[1]/ul/li"))
        # The last element is junk
        return tab_elements[0: max(0, len(tab_elements) - 1)]

    @property
    def tab_text_list(self) -> List[str]:
        return [x.text for x in self.tab_list]

    def has_tab(self, tab_text: str):
        texts_lower = [x.lower() for x in self.tab_text_list]
        return tab_text.lower() in texts_lower

    def get_tab_with_text(self, target: str) -> Optional[WebElement]:
        tab_list = self.tab_list
        target_lower = target.lower()
        for tab in tab_list:
            text = self.sapio_driver.get_inner_text(tab).lower()
            if text and text == target_lower:
                return tab
        return None

    def get_tab_containing_text(self, text: str):
        for tab in self.tab_list:
            inner_text = self.sapio_driver.get_inner_text(tab)
            if inner_text and text.lower() in inner_text.lower():
                return tab

    @property
    def active_tab(self) -> Optional[WebElement]:
        return self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH, "./div[1]/div[1]/ul/li[contains(@class,\"selected\")]"))

    @property
    def active_tab_text(self) -> Optional[str]:
        tab = self.active_tab
        if not tab:
            return None
        return tab.text

    @property
    def active_tab_contents(self):
        tab_list = self.tab_list
        active_tab_idx = 0
        for tab in tab_list:
            if "selected" in tab.get_attribute("class"):
                break
            active_tab_idx += 1
        if active_tab_idx >= len(tab_list):
            # we hit the end, and didn't find a selected tab.
            return None
        return self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH, "./div[2]/div/div[" + str(active_tab_idx + 1) + "]"))

    def click_tab_containing(self, tab_text: str):
        return self.sapio_driver.click(self.get_tab_containing_text(tab_text))

    def click_tab(self, tab_text: str):
        element: WebElement | None = self.wait.until(lambda d: self.get_tab_with_text(tab_text))
        if not element:
            raise ValueError("Tab not found: " + tab_text)
        return self.sapio_driver.click(element)


class VeloxDateEditor(BasePageObject):

    @property
    def main_element(self) -> WebElement:
        return self.sapio_driver.selenium_driver.find_element(
            By.XPATH, "//body/div[last()][//div[text()=\"Set as Now\"]]")

    def _get_scroller_elements(self) -> List[WebElement]:
        return self.sapio_driver.selenium_driver.find_elements(
            By.XPATH, "//body/div[last()]//div" + self.sapio_driver.x_path_contains_class(
                "velox-button-button-velox-menu-menu-scroller"))

    @property
    def up_scroller(self) -> Optional[WebElement]:
        """
        If the date editor is turned into a scrolled view then this is the "up scroller button"
        """
        elements = self._get_scroller_elements()
        if not elements:
            return None
        return elements[0]

    @property
    def down_scroller(self) -> Optional[WebElement]:
        """
        If the date editor is turned into a scrolled view then this is the "down scroller button"
        """
        elements = self._get_scroller_elements()
        if not elements:
            return None
        return elements[1]

    def set_as_today(self) -> None:
        def scroll_until_clickable(d: WebDriver) -> Optional[WebElement]:
            ret: WebElement = self.main_element.find_element(By.XPATH, ".//div[text()=\"Set as Now\"]")
            if not ret.is_displayed() or not self.sapio_driver.is_visible_in_viewport(ret):
                self.down_scroller.click()
                return None
            return ret

        today_button: WebElement = self.sapio_driver.wait().until(scroll_until_clickable)
        today_button.click()

    @staticmethod
    def get_date_editor(sapio_driver: SapioSeleniumDriver) -> VeloxDateEditor:
        element = sapio_driver.selenium_driver.find_element(
            By.XPATH, "//body/div[last()][//div[text()=\"Set as Now\"]]")
        return VeloxDateEditor(parent_page=None, main_element=element, driver=sapio_driver)


class ScrollAction(Enum):
    """
    The scrolling action performed.
    """
    NONE = 0
    DOWN = 1
    UP = 2


class VeloxGrid(BasePageObject):
    BY_CSS = ".velox-grid-grid-empty-area"
    auto_send_enter: bool

    def __init__(self, parent_page: BasePage = None, main_element: WebElement = None, relative_to_parent: bool = True,
                 driver: Optional[SapioSeleniumDriver] = None, timeout_seconds: Optional[float] = None):
        super().__init__(parent_page, main_element, relative_to_parent, driver, timeout_seconds)
        self.auto_send_enter = True

    @property
    def header(self) -> WebElement:
        return self._load_cached_element("_header", By.XPATH, "./div[2]/div")

    @property
    def body(self) -> WebElement:
        return self._load_cached_element("_body", By.XPATH, "./div[3]/div[1]")

    def double_click_row_number(self, row: int):
        row_element = self.wait_for(
            lambda d: self.get_row_by_number(row)[0]
        )
        rect = Rectangle(row_element.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(row_element, (rect.width // -2) + 5, 0).double_click()
        actions.perform()

    def set_value(self, row: int, column_name: str, value: Optional[str]):
        """
        Enter the value with the keyboard emulation into a particular location
        in the velox grid.
        """
        self.click_cell(row, column_name, click_twice=self.sapio_driver.browser_type == BrowserType.FIREFOX)

        # We are still doing ctrl+A instead of WebElement#clear because that will cause a commit test for blanks.
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.key_down(Keys.CONTROL).send_keys("A").key_up(Keys.CONTROL).pause(.25).send_keys(Keys.DELETE)
        actions.perform()
        self.sapio_driver.wait_seconds(.25)
        editor_element: WebElement = self._get_input_element_after_click()
        self.sapio_driver.wait_seconds(.25)
        editor_element.send_keys(value)
        self.sapio_driver.wait_seconds(.25)
        if self.auto_send_enter:
            editor_element: WebElement = self._get_input_element_after_click()
            editor_element.send_keys(Keys.ENTER)
            self.sapio_driver.wait_seconds(.25)

    def set_enum_value(self, row: int, column_name: str, value: str):
        """
        Set value via dropdown instead of typing.
        Should be something like a picklist.
        """
        self.click_cell(row, column_name)
        choose_item_from_popup_list(value, self.sapio_driver)

    def set_date_value_to_today(self, row: int, column_name: str):
        self.click_cell(row, column_name)
        VeloxDateEditor.get_date_editor(self.sapio_driver).set_as_today()
        self.sapio_driver.wait_seconds(2.5)

    def click_cell(self, row: int, column_name: str,
                   ctrl: bool = False, shift: bool = False, trigger: bool = False,
                   scrolled_already: bool = False, click_twice: bool = False) -> None:
        """
        Click on a cell by position
        :param click_twice: if true we will click the cell twice instead of once but not as double-click.
        Some browsers for some editors we need to do it twice (firefox eww)
        :param row: The row to click
        :param column_name: The column to key
        :param ctrl: Use ctrl key select
        :param shift: Use shift key select
        :param trigger: Whether to click on the center of the cell or the trigger button of the cell.
        :param align_to_top: how shall the alignment of the cell be aligned in response to scrolling action.
        :param scrolled_already: assume previously mouse is already at the cell position.
        This is in case we need to click a button and click another button inside. scrolling again invalidates.
        """

        # first make sure the grid is clickable before we try to click on anything
        # but if we're in-progress, let's not wait again.
        if not scrolled_already:
            self.sapio_driver.wait_until_clickable(lambda d: self.body)

        actions = ActionChains(self.sapio_driver.selenium_driver)
        self._scroll_cell_into_view(row, column_name, trigger, scrolled_already)
        actions.pause(.25)
        if ctrl:
            actions.key_down(Keys.CONTROL)
        if shift:
            actions.key_down(Keys.SHIFT)
        actions.click()
        if click_twice:
            # Sometimes firefox click once doesn't give you editor you need to click again.
            # We also need to wait a while, so it is not being misrepresented as double click :(
            actions.pause(1.5)
            self._scroll_cell_into_view(row, column_name, trigger, scrolled_already)
            actions.click()
        if ctrl:
            actions.key_up(Keys.CONTROL)
        if shift:
            actions.key_up(Keys.SHIFT)
        actions.pause(.25)
        actions.perform()

    def click_cell_trigger(self, row: int, column_name: str):
        self.click_cell(row, column_name)
        self.sapio_driver.wait_seconds(.25)
        self.click_cell(row, column_name, False, False, trigger=True, scrolled_already=True)

    def get_cell_value(self, row: int, column_name: str) -> Optional[str]:
        cell_rect = self._scroll_cell_into_view(row, column_name, False)
        # (the near upper-left corner of the cell is more likely to be visible on screen than the middle of the
        # cell, so we'll target that instead of the dead center)
        # PR-46428: Add 5 to both the x and the y coordinates so that we don't aim at the border between cells
        # and potentially get the wrong element.
        cell_el = self.sapio_driver.get_element_at_point(cell_rect.x + 5, cell_rect.y + 5)
        return cell_el.text

    def select(self, start_row: int, start_column_name: str, end_row: int, end_column_name: str):
        """
        Make selection in grid (to prep for auto fill or some other buttons)
        """
        # self.sapio_driver.scroll_down(self._get_vertical_scroller(), True)
        self.sapio_driver.scroll_up(self._get_vertical_scroller(), True)
        self.sapio_driver.wait_seconds(.2)

        self.click_cell(start_row, start_column_name)
        self.sapio_driver.wait_seconds(.2)

        # self.sapio_driver.scroll_down(self._get_vertical_scroller(), True)
        self.sapio_driver.scroll_up(self._get_vertical_scroller(), True)
        self.sapio_driver.wait_seconds(.2)

        self.click_cell(end_row, end_column_name, shift=True, scrolled_already=True)

    @property
    def empty(self) -> bool:
        return not self.sapio_driver.exists_in_element(self.body, By.XPATH,
                                                       "./table[1]/tbody[2]/tr[1]", timeout_seconds=.25)

    @property
    def size(self) -> int:
        """
        Get the number of rows in the grid. Requires that the table have the row number column on the far left side.
        """
        # This grid may be for a paged table, meaning the last row number isn't necessarily the size of the current
        # grid.
        return self.last_row_number - self.first_row_number + 1

    @property
    def first_row_number(self) -> int:
        """
        Return the number of the first row in the grid. May not necessarily be 1 if the grid is from a paged table.
        """
        self.scroll_to_top()
        self.sapio_driver.wait_seconds(.2)
        first_row = self.wait_for(lambda d: self.body.find_element(
            By.XPATH, "./table[1]/tbody[2]/tr[1]"
        ))
        first_row_number = int(self.sapio_driver.get_inner_text(first_row.find_element(
            By.XPATH, "./td[1]"
        )))
        return first_row_number

    @property
    def last_row_number(self) -> int:
        """
        Return the number of the last row in the grid.
        """
        self.scroll_to_bottom()
        self.sapio_driver.wait_seconds(.2)
        last_row = self.body.find_element(By.XPATH, "./table[1]/tbody[2]/tr[last()]")
        last_row_number = int(self.sapio_driver.get_inner_text(last_row.find_element(
            By.XPATH, "./td[1]"
        )))
        return last_row_number

    @staticmethod
    def _normalize_header_text(text: str):
        if text.endswith("*"):
            text = text[0: len(text) - 1]
        return text.strip()

    def get_column_header(self, header_text: str) -> Optional[WebElement]:
        header_cells = self.wait_for_many(lambda d: self.header.find_elements(
            By.XPATH, "./table/tbody/tr/td"
        ))
        for header_cell in header_cells:
            text = self._normalize_header_text(self.sapio_driver.get_inner_text(header_cell))
            if header_text.lower() == text.lower():
                return header_cell
        return None

    def _get_vertical_scroller(self) -> WebElement:
        elements = self.wait_for_many(lambda d: self.main_element.find_elements(
            By.CSS_SELECTOR, ".veloxGridScroller"
        ))
        if len(elements) == 1:
            return elements[0]
        return self.wait_for(lambda d: self.main_element.find_element(
            By.CSS_SELECTOR, ".veloxLiveGridLiveScroller"))

    def get_row_by_number(self, index: int) -> (WebElement, ScrollAction):
        """
        Find a row (TR) by number (0-based).
        Requires the table to have a row-numberer column at the far-left.
        This will scroll the grid if it has to.
        """
        in_range: bool = False
        first_row_index: int = -1
        last_scroll_action: ScrollAction = ScrollAction.NONE
        while not in_range:
            first_row = self.wait_for(lambda d: self.body.find_element(
                By.XPATH, "./table[1]/tbody[2]/tr[1]"
            ))
            first_row_index = int(self.sapio_driver.get_inner_text(first_row.find_element(
                By.XPATH, "./td[1]"
            )))
            last_row = self.body.find_element(By.XPATH, "./table[1]/tbody[2]/tr[last()]")
            last_row_index = int(self.sapio_driver.get_inner_text(last_row.find_element(
                By.XPATH, "./td[1]"
            )))
            if index + 1 < first_row_index:
                # Need to scroll up
                if self.sapio_driver.at_max_scroll_top(self._get_vertical_scroller()):
                    break
                self.sapio_driver.scroll_up(self._get_vertical_scroller())
                self.sapio_driver.wait_seconds(.2)
                last_scroll_action = ScrollAction.UP
            elif index + 1 > last_row_index:
                # Need to scroll down
                if self.sapio_driver.at_max_scroll_bottom(self._get_vertical_scroller()):
                    break
                self.sapio_driver.scroll_down(self._get_vertical_scroller())
                self.sapio_driver.wait_seconds(.2)
                last_scroll_action = ScrollAction.DOWN
            else:
                in_range = True

        if in_range:
            n_th = index - first_row_index + 2
            return self.body.find_element(By.XPATH, "./table[1]/tbody[2]/tr[" + str(n_th) + "]"), last_scroll_action
        raise ValueError("Row " + str(index) + " does not exist in the grid.  (Hint: expecting 0-based row numbers)")

    def _scroll_cell_into_view(self, row: int,
                               column_name: str, trigger: bool = False, scrolled_already: bool = False) -> Rectangle:
        """
        Scrolls the specified cell into view and moves the mouse over it (either in the center or over the trigger).
        """
        self.scroll_column_into_view(column_name)

        def waiter(driver: WebDriver):
            col_el = self.get_column_header(column_name)
            row_el, scroll_action = self.get_row_by_number(row)
            # If we did a scroll down or none then we are at risk of not getting the bottom of row element we select.
            if not scrolled_already:
                self.sapio_driver.scroll_into_view(row_el, align_to_top=scroll_action == ScrollAction.UP)
                self.sapio_driver.scroll_into_view(self.main_element, align_to_top=True)
            column_el_rect = Rectangle(col_el.rect)
            column_mid_y = column_el_rect.y + (column_el_rect.height // 2)
            row_el_rect = Rectangle(row_el.rect)
            row_mid_y = row_el_rect.y + (row_el_rect.height // 2)
            x_offset = ((column_el_rect.width // 2) - 5) if trigger else 0
            actions = ActionChains(self.sapio_driver.selenium_driver)
            actions.move_to_element_with_offset(col_el, x_offset, row_mid_y - column_mid_y)
            actions.perform()
            return Rectangle.of(column_el_rect.x, row_el_rect.y, row_el_rect.height,
                                column_el_rect.width)

        return self.sapio_driver.stale_wait().until(waiter)

    @property
    def _horizontal_scroller(self) -> WebElement:
        elements = self.wait_for_many(
            lambda d: self.main_element.find_elements(By.CSS_SELECTOR, ".veloxGridScroller")
        )
        return elements[-1]

    @property
    def _vertical_scroller(self) -> WebElement:
        elements = self.wait_for_many(
            lambda d: self.main_element.find_elements(By.CSS_SELECTOR, ".veloxGridScroller")
        )
        # non-live grids just have one div to scroll both ways
        if len(elements) == 1:
            return elements[0]
        # live grids have two divs, including one that is especially for vertical scrolling
        return self.wait_for(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, ".veloxLiveGridLiveScroller")
        )

    def scroll_column_into_view(self, header_text: str):
        """
        Works under assumption that most automations will work left-to-right
        """
        column_header = self.get_column_header(header_text)
        been_to_max_left: bool = self.sapio_driver.at_max_scroll_left(self._horizontal_scroller)
        while not column_header.is_displayed() and not self.sapio_driver.at_max_scroll_right(self._horizontal_scroller):
            self.sapio_driver.scroll_to_right(self._horizontal_scroller)
        # if it's visible now then we're done
        if column_header.is_displayed():
            return
        # if we haven't been all the way to the left then work back to the left until we find it
        if not been_to_max_left:
            while not column_header.is_displayed() and not self.sapio_driver.at_max_scroll_left(
                    self._horizontal_scroller):
                self.sapio_driver.scroll_to_left(self._horizontal_scroller)
        # it should be done now

    def scroll_to_top(self):
        vertical_scroller = self._vertical_scroller
        while not self.sapio_driver.at_max_scroll_top(vertical_scroller):
            self.sapio_driver.scroll_up(vertical_scroller)

    def scroll_to_bottom(self):
        vertical_scroller = self._vertical_scroller
        while not self.sapio_driver.at_max_scroll_bottom(vertical_scroller):
            self.sapio_driver.scroll_down(vertical_scroller)

    def select_all(self):
        self.body.send_keys(Keys.CONTROL + "a" + Keys.NULL)
        self.sapio_driver.wait_seconds(.25)

    def _get_input_element_after_click(self) -> WebElement:
        """
        Given we have already just clicked the cell, return input or textarea of the element we can enter text.
        The editor will be created in DOM when we have focus by clicking on a editable cell.
        """
        editor_element: WebElement = self.main_element.find_element(By.CSS_SELECTOR, '.velox-grid-editor')
        return editor_element.find_element(By.XPATH, ".//" + self.sapio_driver.x_path_any_tag_of(['input', 'textarea']))


class VeloxForm(BasePageObject):
    _scroller: WebElement
    send_tabs_after_edit: bool
    send_enters_after_edit: bool

    def __init__(self, parent_page: BasePage, main_element: WebElement, scroller: WebElement = None,
                 relative_to_parent: bool = True):
        super().__init__(parent_page, main_element, relative_to_parent)
        self.send_tabs_after_edit = False
        self.send_enters_after_edit = False
        if not scroller:
            scroller = parent_page.main_element
        self._scroller = scroller

    @property
    def scroller(self):
        return self._scroller

    def set_bool_field(self, label: str, value: bool) -> None:
        """
        Set the labeled boolean editor to a value.
        That is, check the value of the current editor state. If it's not equal, click on the editor to flip it.
        This does not handle tri-state editor.
        """
        editor = self._create_relative_editor_supplier(label, By.CSS_SELECTOR, "div > div > div > div")
        current_value = bool(editor.get_attribute("value"))
        if current_value != value:
            editor.click()

    def set_string_field(self, label: str, value: str) -> None:
        """
        Set the value on a labeled string field on this form to some text value.
        Emulates user typing the text value into a text field.
        """
        editor = self._create_string_editor_supplier(label)
        editor.click()
        actions = ActionChains(self.sapio_driver.selenium_driver)
        # ctrl + a select all and delete existing content
        (actions.key_down(Keys.CONTROL).send_keys("a")
         .key_up(Keys.CONTROL).pause(.25).send_keys(Keys.BACKSPACE).perform())
        # then write what we enter
        editor.send_keys(value)
        if self.send_tabs_after_edit:
            editor.send_keys(Keys.TAB)
        if self.send_enters_after_edit:
            editor.send_keys(Keys.ENTER)

    def get_string_value(self, label: str) -> str:
        editor = self._create_string_editor_supplier(label)
        return editor.get_attribute("value")

    def click_action_button(self, label: str):
        try:
            self._create_editor_supplier(label, lambda d: None).click()
        except StaleElementReferenceException as e:
            # try again if not loaded yet.
            self.click_action_button(label)

    def _ensure_ready(self, el: WebElement):
        self.wait.until(lambda d: self.sapio_driver.is_visible_in_viewport(el))

    def _get_root(self) -> WebElement:
        root = self.main_element
        self._ensure_ready(root)
        return root

    def _get_scroller(self) -> WebElement:
        scroller = self.scroller
        self._ensure_ready(scroller)
        return scroller

    def _create_string_editor_supplier(self, label: str):
        root = self._get_root()
        anchor = self.wait_for(lambda d: root.find_element(
            By.XPATH, ".//label" + self.sapio_driver.x_path_ci_text_equals(label)))

        def supplier(driver: WebDriver) -> WebElement:
            # click the input box if exists to create hidden editor if not created yet (picklist)
            if self.sapio_driver.exists_in_element(
                    anchor, By.XPATH,
                    "./following-sibling::*//*" + self.sapio_driver.x_path_contains_class("veloxInputEditor"),
                    timeout_seconds=.25):
                anchor.find_element(By.XPATH, "./following-sibling::*//*" + self.sapio_driver.x_path_contains_class(
                    "veloxInputEditor")).click()
            input_ele = anchor.find_element(By.XPATH, "./following-sibling::*//" +
                                            self.sapio_driver.x_path_any_tag_of(["input", "textarea"]))
            return input_ele

        return self._create_editor_supplier(label, supplier)

    def _create_relative_editor_supplier(self, label: str, editor_by: By, editor_using: str) -> WebElement:
        """
        Creates a By that handles scrolling down and up and down the form looking for the given label and matching
        editor beneath it.
        :param label: The field's label (as it appears on the form, minus the training colon)
        :param editor_by: A locator for the editor.  This must be one of the simpler built-in By instances.
        """
        root = self._get_root()
        anchor = self.wait_for(lambda d: root.find_element(By.XPATH, ".//*[text()=\"" + label + "\"]"))
        locator = locate_with(editor_by, editor_using).near(anchor)

        def supplier(driver: WebDriver) -> WebElement:
            return root.find_element(locator)

        return self._create_editor_supplier(label, supplier)

    def _create_editor_supplier(self, label: str, supplier: Callable[[WebDriver], Optional[WebElement]]) \
            -> Optional[WebElement]:
        root: WebElement = self._get_root()
        scroller: WebElement = self._get_scroller()
        anchor_xpath: str = ".//label" + self.sapio_driver.x_path_ci_text_equals(label)
        for i in range(0, 45):
            self._ensure_ready(root)
            self._ensure_ready(scroller)
            if self.sapio_driver.exists_in_element(root, By.XPATH,
                                                   anchor_xpath, visible_required=True, timeout_seconds=0.1):
                if supplier is None:
                    return root.find_element(By.XPATH, anchor_xpath)
                if self.sapio_driver.exists_by_supplier(supplier, timeout_seconds=.1):
                    return supplier(self.sapio_driver.selenium_driver)

            # handle lazy scrolling
            if i < 15:
                self.sapio_driver.scroll_down(self.scroller, False)
            elif i < 30:
                self.sapio_driver.scroll_up(self.scroller, False)
            else:
                self.sapio_driver.scroll_down(self.scroller, False)
        raise ValueError("The editor was not found: " + label)


class Rectangle:
    """
    Return the dimensions and coordinates of an element
    """
    x: int
    y: int
    height: int
    width: int

    def __init__(self, values: Dict):
        self.x = values.get("x")
        self.y = values.get("y")
        self.height = values.get("height")
        self.width = values.get("width")

    @staticmethod
    def of(x: int, y: int, height: int, width: int) -> Rectangle:
        return Rectangle({
            "x": x,
            "y": y,
            "height": height,
            "width": width
        })


class LoginForm(BasePageObject):
    @property
    def user_name_field(self) -> WebElement:
        return self._load_cached_element("_username_field", By.NAME, "username-field")

    @property
    def password_field(self) -> WebElement:
        return self._load_cached_element("_password_field", By.NAME, "password-field")

    def do_login(self, username: str, password: str) -> None:
        self.user_name_field.send_keys(username)
        self.password_field.send_keys(password + Keys.ENTER)


class LoginWebForm(BasePageObject):
    @property
    def user_name_field(self) -> WebElement:
        return self._load_cached_element("_username_field", By.NAME, "field-email-address")

    @property
    def password_field(self) -> WebElement:
        return self._load_cached_element("_password_field", By.NAME, "field-password")

    @property
    def lab_field(self) -> WebElement:
        return self._load_cached_element("_lab_field", By.NAME, "field-guid")


class Toastr(BasePage):
    """
    Represents the toastr popup in the widgets. Note this may go away on its own and becomes stale very soon.
    """

    def _get_source(self) -> WebElement:
        return self.sapio_driver.selenium_driver.find_element(By.XPATH, TOASTR_XPATH)

    @property
    def message(self) -> str:
        return self.main_element.find_element(By.XPATH, ".//*[@id=\"toast-message\"]").text

    @property
    def title(self) -> str:
        return self.main_element.find_element(By.XPATH, ".//*[@id=\"toast-title\"]").text
