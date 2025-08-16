from typing import Optional, List, Callable

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from sapioseleniumlib.util.driver import SapioVersion
from sapioseleniumlib.util.ops import choose_item_from_popup_list
from sapioseleniumlib.widgets import toolbars
from sapioseleniumlib.widgets import windowobj
from sapioseleniumlib.widgets.pagedef import BasePageObject


class VeloxWestPanel(BasePageObject):
    """
    The west panel of the main GUI.  Contains user menu, quick search box, main menu, data tree, and workflows.
    """
    BY_CSS = "[data-main-west-panel]"

    @property
    def quick_access_toolbar(self) -> toolbars.QuickAccessToolbar:
        self.expand()
        element: WebElement = self.wait_for_many(lambda d: self.main_element.find_elements(
            By.CSS_SELECTOR, windowobj.VeloxToolbar.CSS_CLASS))[1]
        return toolbars.QuickAccessToolbar(self, element)

    def is_collapsed(self) -> bool:
        ele_id = self.main_element.get_attribute("id")
        return not ele_id or "primaryWestPanel".lower() != ele_id.lower()

    def expand(self):
        if not self.is_collapsed():
            return
        parent: WebElement = self.wait.until(EC.visibility_of(self.main_element.find_element(By.XPATH, "./..")))
        self.sapio_driver.click(self.wait_for(lambda d: self.main_element.find_element(
            By.XPATH, windowobj.VeloxButton.XPATH)))
        self.rebase(self.wait.until(lambda d: parent.find_element(By.CSS_SELECTOR, self.BY_CSS)))

    def collapse(self):
        if self.is_collapsed():
            return
        buttons = self.quick_access_toolbar.buttons
        return buttons[-1].click()

    @property
    def tab_panel(self):
        element = self.wait.until(lambda d: self.main_element.find_element(
            By.XPATH, "./div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]"
        ))
        return windowobj.VeloxTabPanel(self, main_element=element)

    @property
    def notebook_explorer_menu_item(self):
        return self.get_menu_item("notebook explorer")

    def _ensure_menu_tab(self):
        tab_el = self.tab_panel.get_tab_containing_text("menu")
        if tab_el.is_displayed():
            self.sapio_driver.click(tab_el)
        elif len(self.tab_panel.tab_list) != 1:
            raise ValueError("Could not find menu tab because too menu tabs contains the text 'menu'.")

    @property
    def menu(self) -> Optional[windowobj.VeloxMenu]:
        self._ensure_menu_tab()
        return windowobj.VeloxMenu(self, self.wait.until(lambda d: self.tab_panel.active_tab_contents.find_element(
            By.XPATH, ".//" + windowobj.VeloxMenu.X_PATH)))

    def get_menu_item(self, text: str) -> Optional[windowobj.VeloxMenuItem]:
        return self.menu.get_menu_item_containing_text(text)

    def click_menu_items(self, text: List[str]):
        return self.menu.click_menu_items(text)


class ListView(BasePageObject):
    CSS_SELECTOR: str = "[data-list]"

    def select_item(self, item_text: str) -> None:
        # TODO scrolling
        elements = self.wait_for_many(lambda d: self.main_element.find_elements(By.XPATH, "./div"))
        for element in elements:
            if element.text.lower() == item_text.lower():
                element.click()


class IdvWestPanel(windowobj.VeloxPanel):
    @property
    def has_key_field_editors(self) -> bool:
        if self.sapio_driver.exists_by_supplier(self._get_possible_form_panel_supplier()):
            possible_form_panel = windowobj.VeloxPanel(self,
                                                       self.wait_for(self._get_possible_form_panel_supplier()))
            return not possible_form_panel.header.is_displayed()
        return False

    @property
    def key_fields_form(self) -> Optional[windowobj.VeloxForm]:
        if not self.has_key_field_editors:
            return None
        return windowobj.VeloxPanel(self, self.wait_for(self._get_possible_form_panel_supplier())).form

    @property
    def has_linked_records_panel(self):
        return self._linked_records_panel is not None

    def expand_linked_records_panel(self) -> None:
        if not self.has_linked_records_panel:
            return
        panel: windowobj.VeloxPanel = self._linked_records_panel
        if panel.body.is_displayed():
            # already expanded the panel.
            return
        # if not expanded click the header of the panel to expand it.
        self.sapio_driver.click(panel.header)

    def collapse_linked_records_panel(self) -> None:
        if not self.has_linked_records_panel:
            return
        panel = windowobj.VeloxPanel(self, self.wait_for(self._get_possible_linked_records_supplier()))
        if not panel.body.is_displayed():
            # already collapsed.
            return
        self.sapio_driver.click(panel.header)

    def get_linked_records_editor_element(self, data_type_display_name: str) -> Optional[WebElement]:
        matching_editor_panel = self._get_panel_for_linked_records_editor(data_type_display_name)
        if matching_editor_panel is None:
            return None
        return matching_editor_panel.body.find_element(By.XPATH, "./div/div")

    @property
    def add_link_button(self) -> Optional[windowobj.VeloxButton]:
        if not self.has_linked_records_panel:
            return None
        linked_records_panel = self._linked_records_panel
        if not linked_records_panel:
            return None
        buttons = windowobj.VeloxButton.get_buttons_by_element(linked_records_panel.header, self.sapio_driver)
        for button in buttons:
            if button.is_plus_button:
                return button
        return None

    @property
    def can_add_linked_record(self) -> bool:
        return self.add_link_button is not None

    def click_add_link_record(self) -> None:
        add_link_button = self.add_link_button
        if add_link_button is None:
            return
        add_link_button.click()

    def _get_add_link_button(self, data_type_display_name: str) -> Optional[windowobj.VeloxButton]:
        if not self.has_linked_records_panel:
            return None
        panel_for_linked_record_editor = self._get_panel_for_linked_records_editor(data_type_display_name)
        if panel_for_linked_record_editor is None:
            return None
        buttons = windowobj.VeloxButton.get_buttons_by_element(panel_for_linked_record_editor.header, self.sapio_driver)
        for button in buttons:
            if button.is_plus_button:
                return button
        return None

    def can_add_linked_record_of_type(self, data_type_display_name: str) -> bool:
        return self._get_add_link_button(data_type_display_name) is not None

    def click_add_linked_record_of_type(self, data_type_display_name: str) -> None:
        add_link_button = self._get_add_link_button(data_type_display_name)
        if add_link_button is None:
            return
        add_link_button.click()

    def _get_panel_for_linked_records_editor(self, data_type_display_name: str) -> Optional[windowobj.VeloxPanel]:
        if not self.has_linked_records_panel:
            return None
        self.expand_linked_records_panel()
        panel = windowobj.VeloxPanel(self, self.wait_for(self._get_possible_linked_records_supplier()))
        panel_divs = self.wait_for_many(
            lambda d: panel.body.find_elements(By.XPATH, "./div/div/div")
        )
        matching_editor_panel: Optional[windowobj.VeloxPanel] = None
        data_type_display_name = self.sapio_driver.normalize_text(data_type_display_name)
        for panel_div in panel_divs:
            editor_panel = windowobj.VeloxPanel(self, main_element=panel_div)
            if editor_panel.header_text_normalized.lower() == data_type_display_name.lower():
                matching_editor_panel = editor_panel
                break
        return matching_editor_panel

    @property
    def _linked_records_panel(self) -> Optional[windowobj.VeloxPanel]:
        method: Callable[[WebDriver], Optional[WebElement]] = self._get_possible_linked_records_supplier()
        if self.sapio_driver.exists_by_supplier(method):
            panel = windowobj.VeloxPanel(self, self.wait_for(self._get_possible_linked_records_supplier()))
            if panel.header.is_displayed() and panel.header_text_normalized and \
                    panel.header_text_normalized.lower() == "Linked Records".lower():
                return panel
        return None

    def _get_possible_linked_records_supplier(self) -> Callable[[WebDriver], Optional[WebElement]]:
        def fun(driver: WebDriver) -> Optional[WebElement]:
            elements = self.body.find_elements(By.XPATH, "./div/div/div")
            if not elements:
                return None
            return elements[-1]

        return fun

    def _get_possible_form_panel_supplier(self) -> Callable[[WebDriver], Optional[WebElement]]:
        def fun(driver: WebDriver) -> Optional[WebElement]:
            return self.body.find_element(By.XPATH, "./div/div/div[1]")

        return fun


class IntegratedDataView(BasePageObject):
    BY_CSS_SELECTOR: str = "[data-datarecord-view]"
    _hasWestPanel: bool

    @property
    def has_west_panel(self) -> bool:
        if hasattr(self, "_hasWestPanel"):
            return self._hasWestPanel
        self._hasWestPanel = self.sapio_driver.exists_by_supplier(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, "[data-west-panel]"), 1)
        return self._hasWestPanel

    @property
    def data_type(self) -> str:
        return str(self.main_element.get_attribute("data-datatype"))

    @property
    def center_panel(self) -> windowobj.VeloxPanel:
        return windowobj.VeloxPanel(self, self.wait_for(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, "[data-center-panel]")))

    @property
    def tab_panel(self) -> windowobj.VeloxTabPanel:
        return windowobj.VeloxTabPanel(self, self.wait_for(
            lambda d: self.center_panel.main_element.find_element(By.XPATH, "./div[last()]").
            find_element(By.CSS_SELECTOR, windowobj.VeloxTabPanel.CSS_SELECTOR)
        ))

    @property
    def active_panel(self) -> windowobj.VeloxPanel:
        return windowobj.VeloxPanel(self, self.wait_for(
            lambda d: self.tab_panel.active_tab_contents
        ))

    @property
    def west_panel(self) -> Optional[IdvWestPanel]:
        if not self.has_west_panel:
            return None
        return IdvWestPanel(self, self.wait_for(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, "[data-west-panel]")))

    def get_component_with_title(self, title: str) -> Optional[windowobj.VeloxPanel]:
        return self.active_panel.get_component_with_title(title)


class ProcessQueue(BasePageObject):
    @property
    def container(self) -> WebElement:
        return self.wait_for(
            lambda d: self.main_element.find_element(By.XPATH, "./div[2]/div[1]/div/div")
        )

    @property
    def header(self) -> WebElement:
        return self.wait_for(
            lambda d: self.container.find_element(By.XPATH, "./div/div/div/div[1]")
        )

    def click_queued_button(self) -> None:
        self.sapio_driver.highlight(self.main_element)
        self.click_element(self.wait_for(
            lambda d: self.header.find_element(By.XPATH, ".//div[text()=\"Queued\"]")
        ))

    def click_in_process_button(self) -> None:
        self.click_element(self.wait_for(
            lambda d: self.header.find_element(By.XPATH, ".//div[text()=\"In Process\"]")
        ))

    @property
    def body(self) -> WebElement:
        return self.wait_for(
            lambda d: self.container.find_element(By.XPATH, "./div/div/div/div[2]")
        )

    @property
    def processes(self) -> List[WebElement]:
        ret: List[WebElement] = self.wait_for_many(
            lambda d: self.body.find_elements(By.XPATH, ".//*[@data-processclientid]")
        )
        return ret

    @property
    def step_panel(self) -> WebElement:
        return self.wait_for(
            lambda d: self.body.find_element(By.XPATH, "./div[1]/div/div/div/div/div/div[3]")
        )

    @property
    def step_panel_header(self) -> WebElement:
        maybe_header = self.wait_for(lambda d: self.step_panel.find_element(By.XPATH, "./div/div[1]"))
        # if the process queue is using a page limit, there may be an extra div holding a message
        if "exceeds the queue" in maybe_header.text.lower():
            return self.step_panel.find_element(By.XPATH, "./div/div[2]")
        return maybe_header

    @property
    def step_panel_body(self) -> WebElement:
        return self.step_panel.find_element(By.XPATH, "./div/div[2]")

    @property
    def in_process_grid(self) -> windowobj.VeloxGrid:
        element = self.step_panel_body.find_element(By.XPATH, "./div/div/div[1]/div/div[2]/div[1]/div/div/div")
        return windowobj.VeloxGrid(self, main_element=element)

    def start_process_step(self, process_name: str, step_id: str | int, scan_values: list[str],
                           scan_type: str | None = None, scan_field: str | None = None,
                           wait_for_eln_load: bool = True) -> None:
        """
        Start a process at a specific step, scanning any provided values before starting.
        :param process_name: The name of the process to open.
        :param step_id: An identifier for the step to open. This is either a string representing the step name or an
            integer for the step number.
        :param scan_values: The values to scan before starting the process step.
        :param scan_type: The type of item being scanned, either None, "Samples", or "Plates". If None, then
            whatever mode the queue was already in is used. If "Samples", then the sample button is clicked. If
            "Plates", then the plate button is clicked. The "Samples" and "Plates" buttons must be visible in order
            for them to be clicked.
        :param scan_field: The field to scan against. If None, leaves the scan field at its current value.
        :param wait_for_eln_load: If true, this function waits until the user has entered the ELN page before
            proceeding. Cases where one might want this to be false include experiments where a popup appears upon
            clicking "Start Workflow" but before the user is actually sent to the ELN page.
        """
        self.click_queued_button()

        if isinstance(step_id, str):
            self.click_process_step(process_name, step_id)
        else:
            self.click_process_step_by_number(process_name, step_id)

        if scan_type and scan_type.lower() == "samples":
            self.click_sample_buttons()
        elif scan_type and scan_type.lower() == "plates":
            self.click_plates_button()
        elif scan_type is not None:
            raise Exception(f'Unknown scan type {scan_type}. Scan type should be either None, "samples", or "plates".')

        if scan_field is not None:
            self.change_scan_field(scan_field)

        self.scan_values(scan_values)

        self.click_start_workflow_button()

        if wait_for_eln_load is True:
            self.wait.until(EC.url_contains("view=eln"))

    def click_process_step(self, process_name: str, step_name: str) -> None:
        self.click_process(process_name)

        self.sapio_driver.wait_seconds(.5)
        # click the step.
        self.click_element(self.wait_for(
            lambda d: self.body.find_element(By.XPATH, self._process_x_path(process_name)
                                             + "/" + self._process_step_x_path(step_name))
        ))

    def click_process_step_by_number(self, process_name: str, step_number: int) -> None:
        self.click_process(process_name)

        self.sapio_driver.wait_seconds(.5)
        # click the step.
        self.click_element(self.wait_for(
            lambda d: self.body.find_element(By.XPATH, self._process_x_path(process_name)
                                             + "/" + self._process_step_xpath(step_number))
        ))

    def click_process(self, process_name):
        self.sapio_driver.highlight(self.body, False)
        # click the process (assuming it's not expanded) TODO handle already expanded case
        process_ele = self.sapio_driver.wait_until_element_visible(
            self.body, By.XPATH, self._process_x_path(process_name), self.timeout_seconds)
        self.sapio_driver.highlight(process_ele, False)

        # go up two divs to the div that contains this and any workflow steps and look for the workflow steps.
        wf_elements = process_ele.find_elements(By.XPATH, '../..//*[@data-wfindex]')

        # if there are no workflow steps, then this is collapsed and needs to be clicked.
        if len(wf_elements) == 0:
            self.sapio_driver.click(process_ele)

    def scan_values(self, values: List[str]) -> bool:
        # wait until clickable, don't simply wait (PR-47158)
        scanner: WebElement = self.sapio_driver.wait_until_clickable(
            lambda d: self.step_panel_header.find_element(By.XPATH, ".//textarea")
        )
        for value in values:
            scanner.send_keys(value + Keys.ENTER)
        self.sapio_driver.wait_seconds(.5)
        return True

    def change_scan_field(self, field: str) -> None:
        scanner_dropdown: WebElement = self.wait.until(
            lambda d: self.step_panel_header.find_element(By.XPATH, ".//textarea/ancestor::tr/td[2]")
        )
        self.sapio_driver.click(scanner_dropdown)
        self.sapio_driver.wait_seconds(.5)
        choose_item_from_popup_list(field, self.sapio_driver)
        self.sapio_driver.wait_seconds(.5)

    def click_sample_buttons(self) -> None:
        self.sapio_driver.click(
            self.step_panel_header.find_element(
                By.XPATH, ".//div" + self.sapio_driver.x_path_ci_text_equals("Samples")
            ))

    def click_plates_button(self, timeout_seconds: Optional[float] = None) -> None:
        self.sapio_driver.find_and_click(lambda d: self.step_panel_header.find_element(
            By.XPATH, ".//div" + self.sapio_driver.x_path_ci_text_equals("Plates")), timeout_seconds=timeout_seconds)

    def click_start_workflow_button(self) -> None:
        self.sapio_driver.click(self.step_panel_header.find_element(
            By.XPATH, "./div/div/div[.//div" + self.sapio_driver.x_path_ci_text_equals("Start Workflow") + "]"
        ))

    def _process_x_path(self, process_name: str) -> str:
        if self.sapio_driver.target_sapio_version == SapioVersion.V23_12:
            return ".//*[@data-processrecordid]//*" + self.sapio_driver.x_path_ci_text_equals(process_name)
        return ".//*[@data-processclientid]//*" + self.sapio_driver.x_path_ci_text_equals(process_name)

    def _process_step_x_path(self, step_name: str) -> str:
        return "../following-sibling::div/div/div[2]" + self.sapio_driver.x_path_ci_text_equals(step_name)

    def _process_step_xpath(self, step_number: int) -> str:
        return "../following-sibling::div/div/div[1]" + self.sapio_driver.x_path_ci_text_equals(str(step_number) + ".")


class RequestsAwaitingApproval(BasePageObject):
    def approve_request(self, request_id: str):
        self.sapio_driver.wait_seconds(.5)
        filter_element: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(By.TAG_NAME, "input")
        )
        filter_element.send_keys(request_id)
        self.sapio_driver.wait_seconds(.5)

        requests_grid_element: WebElement = self.wait_for(
            lambda d: self.main_element.find_element(By.CSS_SELECTOR, windowobj.VeloxGrid.BY_CSS)
        )
        requests_grid: windowobj.VeloxGrid = windowobj.VeloxGrid(self, main_element=requests_grid_element)
        self.sapio_driver.wait_seconds(1)
        if requests_grid.empty:
            # not matching request id because it's blank.
            return

        requests_grid.double_click_row_number(0)
        request_dialog = windowobj.VeloxDialog.get_dialog_with_title("View / Edit Request", self.sapio_driver)
        click_attempts_left = 5
        while click_attempts_left > 0:
            try:
                request_dialog.click_button_with_text("Approve Request")
                break
            except IndexError:
                # plugin toolbar buttons probably still loading, so wait and try again (within reason)
                click_attempts_left -= 1
                self.sapio_driver.wait_seconds(0.5)
        self.sapio_driver.wait_seconds(1)
        request_dialog.click_bottom_dialog_button("OK")
