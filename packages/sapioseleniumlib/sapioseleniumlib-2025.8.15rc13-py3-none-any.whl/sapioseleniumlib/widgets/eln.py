from __future__ import annotations

from enum import Enum
from typing import List, Optional

import selenium.webdriver.support.expected_conditions as EC
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from sortedcontainers import SortedDict

from sapioseleniumlib.util.ops import choose_item_from_popup_list, choose_index_from_popup_list
from sapioseleniumlib.widgets import windowobj
from sapioseleniumlib.widgets.pagedef import BasePage
from sapioseleniumlib.widgets.toolbars import ElnToolbar


class ElnEntry(windowobj.BasePageObject):
    """
    This is a single entry inside an Eln page.
    """
    BY_CSS = ".velox-eln-eln-entry"

    @property
    def entry_name(self) -> str:
        entry_element = self.main_element
        if not self.sapio_driver.exists_in_element(entry_element, By.XPATH,
                                                   "./div[1]/div[1]/table[1]/tr[1]/td[2]//td[1]", timeout_seconds=.25):
            # some entries (like Experiment Notes) will not have headers, so return an empty string instead
            return ""
        entry_name = entry_element.find_element(By.XPATH, "./div[1]/div[1]/table[1]/tr[1]/td[2]//td[1]").text
        if not entry_name or not entry_name.strip():
            entry_name = (entry_element.find_element(By.XPATH, "./div[1]/div[1]/table[1]/tr[1]/td[2]//td[2]//input")
                          .get_attribute("value"))
        return entry_name

    @property
    def toolbar(self) -> windowobj.VeloxToolbar:
        ele = self.wait.until(lambda d: self.main_element.find_element(By.CSS_SELECTOR, ".experimentEntryToolbar"))
        return windowobj.VeloxToolbar(self, ele)

    @property
    def submit_button(self) -> windowobj.VeloxButton:
        return self.toolbar.get_button_with_icon("svg-native-check")

    @property
    def is_template(self) -> bool:
        awaiting_activation: bool = bool(self.main_element.find_elements(
            By.CSS_SELECTOR, ".velox-eln-eln-entry-template"
        ))
        awaiting_prerequisites: bool = bool(self.main_element.find_elements(
            By.CSS_SELECTOR, ".elnPrerequisitesContainerMessage"
        ))
        return awaiting_activation or awaiting_prerequisites

    def submit(self) -> None:
        # move the mouse out of the way, otherwise we may get a tooltip covering the button
        self.sapio_driver.move_mouse_to(0, 0)
        # wait a few seconds in case there is a tooltip covering the button
        self.sapio_driver.wait_seconds(3)
        self.click_element(self.submit_button.main_element)
        self.sapio_driver.wait_seconds(.25)

    def activate(self) -> None:
        self.sapio_driver.click(self.wait_for(lambda d: self.main_element.find_element(
            By.CSS_SELECTOR, ".velox-eln-eln-entry-template"
        )))

    def get_form(self) -> windowobj.VeloxForm:
        scroller = self.main_element.find_element(
            By.XPATH, "./ancestor-or-self::*" + self.sapio_driver.x_path_contains_class(
                "verticalScrollingLayoutContainer"))
        ret = windowobj.VeloxForm(self, self.main_element, scroller=scroller)
        ret.send_tabs_after_edit = True
        return ret

    @property
    def form(self) -> windowobj.VeloxForm:
        return self.get_form()


class ElnTableEntry(ElnEntry):
    """
    Table entry within an Elnpage
    """

    @property
    def add_rows_button(self) -> windowobj.VeloxButton:
        return self.toolbar.get_button_with_icon("svg-native-tablerowplusafter")

    @property
    def grid(self) -> windowobj.VeloxGrid:
        self.sapio_driver.scroll_into_view(self.main_element)
        grid_el = self.wait.until(lambda d: self.main_element.find_element(By.CSS_SELECTOR, windowobj.VeloxGrid.BY_CSS))
        grid = windowobj.VeloxGrid(self, grid_el)
        return grid

    def add_row(self, num_rows: int):
        """
        Emulate the user's action of adding specified number of roles into table via OOB button.
        That will work only on unlocked enb type table entries.
        """
        self.add_rows_button.click()
        add_dialog = windowobj.VeloxDialog.get_dialog_with_title_containing("Enter the Number", self.wait)
        input_el = self.wait_for(lambda d: add_dialog.main_element.find_element(By.TAG_NAME, "input"))
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(input_el)
        actions.click()
        actions.send_keys(Keys.BACKSPACE + str(num_rows) + Keys.ENTER)
        actions.perform()

    def fill_column_drop_down_field(self, column: str, rows: int | range | list[int] | None = None,
                                    autofill: bool = False, differing_values: bool = False) -> None:
        """
        Given a column name and rows in the table for a field that displays a dropdown list when clicked,
        select an item in the list for every row. Useful for when the exact values in the dropdown list aren't known.
        :param column: The name of the column to fill.
        :param rows: The rows in the table to fill. Able to be provided as a number of rows from the first row, a range,
            or a list, where the range or list specify the row indices to fill. If not provided, fills every row.
        :param autofill: If true, fill first row, shift click the last row, and use the autofill button to fill the
            entire column within the given range of rows. The autofill button must be visible, otherwise this will fail.
            Currently, the overflow menu is not checked.
        :param differing_values: If true, the item chosen from the dropdown list is different for every row. Requires
            that the dropdown list contain at least as many items as the table has rows. Ignored if autofill is true.
        """
        grid = self.grid
        if rows is None:
            row_range = range(grid.first_row_number - 1, grid.last_row_number)
        elif isinstance(rows, int):
            first_index = grid.first_row_number - 1
            row_range = range(first_index, first_index + rows)
        else:
            row_range = rows

        if autofill:
            if isinstance(row_range, range):
                first_index = row_range.start
                last_index = row_range.stop - row_range.step
            else:
                first_index = row_range[0]
                last_index = row_range[len(row_range) - 1]
            grid.click_cell(first_index, column)
            self.sapio_driver.wait_seconds(.5)
            choose_index_from_popup_list(0, self.sapio_driver)
            self.sapio_driver.wait_seconds(.25)
            grid.click_cell(last_index, column, shift=True)
            self.sapio_driver.wait_seconds(.25)
            self.toolbar.click_auto_fill()
        else:
            for i, row in enumerate(row_range):
                grid.click_cell(row, column)
                self.sapio_driver.wait_seconds(.5)
                choose_index_from_popup_list(i if differing_values else 0, self.sapio_driver)
                self.sapio_driver.wait_seconds(.25)

    def fill_column_input_field(self, value: str, column: str, rows: int | range | list[int] | None = None,
                                autofill: bool = False) -> None:
        """
        Given a column and rows in the table for a field that takes typed input, set each row to the given value.
        :param value: The value to input into each row.
        :param column: The name of the column to fill.
        :param rows: The rows in the table to fill. Able to be provided as a number of rows from the first row, a range,
            or a list, where the range or list specify the row indices to fill. If not provided, fills every row.
        :param autofill: If true, fill first row, shift click the last row, and use the autofill button to fill the
            entire column within the given range of rows. The autofill button must be visible, otherwise this will fail.
            Currently, the overflow menu is not checked.
        """
        grid = self.grid
        if rows is None:
            row_range = range(grid.first_row_number - 1, grid.last_row_number)
        elif isinstance(rows, int):
            first_index = grid.first_row_number - 1
            row_range = range(first_index, first_index + rows)
        else:
            row_range = rows

        if autofill:
            if isinstance(row_range, range):
                first_index = row_range.start
                last_index = row_range.stop - row_range.step
            else:
                first_index = row_range[0]
                last_index = row_range[len(row_range) - 1]
            grid.set_value(first_index, column, value)
            self.sapio_driver.wait_seconds(.25)
            # PR-46800: Ensure that the first row is still selected.
            grid.click_cell(first_index, column)
            grid.click_cell(last_index, column, shift=True)
            self.sapio_driver.wait_seconds(.25)
            self.toolbar.click_auto_fill()
        else:
            for row in row_range:
                grid.set_value(row, column, value)
                self.sapio_driver.wait_seconds(.25)

    def fill_column_from_list(self, values: list[str], column: str, rows: int | range | list[int] | None = None) -> None:
        """
        Given a column and rows in the table for a field that takes typed input, set each row to the value at the
            corresponding index in the list.
        :param values: The values to input into the table. The index of each value in this list corresponds to the index
            of the row in the table it will be placed in.
        :param column: The name of the column to fill.
        :param rows: The rows in the table to fill. Able to be provided as a number of rows from the first row, a range,
            or a list, where the range or list specify the row indices to fill. If not provided, fills as many
            rows as there are values in the provided list.
        """
        grid = self.grid
        if rows is None:
            first_index = grid.first_row_number - 1
            row_range = range(first_index, first_index + len(values))
        elif isinstance(rows, int):
            first_index = grid.first_row_number - 1
            row_range = range(first_index, first_index + rows)
        else:
            row_range = rows
        for row, value in zip(row_range, values, strict=True):
            grid.set_value(row, column, value)
            self.sapio_driver.wait_seconds(.25)


class ElnPage(windowobj.BasePageObject):
    """
    ELN Experiment Page => Tabs => Current Eln Page (You are here) => Entry
    Not to be confused with ELN experiment page.
    """
    BY_CSS = "[data-eln-widgets]"

    @property
    def _scroller(self) -> WebElement:
        return self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH, "./../../.."
        ))

    def scroll_to_top(self):
        self.sapio_driver.selenium_driver.execute_script("arguments[0].scrollTop = 0", self._scroller)

    def scroll_to_bottom(self):
        self.sapio_driver.selenium_driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight",
                                                         self._scroller)

    def _open_entry_menu_at_top(self):
        self.scroll_to_top()
        scroller = self._scroller
        actions = ActionChains(self.sapio_driver.selenium_driver)
        size = scroller.size
        width = size["width"]
        height = size["height"]
        actions.move_to_element_with_offset(scroller, width / -2 + 100, height / -2 + 10)

        actions.click()
        actions.perform()

    def add_entry_to_top(self, menu_item_texts: List[str]):
        self._open_entry_menu_at_top()
        top_most_menu = windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver)
        if not menu_item_texts:
            top_most_menu.click_menu_items(["Notes"])
        else:
            top_most_menu.click_menu_items(menu_item_texts)

    def open_entry_menu_at_bottom(self):
        self.sapio_driver.scroll_to_very_bottom(self.main_element)
        self.sapio_driver.click(self.main_element.find_elements(
            By.XPATH, ".//*" + self.sapio_driver.x_path_ci_contains("Click to Add Entry"))[-1])

    def add_entry_to_bottom(self, menu_item_texts: List[str]):
        self.open_entry_menu_at_bottom()
        top_most_menu = windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver)
        if not menu_item_texts:
            top_most_menu.click_menu_items(["Notes"])
        else:
            top_most_menu.click_menu_items(menu_item_texts)

    @property
    def eln_entry_list(self):
        elements = self.wait_for_many(
            lambda d: self.main_element.find_elements(By.CSS_SELECTOR, ElnEntry.BY_CSS)
        )
        return [ElnEntry(self, e) for e in elements]

    def get_entry_element_with_title(self, title: str) -> Optional[WebElement]:
        self.test_staleness()

        def fun(d: WebDriver) -> Optional[WebElement]:
            eln_entries: List[ElnEntry] = self.eln_entry_list
            for entry in eln_entries:
                try:
                    if entry.entry_name and entry.entry_name.lower() == title.lower():
                        return entry.main_element
                except NoSuchElementException:
                    continue
            return None

        # stale element exception will NOT be ignored here and should be passed up to parent which waiting for this.
        # The parent waiting for this should specify the ignored exceptions.
        return self.wait.until(fun)

    def get_eln_entry_with_title(self, title: str) -> ElnEntry:
        element: WebElement = self.get_entry_element_with_title(title)
        return ElnEntry(self, element)

    def get_eln_table_entry_with_title(self, title: str, timeout_seconds: float | None = None) -> \
            Optional[ElnTableEntry]:

        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds

        def condition(driver: WebDriver):
            entry: ElnEntry = self.get_eln_entry_with_title(title)
            table_entry = ElnTableEntry(entry, entry.main_element)
            if not table_entry.main_element.find_element(By.CSS_SELECTOR, windowobj.VeloxGrid.BY_CSS):
                # Avoid returning masked entry by template name.
                return None
            return table_entry

        return self.sapio_driver.wait(timeout_seconds=timeout_seconds).until(condition)

    def activate_entry(self, title: str) -> None:
        return self.get_eln_entry_with_title(title).activate()

    def submit_entry(self, title: str) -> None:
        return self.get_eln_entry_with_title(title).submit()

    def is_template(self, title: str) -> bool:
        return self.get_eln_entry_with_title(title).is_template

    def wait_unit_entry_ready(self, title: str):
        self.wait.until(lambda d: not self.is_template(title))


class ElnTabPanel(windowobj.VeloxTabPanel):
    BY_CSS = "[data-eln-tab-panel]"

    @property
    def current_eln_page(self) -> ElnPage:
        page_element = self.wait.until(lambda d:
                                       self.active_tab_contents.find_element(By.CSS_SELECTOR, "[data-eln-page]"))
        return ElnPage(self, page_element)

    def add_tab(self, tab_name: str):
        button_panel = self.wait_for(
            lambda d: self.main_element.find_element(By.XPATH, "./div[1]/div[2]"))
        buttons = windowobj.VeloxButton.get_buttons_by_element(button_panel, self.sapio_driver)
        plus_button = next(x for x in buttons if x.is_plus_button)
        plus_button.click()
        self.sapio_driver.wait_seconds(1)
        self.sapio_driver.send_keys(tab_name + Keys.ENTER)
        self.sapio_driver.wait_seconds(1)


class ElnToc(windowobj.BasePageObject):
    BY_CSS = "[data-eln-toc]"

    def click_entry_containing_text(self, text: str) -> None:
        self.sapio_driver.click(self.wait_for(
            lambda d: self.main_element.find_element(By.XPATH, ".//*" + self.sapio_driver.x_path_ci_text_equals(text))
        ))


class NotebookExplorer(BasePage):

    def _get_source(self) -> WebElement:
        return windowobj.VeloxDialog.get_dialog_with_title("Notebook Explorer", self.sapio_driver).main_element

    @property
    def grid_element(self) -> WebElement:
        return self._load_cached_element("_grid_el", By.CSS_SELECTOR, "[data-grid]")

    @property
    def grid(self) -> windowobj.VeloxGrid:
        return windowobj.VeloxGrid(self, self.grid_element)

    @property
    def right_side(self) -> WebElement:
        return self.wait_for(
            lambda d: self.page_source.find_element(By.XPATH, ".//*[@data-dialog-body][1]/div/div[2]"))

    @property
    def main_toolbar(self) -> windowobj.VeloxToolbar:
        return windowobj.VeloxToolbar(self, self.wait.until(
            lambda d: self.right_side.find_element(By.CSS_SELECTOR, windowobj.VeloxToolbar.CSS_CLASS)))

    @property
    def add_experiment_button(self) -> windowobj.VeloxButton:
        return self.main_toolbar.get_button_containing_regex("(?i)add experiment\\+")

    def add_experiment(self) -> None:
        self.add_experiment_button.click()

        prompt_dialog = windowobj.VeloxDialog.get_dialog_with_title_containing("Create", self.sapio_driver)
        prompt_dialog.button_strip_toolbar.get_button_contains_text("Create Default").click()
        self._maybe_select_first_location()

    def _maybe_select_first_location(self) -> None:
        if not windowobj.VeloxDialog.dialog_exists("Select a Location", windowobj.DialogExistsSearchType.STARTS_WITH,
                                                   self.sapio_driver, 2):
            return
        dialog = windowobj.VeloxDialog.get_top_most_dialog(self.sapio_driver)
        self.sapio_driver.click(dialog.body.find_element(By.XPATH, "./div[2]//td/div"))
        dialog.click_bottom_dialog_button("OK")

    def add_experiment_from_template(self, template_display_name: str) -> None:
        self.add_experiment_button.click()
        prompt_dialog = windowobj.VeloxDialog.get_dialog_with_title_containing("Create", self.sapio_driver)
        prompt_dialog.button_strip_toolbar.get_button_contains_text("Create from Template").click()
        from_template_dialog: windowobj.VeloxDialog = windowobj.VeloxDialog.get_dialog_with_title_containing(
            "from Template", self.sapio_driver)
        from_template_dialog.filter(template_display_name)
        self.sapio_driver.wait_seconds(.5)
        # Wait for filter result and then select the row inside the grid
        grid = self.wait_for(lambda d: from_template_dialog.main_element.find_element(
            By.XPATH, ".//*[@data-dialog-body]/div/div[2]"))
        cell = self.wait_for(lambda d: grid.find_element(
            By.XPATH, ".//*" + self.sapio_driver.x_path_ci_text_equals(template_display_name)))
        actions = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(cell).double_click().perform()


class ElnExperimentPage(BasePage):
    EXPERIMENT_XPATH: str = \
        "/html/body/div/table/tbody/tr/td/div/div/div[2]/div[1]/div/div/div/div[3]/div[2]/div[1]/div/div/div"

    def _get_source(self) -> WebElement:
        self.wait.until(EC.url_contains("view=eln"))
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, ElnExperimentPage.EXPERIMENT_XPATH)))

    @property
    def eln_toolbar(self) -> ElnToolbar:
        ele = self.wait_for(lambda d: self.page_source.find_element(
            By.XPATH, "(./div[2]/div/div/table//*" + self.sapio_driver.x_path_contains_class("x-toolbar") +
                      ")[last()]"))
        return ElnToolbar(self, ele)

    @property
    def tab_panel(self) -> ElnTabPanel:
        def pick_tab_panel(d: WebDriver):
            tab_panels = self.page_source.find_elements(By.CSS_SELECTOR, ElnTabPanel.BY_CSS)
            if len(tab_panels) == 0:
                return None
            return tab_panels[-1]

        return ElnTabPanel(self, self.wait_for(pick_tab_panel))

    def select_tab(self, tab_name: str):
        return self.tab_panel.click_tab(tab_name)

    def select_tab_containing(self, tab_text: str):
        return self.tab_panel.click_tab_containing(tab_text)

    def add_tab(self, tab_name: str):
        return self.tab_panel.add_tab(tab_name)

    @property
    def toc(self) -> ElnToc:
        return ElnToc(self, self.wait_for(lambda d: self.page_source.find_element(By.CSS_SELECTOR, ElnToc.BY_CSS)))

    def add_entry_to_top(self, menu_item_text: List[str]):
        return self.tab_panel.current_eln_page.add_entry_to_top(menu_item_text)

    def add_entry_to_bottom(self, menu_item_text: List[str]):
        return self.tab_panel.current_eln_page.add_entry_to_bottom(menu_item_text)

    def get_eln_entry_with_title(self, title: str) -> ElnEntry:
        return (self.sapio_driver.stale_wait()
                .until(lambda d: self.tab_panel.current_eln_page.
                       get_eln_entry_with_title(title)))

    def activate_entry(self, title: str) -> None:
        def wait_fun(driver: WebDriver) -> bool:
            page = self.tab_panel.current_eln_page
            page.activate_entry(title)
            self.sapio_driver.wait_seconds(.25)
            return True

        self.sapio_driver.stale_wait(self.timeout_seconds).until(wait_fun)

    def wait_until_entry_ready(self, title: str) -> None:
        def wait_fun(driver: WebDriver) -> bool:
            self.tab_panel.current_eln_page.wait_unit_entry_ready(title)
            self.sapio_driver.wait_seconds(.25)
            return True

        self.sapio_driver.stale_wait(self.timeout_seconds).until(wait_fun)

    def submit_entry(self, title: str) -> None:
        def wait_fun(driver: WebDriver) -> bool:
            self.tab_panel.current_eln_page.submit_entry(title)
            return True

        self.sapio_driver.stale_wait(self.timeout_seconds).until(wait_fun)

    def get_eln_table_entry_with_title(self, title: str, timeout_seconds: int | None = None) -> ElnTableEntry:

        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds

        return self.sapio_driver.stale_wait(timeout_seconds=timeout_seconds).until(
            lambda d: self.tab_panel.current_eln_page.get_eln_table_entry_with_title(
                title, timeout_seconds=timeout_seconds))


class AliquoterEntry(ElnEntry):

    @staticmethod
    def wrap(entry: ElnEntry) -> AliquoterEntry:
        return AliquoterEntry(entry, entry.main_element)

    def set_plate_name(self, plate_name: str):
        index_type_editor: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/div[2]/" +
                          "div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/div/div//input")
        )
        self.sapio_driver.click(index_type_editor)
        index_type_editor.send_keys(plate_name)

    @property
    def grid(self) -> windowobj.VeloxGrid:
        ele: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH,
                "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div")
        )
        return windowobj.VeloxGrid(self, main_element=ele)

    @property
    def plate_div(self) -> WebElement:
        return self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH,
            "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/" +
            "div/div[1]/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/div/div[2]/div")
                             )

    def get_plate_well(self, row_letter: str, column: int) -> WebElement:
        # get 0-based row and column
        row: int = ord(row_letter.upper()[0]) - ord('A')
        col: int = column - 1

        '''
        all of the .nodeHtmlOverlay divs are plate wells; starts in upper-left corner and goes
        down the column, then wraps back to the top for the next column and continues
        
        we'll need to determine the number of rows first before we can do our calculation, however.
        the wells are absolutely positioned, so count up the wells that line up horizontally with the first well
        and we'll know how many rows there are.
        '''
        well_ele_list: List[WebElement] = self.wait_for_many(
            lambda d: self.plate_div.find_elements(By.CSS_SELECTOR, ".nodeHtmlOverlay")
        )
        first_row_left: str = self.sapio_driver.get_style_property(well_ele_list[0], "left")
        num_rows: int = 0
        for well_ele in well_ele_list:
            if first_row_left == self.sapio_driver.get_style_property(well_ele, "left"):
                num_rows += 1
            else:
                break
        return well_ele_list[(col * num_rows) + row]

    def move_all_to_well(self, row_letter: str, column: int) -> None:
        grid: windowobj.VeloxGrid = self.grid
        row_in_table: WebElement
        row_in_table, ignored = grid.get_row_by_number(0)
        grid.select_all()

        plate_well: WebElement = self.get_plate_well(row_letter, column)
        row_rect = windowobj.Rectangle(row_in_table.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(row_in_table, (row_rect.width // -2) + 5, (row_rect.height // -2) + 5)
        actions.click_and_hold().move_to_element(plate_well).pause(1).release()
        actions.pause(1.5)
        actions.perform()


class SequencingRunMode(Enum):
    HiSeqRapidRun = "HiSeq Rapid Run", True, 2, 1, False, False
    HiSeqHighOutput = "HiSeq High Output", False, 8, 4, False, False
    HiSeqX = "HiSeq X", False, 8, 4, False, False
    MiSeq = "MiSeq", True, 1, 1, True, False
    NextSeq = "NextSeq", True, 4, 1, True, True
    NovaSeqSP = "NovaSeq SP", True, 2, 2, True, False
    NovaSeqS1 = "NovaSeq S1", True, 2, 2, True, False
    NovaSeqS2 = "NovaSeq S2", True, 2, 2, True, False
    NovaSeqS3 = "NovaSeq S3", True, 4, 4, True, False
    NovaSeqS4 = "NovaSeq S4", True, 4, 4, True, False

    display_name: str
    should_auto_assign: bool
    expected_lane_count: int
    num_of_pools: int
    has_on_submit_prompts: False
    has_sample_details_prompt: False

    def __init__(self, display_name: str, should_auto_assign: bool, expected_lane_count: int,
                 num_of_pools: int, has_on_submit_prompts: bool, has_sample_details_prompt: bool):
        self.display_name = display_name
        self.should_auto_assign = should_auto_assign
        self.expected_lane_count = expected_lane_count
        self.num_of_pools = num_of_pools
        self.has_on_submit_prompts = has_on_submit_prompts
        self.has_sample_details_prompt = has_sample_details_prompt


class FlowCellEntry(ElnEntry):
    @staticmethod
    def wrap(entry: ElnEntry) -> FlowCellEntry:
        return FlowCellEntry(entry, entry.main_element)

    def set_flow_cell_id(self, flow_cell_id: str):
        editor = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]//input")
        )
        editor.send_keys(flow_cell_id + Keys.ENTER)

    @property
    def num_of_lanes(self) -> int:
        lane_elements: List[WebElement] = self.wait_for_many(
            lambda d: self.main_element.find_elements(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/" +
                          "div[1]/div[2]/div[1]/div/div")
        )
        return len(lane_elements)

    @property
    def has_assignments(self) -> bool:
        sample_counts: List[WebElement] = self.wait_for_many(
            lambda d: self.main_element.find_elements(
                By.XPATH, ".//*[@class=\"numberOfItemsReadyForWorkflow\"]"
            )
        )
        for sample_count in sample_counts:
            # noinspection PyBroadException
            try:
                count_text: str = sample_count.text
                return int(count_text) > 0
            except Exception as e:
                pass
        return False

    def click_auto_assign(self) -> None:
        ele: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/div")
        )
        toolbar: windowobj.VeloxToolbar = windowobj.VeloxToolbar(self, ele)
        toolbar.get_button_contains_text("Auto Assign Lane Assignments").click()


class FlowCytometryEntry(ElnEntry):
    @staticmethod
    def wrap(entry: ElnEntry) -> FlowCytometryEntry:
        return FlowCytometryEntry(entry, entry.main_element)

    @property
    def west_panel_toolbar(self) -> windowobj.VeloxToolbar:
        def find_button_routine(d: WebDriver) -> Optional[WebElement]:
            button = windowobj.VeloxButton.get_button_with_text("Upload FCS Files", self)
            if not button:
                return None
            return button.main_element

        upload_fcs_files_btn: WebElement = self.wait_for(find_button_routine)
        toolbar_ele = upload_fcs_files_btn.find_element(By.XPATH, "./../..")
        return windowobj.VeloxToolbar(self, toolbar_ele)

    @property
    def east_panel(self) -> windowobj.VeloxPanel:
        ele: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1][@data-panel]"
            )
        )
        return windowobj.VeloxPanel(self, ele)

    @property
    def east_tab_panel(self) -> windowobj.VeloxTabPanel:
        ele: WebElement = self.wait.until(
            lambda d: self.east_panel.main_element.find_element(By.CSS_SELECTOR, windowobj.VeloxTabPanel.CSS_SELECTOR)
        )
        return windowobj.VeloxTabPanel(self, ele)

    @property
    def east_panel_toolbar(self) -> windowobj.VeloxToolbar:
        return windowobj.VeloxToolbar(self, self.east_panel.main_element.find_element(
            By.CSS_SELECTOR, windowobj.VeloxToolbar.CSS_CLASS))

    @property
    def gating_toolbar(self) -> windowobj.VeloxToolbar:
        self.switch_to_gating()
        return windowobj.VeloxToolbar(self, self.wait_for(
            # Find the toolbar among all toolbars that have the text "Draw Gate" on one of its descendant.
            lambda d: self.east_tab_panel.active_tab_contents.find_element(
                By.XPATH, ".//*" + self.sapio_driver.x_path_contains_class("x-toolbar")
                          + "[.//*" + self.sapio_driver.x_path_ci_contains("Draw Gate") + "]")
        ))

    def switch_to_gating(self):
        self._switch_to_tab("Gating")

    def switch_to_histogram(self):
        self._switch_to_tab("Histogram")

    def switch_to_channel_info(self):
        self._switch_to_tab("Channel Info")

    def switch_to_qc_report(self):
        self._switch_to_tab("QC Report")

    def wait_until_gating_loaded(self):
        self.switch_to_gating()

        def wait_routine(d: WebDriver) -> Optional[WebElement]:
            svg_list: List[WebElement] = self.east_tab_panel.active_tab_contents.find_elements(By.TAG_NAME, "svg")
            if svg_list and len(svg_list) > 0:
                return self.main_element
            if "to begin gating" in self.east_tab_panel.active_tab_contents.text.lower():
                return self.main_element
            return None

        self.wait_for(wait_routine)

    @property
    def gating_settings_panel(self) -> windowobj.VeloxPanel:
        self.wait_until_gating_loaded()

        if "Gating Settings" not in self.east_panel.main_element.text:
            self.sapio_driver.click(self.east_tab_panel.active_tab_contents.find_element(
                By.XPATH, "./div[2]/div[1]/div/div/div/div[1]//" + windowobj.VeloxButton.XPATH
            ))
        east_panel_ele: WebElement = self.wait_for(
            lambda d: self.east_tab_panel.active_tab_contents.find_element(
                By.XPATH, "./div[2]/div[1]/div/div/div/div[1]/div[2]"
            )
        )
        return windowobj.VeloxPanel(self, east_panel_ele)

    def set_gating_settings(self, x_channel: Optional[str], y_channel: Optional[str],
                            resolution: Optional[str], normalization: Optional[str]):
        gate_settings_panel: windowobj.VeloxPanel = self.gating_settings_panel
        form: windowobj.VeloxForm = windowobj.VeloxForm(self, gate_settings_panel.main_element)
        form.send_enters_after_edit = True
        if x_channel:
            form.set_string_field("X Channel", x_channel)
        if y_channel:
            form.set_string_field("Y Channel", y_channel)
        if resolution:
            form.set_string_field("Resolution", resolution)
        if normalization:
            form.set_string_field("Normalization", normalization)

    def click_perform_ai_qc(self) -> None:
        def click_button_routine(d: WebDriver) -> bool:
            self.east_panel_toolbar.get_button_contains_text("Perform AI Quality Control").click()
            return True

        self.sapio_driver.stale_wait(self.timeout_seconds,
                                     additional_ignores=[NoSuchElementException]).until(click_button_routine)

    def click_gating_save(self) -> None:
        def click_button_routine(d: WebDriver) -> bool:
            self.gating_toolbar.get_button_contains_text("Save").click()
            return True

        self.switch_to_gating()
        self.sapio_driver.stale_wait(self.timeout_seconds,
                                     additional_ignores=[NoSuchElementException]).until(click_button_routine)

    def click_draw_gate(self) -> None:
        def click_button_routine(d: WebDriver) -> bool:
            self.gating_toolbar.get_button_contains_text("Draw Gate").click()
            return True

        self.switch_to_gating()
        self.sapio_driver.stale_wait(self.timeout_seconds,
                                     additional_ignores=[NoSuchElementException]).until(click_button_routine)

    def click_create_ai_gate(self) -> None:
        def click_button_routine(d: WebDriver) -> bool:
            self.gating_toolbar.get_button_contains_text("Create Auto Gate").click()
            return True

        self.switch_to_gating()
        self.sapio_driver.stale_wait(self.timeout_seconds,
                                     additional_ignores=[NoSuchElementException]).until(click_button_routine)

    @property
    def gating_svg(self) -> WebElement:
        self.switch_to_gating()
        return self.wait_for(
            lambda d: self.east_tab_panel.active_tab_contents.find_element(By.TAG_NAME, "svg")
        )

    def wait_for_qc(self) -> None:
        self.sapio_driver.wait_until_clickable(lambda d: self.east_tab_panel.main_element, stale_wait=True)
        self.switch_to_qc_report()
        self.wait_for(
            lambda d: self.east_tab_panel.active_tab_contents.find_element(By.TAG_NAME, "iframe")
        )
        self.sapio_driver.wait_seconds(5)

    def draw_lower_left_gate(self) -> None:
        gating_svg = self.gating_svg
        gating_svg_rect = windowobj.Rectangle(gating_svg.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(gating_svg).click_and_hold().move_by_offset(
            (gating_svg_rect.width // -2) + 150, (gating_svg_rect.height // 2) - 150
        ).release().perform()

    def click_upload_fcs_files_buttons(self) -> None:
        self.west_panel_toolbar.get_button_contains_text("Upload FCS Files").click()

    def _switch_to_tab(self, tab_name: str):
        def switch_tab_routine(d: WebDriver) -> bool:
            tab_panel = self.east_tab_panel
            if not tab_panel:
                return False
            tab_panel.click_tab(tab_name)
            return True

        wait = WebDriverWait(self.driver, self.sapio_driver.default_timeout,
                             ignored_exceptions=[NoSuchElementException, StaleElementReferenceException, TypeError])
        wait.until(switch_tab_routine)


class IndexerEntry(ElnEntry):
    """
    Index Assignment GUI object.
    """

    @staticmethod
    def wrap(entry: ElnEntry) -> IndexerEntry:
        return IndexerEntry(entry, entry.main_element)

    def set_index_type(self, index_type: str) -> None:
        index_type_editor: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[1]//input")
        )
        self.sapio_driver.click(index_type_editor)
        choose_item_from_popup_list(index_type, self.sapio_driver)

    @property
    def grid(self) -> windowobj.VeloxGrid:
        return windowobj.VeloxGrid(self, main_element=self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[2]/" +
                          "div/div[1]/div[2]/div[1]/div/div[2]/div"
            )
        ))

    @property
    def plate_div(self) -> WebElement:
        return self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div")
        )

    def move_all_to_well(self, row_letter: str, column: int) -> None:
        grid = self.grid
        row_in_table: WebElement
        # The row in table for first one is hidden on left with no width. So we look at 2nd table. special case.
        selector = self.wait_for(lambda d: grid.body.find_element(By.XPATH, "./table[2]/tbody[2]/tr[1]/td[1]"))
        grid.select_all()

        plate_well: WebElement = self._get_plate_well(row_letter, column)

        # drag from row 1 to the plate well
        body_parent = grid.body.find_element(By.XPATH, "./..")
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element(selector)
        actions.click_and_hold().move_to_element(plate_well).pause(1).release()
        actions.pause(1.5).perform()

    def _get_plate_well(self, row_letter: str, column: int):
        # get 0-based row and column
        row: int = ord(row_letter.upper()[0]) - ord('A')
        col: int = column - 1

        well_ele_list: List[WebElement] = self.wait_for_many(
            lambda d: self.plate_div.find_elements(By.CSS_SELECTOR, ".nodeHtmlOverlay")
        )
        first_row_left: str = self.sapio_driver.get_style_property(well_ele_list[0], "left")
        num_rows: int = 0
        for well_ele in well_ele_list:
            if first_row_left == self.sapio_driver.get_style_property(well_ele, "left"):
                num_rows += 1
            else:
                break
        return well_ele_list[(col * num_rows) + row]


class Plater3DFillByMethod(Enum):
    FILL_BY_COLUMN_SE = "Fill by Column (SE)"
    FILL_BY_COLUMN_NE = "Fill by Column (NE)"
    FILL_BY_COLUMN_SW = "Fill by Column (SW)"
    FILL_BY_COLUMN_NW = "Fill by Column (NW)"
    FILL_BY_ROW_SE = "Fill by Row (SE)"
    FILL_BY_ROW_NE = "Fill by Row (NE)"
    FILL_BY_ROW_SW = "Fill by Row (SW)"
    FILL_BY_ROW_NW = "Fill by Row (NW)"

    label: str

    def __init__(self, label: str):
        self.label = label


class Plater3DEntry(ElnEntry):
    @staticmethod
    def wrap(entry: ElnEntry) -> Plater3DEntry:
        return Plater3DEntry(entry, entry.main_element)

    @property
    def grid(self) -> windowobj.VeloxGrid:
        return windowobj.VeloxGrid(self, main_element=self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, ".//div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div[2]/div[1]/" +
                          "div/div[2]/div")
        ))

    @property
    def plate_div(self) -> WebElement:
        return self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, ".//div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/" +
                          "div/div/div/table/tbody/tr[2]/td[2]/div/div/div")
        )

    def _get_plate_well(self, row_letter: str, column: int):
        row: int = (ord(row_letter.upper()[0]) - ord('A')) + 1
        return self.wait_for(
            lambda d: self.plate_div.find_element(By.XPATH, "./div[" + str(row) + "]/div[" + str(column) + "]")
        )

    def move_all_to_well(self, row_letter: str, column: int, fill_by_method: Plater3DFillByMethod,
                         replicates: int = 1) -> None:
        grid: windowobj.VeloxGrid = self.grid
        row_in_table: WebElement
        row_in_table, ignored = grid.get_row_by_number(0)
        grid.select_all()

        plate_well = self._get_plate_well(row_letter, column)
        self.sapio_driver.scroll_into_view(self.main_element)
        row_rect = windowobj.Rectangle(row_in_table.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(row_in_table, (row_rect.width // -2) + 15, (row_rect.height // -2) + 15)
        actions.click_and_hold()
        actions.move_to_element(plate_well).pause(1).release()
        actions.pause(1.5)
        actions.perform()

        edit_well_assignment_settings_dialog: Optional[windowobj.VeloxDialog] = (
            windowobj.VeloxDialog.get_dialog_with_title_if_exists("Edit Well Assignment Settings",
                                                                  self.sapio_driver))
        if not edit_well_assignment_settings_dialog:
            return
        if fill_by_method is not None:
            fill_by_label: WebElement = self.wait_for(
                lambda d: edit_well_assignment_settings_dialog.body.find_element(
                    By.XPATH, ".//label" + self.sapio_driver.x_path_ci_text_equals(fill_by_method.label)
                )
            )
            self.sapio_driver.wait_until_clickable(lambda d: fill_by_label, self.timeout_seconds)
            actions = ActionChains(self.sapio_driver.selenium_driver)
            actions.move_to_element_with_offset(fill_by_label, 0, -50).click().perform()
        # now set the replicates to the desired value
        if replicates is not None:
            edit_well_assignment_settings_dialog.get_form().set_string_field(
                "Number of Aliquots/Derivatives to Create Per Input Sample", str(replicates))
        edit_well_assignment_settings_dialog.click_bottom_dialog_button("OK")

        self.sapio_driver.scroll_into_view(self.main_element)


class PoolingEntry(ElnEntry):
    @staticmethod
    def wrap(entry: ElnEntry) -> PoolingEntry:
        return PoolingEntry(entry, entry.main_element)

    @property
    def tubes(self) -> List[WebElement]:
        tube_ele_list: List[WebElement] = self.wait_for_many(
            lambda d: self.main_element.find_elements(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div[2]/div[2]/" +
                          "div[1]/div/div[2]/div/div[contains(@class,\"nodeHtmlOverlay\")]")
        )
        #  will sort by top position and then by left position
        sort_tree: SortedDict[int, SortedDict[int, WebElement]] = SortedDict()
        for tube_ele in tube_ele_list:
            top_string: str = self.sapio_driver.get_style_property(tube_ele, "top")
            top: int = int(top_string.lower().removesuffix("px"))
            left_string = self.sapio_driver.get_style_property(tube_ele, "left")
            left: int = int(left_string.lower().removesuffix("px"))

            if top not in sort_tree:
                inner_map = SortedDict()
                sort_tree[top] = inner_map
            inner_map = sort_tree[top]
            inner_map[left] = tube_ele

        # traverse the maps and build out the overall list
        ret: List[WebElement] = []
        for top, inner in sort_tree.items():
            for left, tube in inner.items():
                ret.append(tube)
        return ret

    def move_all_tube(self, tube_number: int) -> None:
        """
        Moves all samples to the specified tube.
        :param tube_number: index of the tube, 0-based
        """
        grid: windowobj.VeloxGrid = self.grid
        grid.select_all()

        tube = self.tubes[tube_number]

        body_parent: WebElement = grid.body.find_element(By.XPATH, "./..")
        rect: windowobj.Rectangle = windowobj.Rectangle(body_parent.rect)
        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(body_parent, (rect.width // -2) + 5, (rect.height // -2) + 5)
        actions.click_and_hold().move_to_element(tube).pause(1).release()
        actions.pause(1.5).perform()

    def move_to_tube(self, start_row: int, end_row: int, tube_number: int) -> None:
        """
        Moves the samples in the specified range to the specified tube.
        :param start_row: The first row of the selection (0-based).
        :param end_row: The last row of the selection (0-based).
        :param tube_number: The index of the destination tube (0-based).
        """
        self.sapio_driver.scroll_into_view(self.main_element)
        grid: windowobj.VeloxGrid = self.grid
        grid.select(start_row, "Index Tag", end_row, "Index Tag")
        tube: WebElement = self.tubes[tube_number]
        """
        // the moveToElement action will scroll the given element into view and anchor it to the bottom of the
        // view port.  This means it will scroll the experiment so that the well is at the bottom of the view, thus
        // making the entry be halfway off of the screen.  While this will work with some unusual-looking activity,
        // we will instead calculate where the center of the drop target's rectangle is relative to the source and
        // move the cursor that way instead.
        """
        row_rect: windowobj.Rectangle = self.sapio_driver.stale_wait().until(
            lambda d: windowobj.Rectangle(self.grid.get_row_by_number(end_row)[0].rect)
        )
        entry: WebElement = self.main_element
        entry_rect: windowobj.Rectangle = windowobj.Rectangle(entry.rect)
        tube_rect: windowobj.Rectangle = windowobj.Rectangle(tube.rect)

        entry_center_x: int = entry_rect.x + (entry_rect.width // 2)
        entry_center_y: int = entry_rect.y + (entry_rect.height // 2)

        row_center_x: int = row_rect.x + (row_rect.width // 2)
        row_center_y: int = row_rect.y + (row_rect.height // 2)

        tube_center_x: int = tube_rect.x + (tube_rect.width // 2)
        tube_center_y: int = tube_rect.y + (tube_rect.height // 2)

        row_offset_x: int = row_rect.width // -2 + 5
        row_offset_y: int = row_rect.height // -2 + 5

        entry_to_row_x: int = row_center_x - entry_center_x
        entry_to_row_y: int = row_center_y - entry_center_y

        entry_to_tube_x: int = tube_center_x - entry_center_x
        entry_to_tube_y: int = tube_center_y - entry_center_y

        actions: ActionChains = ActionChains(self.sapio_driver.selenium_driver)
        actions.move_to_element_with_offset(entry, entry_to_row_x + row_offset_x, entry_to_row_y + row_offset_y)
        actions.click_and_hold().pause(1)
        actions.move_to_element_with_offset(entry, entry_to_tube_x, entry_to_tube_y).pause(3).release()
        actions.pause(1)
        actions.perform()

        self.sapio_driver.scroll_into_view(self.main_element)

    @property
    def grid(self) -> windowobj.VeloxGrid:
        element = self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div"
        ))
        return windowobj.VeloxGrid(self, main_element=element)

    def _click_actions_button(self) -> None:
        self.sapio_driver.click(self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div[2]/" +
                          "div[2]/div[1]/div/div[1]/div/div/div[1]"
            )
        ))

    def set_number_of_tubes(self, num_of_tubes: int):
        self._click_actions_button()
        windowobj.VeloxMenu.get_top_most_menu(self.sapio_driver).click_menu_items(["Set # of Tubes"])
        dialog: windowobj.VeloxDialog = windowobj.VeloxDialog.get_dialog_with_title(
            "Set # of Tubes", self.sapio_driver)
        editor: WebElement = self.wait_for(
            lambda d: dialog.main_element.find_element(By.XPATH, ".//input")
        )
        editor.send_keys(str(num_of_tubes))
        dialog.click_bottom_dialog_button("OK")
        self.sapio_driver.wait_seconds(.25)


class RequestedServicesEntry(ElnEntry):
    @staticmethod
    def wrap(entry: ElnEntry) -> RequestedServicesEntry:
        return RequestedServicesEntry(entry, entry.main_element)

    @property
    def grid(self) -> windowobj.VeloxGrid:
        ele: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(
                By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[2]/div")
        )
        return windowobj.VeloxGrid(self, ele)

    def set_services_requested(self, row: int, service_name: str) -> None:
        """
        Sets the requested service for the given row to the given service.
        :param row: Row in the grid -- 0-based.
        :param service_name: name of the service, should match the Process Name shown in the dialog
        """
        self.grid.click_cell_trigger(row, "Services Requested")
        dialog: windowobj.VeloxDialog = windowobj.VeloxDialog.get_dialog_with_title(
            "Select Assigned Process Destination(s)", self.sapio_driver)
        dialog.double_click_text(service_name)
        self.sapio_driver.scroll_into_view(self.main_element)

    def auto_fill(self, start_row: int, end_row: int):
        self.grid.select(start_row, "Services Requested", end_row, "Services Requested")
        self.sapio_driver.click(self.main_element.find_element(
            By.XPATH, "./div[2]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/div/div")
        )
