import datetime
import logging
import pathlib
import time
from importlib import resources
from pathlib import Path
from typing import Optional, List, Union

from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from sapioseleniumlib.util.driver import SapioVersion
from sapioseleniumlib.util.script import VeloxSeleniumScript
from sapioseleniumlib.widgets import dialogs
from sapioseleniumlib.widgets import windowobj
from sapioseleniumlib.widgets.dialogs import StorageDialog
from sapioseleniumlib.widgets.eln import ElnEntry, SequencingRunMode, FlowCellEntry, IndexerEntry, Plater3DFillByMethod, \
    Plater3DEntry, \
    PoolingEntry, RequestedServicesEntry
from sapioseleniumlib.widgets.eln import ElnExperimentPage as ElnExperiment, ElnTableEntry
from sapioseleniumlib.widgets.pages import MainPage
from sapioseleniumlib.widgets.panels import ProcessQueue, RequestsAwaitingApproval
from sapioseleniumlib.widgets.windowobj import DialogExistsSearchType, VeloxButton, VeloxTabPanel, VeloxPanel, \
    VeloxToolbar, VeloxGrid, VeloxDialog, VeloxForm
from sapioseleniumlib.widgets.windowobj import VeloxDialog as Dialog


class TruSeqDnaSequencingFromBlood(VeloxSeleniumScript):
    """
    An automation suite for the "ELN TruSeq DNA Sequencing from Blood Process Test Plan" script.
    """
    _receiving_plate_id: Optional[str] = None
    _request_id: Optional[str] = None
    _dna_extraction_plate_id: Optional[str] = None
    _lib_prep_plate_id: Optional[str] = None
    _lib_prep_rerun_plate_id: Optional[str] = None
    _pools: List[str] = None
    _single_sequencing_run: bool = False

    def set_single_sequencing_run(self, single_sequencing_run: bool) -> None:
        self._single_sequencing_run = single_sequencing_run

    def create_ten_new_samples(self) -> None:
        # step 1
        # main menu -> registration -> Sample Management -> Sample Registration
        self.do.main_menu(["Registration", "Sample Management", "Sample Registration"])

        # step 2
        # click on first entry
        exp = ElnExperiment(self.driver)
        exp.activate_entry("New Samples")

        # "register new samples" dialog -> click "Create New" dialog button
        register_new_samples_diag = Dialog.get_dialog_with_title("Register New Samples", self.driver)
        register_new_samples_diag.click_bottom_dialog_button("Create New")

        # "number of samples" dialog -> enter 10 into "Number of Samples" field; press OK dialog button
        num_of_samples_diag = Dialog.get_dialog_with_title("Number of Samples", self.driver)
        number_of_samples_form: windowobj.VeloxForm = num_of_samples_diag.get_form()
        number_of_samples_form.set_string_field("Number of Samples", "10")
        num_of_samples_diag.click_bottom_dialog_button("OK")

        # "please select a sample type" dialog -> double-click "Default/Standard" row
        sample_type_diag = Dialog.get_dialog_with_title("Please Select a Sample Type", self.driver)
        sample_type_diag.filter("Default/Standard")

        # wait for the entry to re-load
        self.driver.wait_until_clickable(
            lambda d: exp.get_eln_entry_with_title("New Samples").main_element
        )

        self.screenshot("request creation step 2")

    def create_96_samples_from_file_using_experiments(self):
        logging.info("Starting Sample Registration")

        # step 3
        # main menu -> registration -> Sample Management -> Sample Registration
        self.do.main_menu(["Registration", "Sample Management", "Register Samples"])

        if Dialog.dialog_exists("Select a Parent", DialogExistsSearchType.CONTAINS, self.driver):
            location_diag = dialogs.LocationPickerDialog.get_location_picker_dialog("Select a Parent", self.driver)
            location_diag.select_first_location()
            location_diag.make_default()

        # step 4
        # click "New Samples" entry
        exp = ElnExperiment(self.driver)
        exp.activate_entry("New Samples")

        # "register new samples" dialog; click "Import from Spreadsheet" dialog button
        Dialog.get_dialog_with_title("Register New Samples", self.driver). \
            click_bottom_dialog_button("Import from Spreadsheet")

        if Dialog.dialog_exists("Select a Pre-Defined Mapping", DialogExistsSearchType.EXACT, self.driver):
            mapping_dialog: Dialog = Dialog.get_dialog_with_title("Select a Pre-Defined Mapping", self.driver)
            mapping_dialog.filter_and_select("[!-- DEFINE NEW MAPPING --]")

        # "sample registration" dialog; click "Load Plate Manifest" dialog button
        Dialog.get_dialog_with_title("Load Sample Manifest", self.driver).click_bottom_dialog_button(
            "Load Plated Sample Manifest")
        # "load sample manifest" dialog; click "Browse Files" form button
        load_sample_manifest_dialog: Dialog = Dialog.get_dialog_with_title("Load Sample Manifest", self.driver)

        # upload "noplate_sample_manifest.xlsx" test file
        file_data: bytes = resources.read_binary(__package__,
                                                 "noplate_sample_manifest.xlsx")
        tube_manifest_path: str = self.file_man.upload_temp_bytes("tube_manifest", file_data)
        self.driver.drop_file(Path(tube_manifest_path), load_sample_manifest_dialog.body)

        # "please select a sample type" dialog; double-click "Default/Standard"
        sample_type_diag = Dialog.get_dialog_with_title("Please Select a Sample Type", self.driver)
        sample_type_diag.filter_and_select("Default/Standard")

        map_headers_dialog: Dialog = Dialog.get_dialog_with_title("Map Headers to Fields", self.driver)
        map_headers_grid: windowobj.VeloxGrid = windowobj.VeloxGrid(
            map_headers_dialog, map_headers_dialog.body.find_element(By.CSS_SELECTOR, windowobj.VeloxGrid.BY_CSS))
        # scroll to row with "data field name" column value "WellLocation"
        map_headers_dialog.filter_and_select("WellLocation")
        # for that row, set "File Header" field to "Well Position"
        map_headers_grid.set_enum_value(0, "File Header", "Well Position")
        # press OK
        map_headers_dialog.click_bottom_dialog_button("OK")

        # "sample import" dialog; choose "No" dialog button
        Dialog.get_dialog_with_title("Sample Import", self.driver).click_bottom_dialog_button("No")
        # "plate creation" dialog; choose "OK" dialog button
        Dialog.get_dialog_with_title("Plate Creation", self.driver).click_bottom_dialog_button("OK")

        # step 5
        # scroll to bottom of "New Samples" table
        new_samples_grid: windowobj.VeloxGrid = self.driver.wait_until_refreshed(
            lambda d: exp.get_eln_table_entry_with_title("New Samples").grid)
        new_samples_grid.scroll_to_bottom()
        self.screenshot("request creation step 5")

        # step 6
        # set row 1 Sample Type column Blood
        new_samples_grid.set_value(0, "Sample Type", "Blood")
        # shift-select row 96 Sample Type column
        new_samples_grid.select(0, "Sample Type", 95, "Sample Type")
        # autofill
        new_samples_entry: ElnTableEntry = exp.get_eln_table_entry_with_title("New Samples")
        new_samples_entry.toolbar.click_auto_fill()

        # refresh experiment
        exp.eln_toolbar.click_refresh()
        new_samples_entry = self.driver.wait_until_refreshed(
            lambda d: ElnExperiment(self.driver).get_eln_table_entry_with_title("New Samples")
        )
        self.driver.scroll_into_view(new_samples_entry.main_element)
        self.screenshot("request creation step 6")

        # step 7
        # submit "New Samples" entry
        exp.submit_entry("New Samples")
        Dialog.get_dialog_with_title("Select an Option", self.driver).click_bottom_dialog_button("Receive them")
        sample_receipt_detail_entry: ElnTableEntry = exp.get_eln_table_entry_with_title("Sample Receipt Details")
        self.driver.scroll_into_view(sample_receipt_detail_entry.main_element)
        self.screenshot("request creation step 7")

        # step 8
        # get Sample Receipt Details table entry
        # set row 1, "Sample Receipt Status" to "Rejected"
        sample_receipt_detail_entry.grid.set_value(0, "Sample Receipt Status", "Rejected")
        # set row 1, "Rejection Reason" to "Container Compromised"
        sample_receipt_detail_entry.grid.set_value(0, "Rejection Reason", "Container Compromised")
        # submit entry
        sample_receipt_detail_entry.submit()

        # storage information dialog
        storage_dialog: StorageDialog = StorageDialog.get_storage_dialog_with_title("Storage Information", self.driver)
        self._receiving_plate_id = storage_dialog.grid.get_cell_value(0, "Plate")
        logging.info("Receiving plate ID: " + self._receiving_plate_id)

        storage_dialog.place_all_into_storage()
        storage_dialog.click_bottom_dialog_button("OK")

        # step 9
        # get no-title dialog; click "Add to New Request" dialog button
        Dialog.get_dialog_with_title("Request Creation", self.driver).click_bottom_dialog_button("Add to New Request")

        # copy the "Request ID" value out of the form
        request_details_entry: ElnEntry = exp.get_eln_entry_with_title("Request Details")
        self.driver.scroll_into_view(request_details_entry.main_element)
        self._request_id = "ASDF-" + str(time.time_ns())
        request_details_entry.form.set_string_field("Request Name", self._request_id)

        # get the "Request Details" entry and submit it
        request_details_entry.submit()

        # wait for requested services entry to refresh
        exp.wait_until_entry_ready("Requested Service(s)")

        requested_services_entry: RequestedServicesEntry = RequestedServicesEntry.wrap(
            exp.get_eln_entry_with_title("Requested Service(s)"))
        self.driver.scroll_into_view(requested_services_entry.main_element)
        requested_services_entry.grid.scroll_to_bottom()
        self.screenshot("request creation step 9")

        # step 10
        # set row 1 "Services Requested" field to "ELN TruSeq DNA Sequencing from Blood" via its dialog
        requested_services_entry.set_services_requested(0, "ELN TruSeq DNA Sequencing from Blood")
        requested_services_entry.auto_fill(0, 94)
        requested_services_entry.submit()

        self.driver.wait_seconds(4)

    def create_96_samples_from_file_using_forms(self):
        logging.info("Starting Sample Registration")

        # step 3
        # main menu -> registration -> Sample Management -> Sample Registration
        self.do.main_menu(["Registration", "Sample Management", "Register Samples"])

        reg_dialog = Dialog.get_dialog_with_title("Register Samples", self.driver)

        form = reg_dialog.get_form()

        form.set_string_field("Sample Type", "Blood")

        self.driver.click(reg_dialog.main_element.find_element(By.XPATH, ".//*" + self.driver.x_path_ci_contains("Import with Mapping Template")))

        form.set_string_field("Mapping Template", "Create New Mapping Template")

        reg_dialog.click_bottom_dialog_button("Register Samples")

        # "sample registration" dialog; click "Load Plate Manifest" dialog button
        Dialog.get_dialog_with_title("Load Sample Manifest", self.driver).click_bottom_dialog_button(
            "Load Plated Sample Manifest")
        # "load sample manifest" dialog; click "Browse Files" form button
        load_sample_manifest_dialog: Dialog = Dialog.get_dialog_with_title("Load Sample Manifest", self.driver)

        # upload "noplate_sample_manifest.xlsx" test file
        file_data: bytes = resources.read_binary(__package__,
                                                 "noplate_sample_manifest.xlsx")
        tube_manifest_path: str = self.file_man.upload_temp_bytes("tube_manifest", file_data)
        self.driver.drop_file(Path(tube_manifest_path), load_sample_manifest_dialog.body)

        # "File Contains Headers?" dialog
        sample_type_diag = Dialog.get_dialog_with_title("File Contains Headers?", self.driver)
        sample_type_diag.click_bottom_dialog_button("Yes")

        map_headers_dialog: Dialog = Dialog.get_dialog_with_title("Map Headers to Fields", self.driver)
        map_headers_grid: windowobj.VeloxGrid = windowobj.VeloxGrid(
            map_headers_dialog, map_headers_dialog.body.find_element(By.CSS_SELECTOR, windowobj.VeloxGrid.BY_CSS))
        # scroll to row with "data field name" column value "WellLocation"
        map_headers_dialog.filter_and_select("WellLocation")
        # for that row, set "File Header" field to "Well Position"
        map_headers_grid.set_enum_value(0, "File Header", "Well Position")
        # press OK
        map_headers_dialog.click_bottom_dialog_button("OK")

        # "sample import" dialog; choose "No" dialog button
        Dialog.get_dialog_with_title("Sample Import", self.driver).click_bottom_dialog_button("No")

        # "plate creation" dialog; choose "OK" dialog button
        Dialog.get_dialog_with_title("Plate Creation", self.driver).click_bottom_dialog_button("OK")

        # wait for the IDV to load
        self.driver.wait_for(lambda d: MainPage(self.driver).integrated_data_view.main_element)

        # get the main IDV
        idv = MainPage(self.driver).integrated_data_view

        def wait_for_idv(driver):
            try:
                if len(idv.active_panel.component_panels) > 1:
                    return idv.active_panel.component_panels[1]
                else:
                    return None
            except StaleElementReferenceException:
                return None

        self.driver.wait_for(wait_for_idv, must_be_visible=False)
        idv_tab_panel_component = idv.active_panel.component_panels[1]
        idv_tabs = VeloxTabPanel(idv_tab_panel_component,
                                 idv_tab_panel_component.main_element.find_element(By.CSS_SELECTOR,
                                                                                   VeloxTabPanel.CSS_SELECTOR))

        # get the samples tab
        samples_panel = VeloxPanel(idv_tabs, idv_tabs.active_tab_contents)
        samples_toolbar = VeloxToolbar(samples_panel, samples_panel.main_element)

        # change sample types to Blood
        samples_grid = VeloxGrid(samples_panel,
                                 samples_panel.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS))
        samples_grid.set_value(0, "Sample Type", "Blood")
        samples_grid.select(0, "Sample Type", 95, "Sample Type")
        samples_toolbar.click_auto_fill()

        receive_samples_btn = samples_toolbar.get_button_contains_text("Receive Samples")
        VeloxToolbar(idv, idv.main_element).get_button_contains_text("Save").click()

        # receive the samples -- have to do a stale wait first, since the prior save is going to refresh the toolbar
        self.driver.wait_until_stale(receive_samples_btn.main_element)

        # toolbar has refreshed or is refreshing, so wait for the button to appear again
        self.driver.wait_for(lambda d: samples_toolbar.get_button_contains_text("Receive Samples"),
                             must_be_visible=False)

        # and now click the button since we know it's there and ready
        samples_toolbar.get_button_contains_text("Receive Samples").click()

        receive_samples_dialog = VeloxDialog.get_dialog_with_title("Receive Samples", self.driver)
        receive_samples_dialog.grid.set_value(0, "Sample Receipt Status", "Rejected")
        receive_samples_dialog.grid.set_value(0, "Rejection Reason", "Container Compromised")
        receive_samples_dialog.click_bottom_dialog_button("OK")

        # wait for the tab strip to reload, since this will have added a Receiving Receipts tab
        self.driver.wait_until_stale(idv_tabs.main_element)

        # fetch a fresh IDV again
        idv = MainPage(self.driver).integrated_data_view
        self.driver.wait_for(wait_for_idv, must_be_visible=False)
        idv_tab_panel_component = idv.active_panel.component_panels[1]
        idv_tabs = VeloxTabPanel(idv_tab_panel_component,
                                 idv_tab_panel_component.main_element.find_element(By.CSS_SELECTOR,
                                                                                   VeloxTabPanel.CSS_SELECTOR))

        # click on the plates tab
        idv_tabs.click_tab("Plates")

        # put the plate into storage
        plates_panel = VeloxPanel(idv_tabs, idv_tabs.active_tab_contents)
        plates_grid = VeloxGrid(plates_panel, plates_panel.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS))
        plates_grid.select_all()
        plates_toolbar = VeloxToolbar(plates_panel, plates_panel.main_element)
        plates_toolbar.get_button_contains_text("Manage Storage").click()

        storage_dialog: StorageDialog = StorageDialog.get_storage_dialog_with_title("Storage Information", self.driver)
        self._receiving_plate_id = storage_dialog.grid.get_cell_value(0, "Plate")
        logging.info("Receiving plate ID: " + self._receiving_plate_id)

        storage_dialog.place_all_into_storage()
        storage_dialog.click_bottom_dialog_button("OK")

        # check for storage failure
        if VeloxDialog.dialog_exists("Running Plugin", DialogExistsSearchType.STARTS_WITH, self.driver, 3):
            logging.info("Storage failed -- skipping storage")
            # close error dialog
            VeloxDialog.get_top_most_dialog(self.driver).close()
            # close storage dialog
            VeloxDialog.get_top_most_dialog(self.driver).close()

        # fetch a fresh IDV again
        idv = MainPage(self.driver).integrated_data_view
        self.driver.wait_for(wait_for_idv, must_be_visible=False)
        idv_tab_panel_component = idv.active_panel.component_panels[1]
        idv_tabs = VeloxTabPanel(idv_tab_panel_component,
                                 idv_tab_panel_component.main_element.find_element(By.CSS_SELECTOR,
                                                                                   VeloxTabPanel.CSS_SELECTOR))

        # back to Samples tab so we can create a request
        idv_tabs.click_tab("Samples")

        samples_panel = VeloxPanel(idv_tabs, idv_tabs.active_tab_contents)
        samples_grid = VeloxGrid(samples_panel,
                                 samples_panel.main_element.find_element(By.CSS_SELECTOR, VeloxGrid.BY_CSS))
        samples_grid.select_all()
        samples_toolbar = VeloxToolbar(samples_panel, samples_panel.main_element)
        samples_toolbar.get_button_contains_text("Create Request").click()

        request_dialog = VeloxDialog.get_dialog_with_title("Assign to Process", self.driver)
        request_grid = request_dialog.grid
        request_grid.set_value(0, "New Process Workflow",
                               "ELN TruSeq DNA Sequencing from Blood: Process Step #1 (Branch: 4): DNA Extraction")
        request_grid.select(0, "New Process Workflow", 94, "New Process Workflow")
        request_toolbar = VeloxToolbar(request_dialog,
                                       request_dialog.body.find_element(By.CSS_SELECTOR, VeloxToolbar.CSS_CLASS))
        request_toolbar.click_auto_fill()
        request_dialog.click_bottom_dialog_button("OK")

        # wait for Requests tab to appear in tab strip
        self.driver.wait_until_stale(idv_tabs.main_element)

        idv = MainPage(self.driver).integrated_data_view
        self.driver.wait_for(wait_for_idv, must_be_visible=False)
        idv_tab_panel_component = idv.active_panel.component_panels[1]
        idv_tabs = VeloxTabPanel(idv_tab_panel_component,
                                 idv_tab_panel_component.main_element.find_element(By.CSS_SELECTOR,
                                                                                   VeloxTabPanel.CSS_SELECTOR))
        idv_tabs.click_tab("Requests")

        requests_form = VeloxForm(idv_tabs, idv_tabs.active_tab_contents)
        self._request_id = "ASDF-" + str(time.time_ns())
        requests_form.set_string_field("Request Name", self._request_id)

        VeloxToolbar(idv, idv.main_element).get_button_contains_text("Save").click()

        self.driver.wait_seconds(4)

    def wf1_eln_dna_extraction(self):
        logging.info("Starting DNA Extraction")

        self.do.home_page()

        pq_event = self.perf_logger.start("Process Queue", True)

        home_page_tab_panel: windowobj.VeloxTabPanel = MainPage(self.driver).home_page_tab_panel
        if home_page_tab_panel.has_tab("Requests Awaiting Approval"):
            home_page_tab_panel.click_tab("Requests Awaiting Approval")
            # active tab should now have a grid with requests
            # approve the request
            requests_awaiting_approval: RequestsAwaitingApproval = RequestsAwaitingApproval(
                home_page_tab_panel, home_page_tab_panel.active_tab_contents)
            requests_awaiting_approval.approve_request(self._request_id)

        # step 1
        # make sure the process queue is showing
        if (home_page_tab_panel.has_tab("Process Queue") and
                home_page_tab_panel.get_tab_with_text("Process Queue").is_displayed()):
            home_page_tab_panel.click_tab("Process Queue")

        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        # show the queue
        process_queue.click_queued_button()
        # select our process and step
        process_queue.click_process_step("ELN TruSeq DNA Sequencing from Blood", "DNA Extraction")
        # work with plates
        process_queue.click_plates_button()
        # scan our plate ID
        process_queue.scan_values([self._receiving_plate_id])
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("DNA Extraction - Process Queue")
        # start the workflow
        process_queue.click_start_workflow_button()

        # step 2
        exp = ElnExperiment(self.driver)
        pq_event.end()
        # submit "Consumable Tracking" entry
        consumable_tracking_entry = exp.get_eln_table_entry_with_title("Reagent Tracking")
        consumable_tracking_entry.grid.set_value(0, "Lot Number", "ASDFGH" + str(time.time_ns()))
        consumable_tracking_entry.grid.set_value(0, "Quantity Used", "2")
        consumable_tracking_entry.submit()

        # may prompt to select a consumable part
        if Dialog.dialog_exists("Select a", DialogExistsSearchType.STARTS_WITH, self.driver):
            d: Dialog = Dialog.get_top_most_dialog(self.driver)
            d.grid.double_click_row_number(0)

        # may prompt with "New Part(s)" dialog
        if Dialog.dialog_exists("Please Select", DialogExistsSearchType.STARTS_WITH, self.driver):
            Dialog.get_top_most_dialog(self.driver).filter_and_select_containing("Consumable")
        if Dialog.dialog_exists("New Part", DialogExistsSearchType.CONTAINS, self.driver) or \
                Dialog.dialog_exists("New Item", DialogExistsSearchType.CONTAINS, self.driver):
            new_part_dialog: Dialog = Dialog.get_top_most_dialog(self.driver)
            form = new_part_dialog.get_form()
            form.set_string_field("Part Number", "HGFDSA" + str(time.time_ns()))
            form.set_string_field("Quantity / Volume Per Item", "999")
            form.set_string_field("Quantity", "2")
            new_part_dialog.click_bottom_dialog_button("OK")

        # step 3
        # get instrument tracking table entry
        instrument_tracking_entry: ElnTableEntry = exp.get_eln_table_entry_with_title("Instrument Tracking")
        self.driver.scroll_into_view(instrument_tracking_entry.main_element)
        # set row 1 "Technician" to current username
        if not instrument_tracking_entry.grid.empty:
            instrument_tracking_entry.grid.set_value(0, "Technician", self._username)
            instrument_tracking_entry.grid.set_date_value_to_today(0, "Date")
        instrument_tracking_entry.submit()

        # step 4
        # activate the "Setup DNA Library Plate" CSP entry
        self.driver.wait_seconds(3)
        plate_entry_name: str = "Setup DNA Plate"
        exp.activate_entry(plate_entry_name)
        exp.wait_until_entry_ready(plate_entry_name)
        plate_entry: Plater3DEntry = Plater3DEntry.wrap(exp.get_eln_entry_with_title(plate_entry_name))
        self.driver.scroll_into_view(plate_entry.main_element)
        # drag all samples to A1 well; choose "Fill by Row (SE)" when prompted in
        # "EDIT WELL ASSIGNMENT SETTINGS" dialog then OK
        plate_entry.move_all_to_well("A", 1, Plater3DFillByMethod.FILL_BY_ROW_SE)
        self.screenshot("DNA Library Prep - Setup DNA Library Plate")
        plate_entry.submit()

        # it might yell about insufficient volume
        if Dialog.dialog_exists("Submitting Entry", DialogExistsSearchType.EXACT, self.driver):
            d: Dialog = Dialog.get_dialog_with_title("Submitting Entry", self.driver)
            d.close()

        # step 5
        derived_samples_entry_name: str = "Derived DNA Samples"
        derived_samples_entry: ElnTableEntry = self.driver.stale_wait().until(
            lambda x: exp.get_eln_table_entry_with_title(derived_samples_entry_name)
        )
        self.driver.scroll_into_view(derived_samples_entry.main_element)
        # move the mouse out of the way, otherwise we may get a tooltip covering the grid
        self.driver.move_mouse_to(0, 0)
        # wait a few seconds in case there is a tooltip covering the grid
        self.driver.wait_seconds(3)
        self._dna_extraction_plate_id = derived_samples_entry.grid.get_cell_value(
            0, "Storage Location Barcode")
        logging.info("DNA Extraction Plate ID: " + self._dna_extraction_plate_id)
        self.screenshot("eln dna extraction step 5")
        derived_samples_entry.submit()

        # complete workflow
        exp.eln_toolbar.complete_experiment()
        self.driver.wait_seconds(1.5)

    def wf2_eln_quality_control(self):
        logging.info("Starting Quality Control")
        self.do.home_page()

        pq_event = self.perf_logger.start("Process Queue", True)

        home_page_tab_panel: windowobj.VeloxTabPanel = MainPage(self.driver).home_page_tab_panel
        # make sure the process queue is showing
        if (home_page_tab_panel.has_tab("Process Queue") and
                home_page_tab_panel.get_tab_with_text("Process Queue").is_displayed()):
            home_page_tab_panel.click_tab("Process Queue")

        # steps 1 + 2
        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        process_queue.click_queued_button()
        process_queue.click_process_step_by_number("ELN TruSeq DNA Sequencing from Blood", 2)
        try:
            process_queue.click_plates_button(timeout_seconds=5)
        except (NoSuchElementException, TimeoutException):
            # In SAAS this is enforced to be plate only. In regular workflow a customer complained so we allow both.
            pass
        process_queue.scan_values([self._dna_extraction_plate_id])
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("WF2 QC Plate Scan")

        process_queue.click_start_workflow_button()

        pq_event.end()

        # submit all entries
        self._qc_simulated_input_output()
        # the exp needs to be created after qc because if created before it becomes stale after switch group.
        exp = ElnExperiment(self.driver)
        exp.submit_entry("Final Instrument Results")

        exp.eln_toolbar.complete_experiment()
        self.driver.wait_seconds(10)

    def _qc_simulated_input_output(self):
        qc_perf = self.perf_logger.start("Get QC Output File", True)
        # Generate simulated output files as admin
        self.driver.wait_seconds(5)
        exp = ElnExperiment(self.driver)
        MainPage(self.driver).west_panel.quick_access_toolbar.change_group("Sapio Admin")
        self.driver.wait_seconds(5)
        exp = ElnExperiment(self.driver)
        samples_entry: ElnEntry = exp.get_eln_entry_with_title("Samples")
        fake_output_button: VeloxButton = samples_entry.toolbar.get_button_with_icon("printqcoutputfilesamplesentry")
        fake_output_button.click()
        output_file_prompt: Dialog = Dialog.get_dialog_with_title(
            "Generate Output File By Selecting An Assay Type", self.driver)
        output_file_prompt.filter_and_select("Qubit")

        # Switch back to normal user to keep running QC.
        self.driver.wait_seconds(5)
        MainPage(self.driver).west_panel.quick_access_toolbar.change_group("Seamless LIMS")
        self.driver.wait_seconds(5)
        exp = ElnExperiment(self.driver)
        qc_perf.end()

        qc_perf = self.perf_logger.start("QC Instrument Results", True)
        exp.get_eln_entry_with_title("Reagent Tracking").submit()
        exp.get_eln_entry_with_title("QC Instrument Results").activate()
        output_file_prompt = Dialog.get_dialog_with_title("Select an Instrument", self.driver)
        output_file_prompt.filter_and_select("Qubit")
        last_downloaded: str = self.driver.file_man.get_last_downloaded_file()
        file_drop_dialog: Dialog = Dialog.get_dialog_with_title("Select file:", self.driver)
        self.driver.drop_file(pathlib.Path(last_downloaded), file_drop_dialog.body)
        self.driver.wait_seconds(12)
        if Dialog.dialog_exists("Running Plugin...", DialogExistsSearchType.EXACT, self.driver):
            Dialog.get_dialog_with_title("Running Plugin...", self.driver).close()
        self.driver.wait().until(
            lambda d: not Dialog.dialog_exists("Performing ELN Template Entry Action",
                                               DialogExistsSearchType.EXACT, self.driver))
        # if Dialog.dialog_exists("Performing ELN Template Entry Action", DialogExistsSearchType.EXACT, self.driver):
        #     Dialog.get_dialog_with_title("Performing ELN Template Entry Action", self.driver).close()
        exp.get_eln_entry_with_title("Instrument Results for Qubit").submit()
        qc_perf.end()

        qc_perf = self.perf_logger.start("Final Instrument Results", True)
        exp.activate_entry("Final Instrument Results")
        qc_perf.end()

    def wf3_dna_lib_prep(self):
        self._lib_prep_plate_id = self._dna_lib_prep(self._dna_extraction_plate_id)

    def wf4_eln_quality_control(self, plate_ids: List[str] = None, is_rerun: bool = False):
        logging.info("Starting Quality Control WF4")
        if not plate_ids:
            plate_ids = [self._lib_prep_plate_id]

        # log the plate IDs
        logging.info("Plate IDs: " + str(plate_ids))

        qc_event = self.perf_logger.start("QC wait for homepage", True)
        self.do.home_page()
        qc_event.end()

        pq_event = self.perf_logger.start("Process Queue", True)

        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        # show the queue
        process_queue.click_queued_button()
        # select our process and step
        # (there are two QC workflows, so reference it by the step number instead)
        process_queue.click_process_step_by_number("ELN TruSeq DNA Sequencing from Blood", 4)
        try:
            process_queue.click_plates_button(timeout_seconds=5)
        except (NoSuchElementException, TimeoutException):
            # In SAAS this is enforced to be plate only. In regular workflow a customer complained so we allow both.
            pass
        process_queue.scan_values(plate_ids)
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("WF4 QC Plate Scan")
        process_queue.click_start_workflow_button()

        pq_event.end()

        # step 2
        # the exp needs to be created after qc because if created before it becomes stale after switch group.
        self._qc_simulated_input_output()

        qc_event = self.perf_logger.start("Submit and complete" if is_rerun else "Fail and complete", True)
        exp = ElnExperiment(self.driver)

        results_table = exp.get_eln_table_entry_with_title("Final Instrument Results")
        if is_rerun:
            # We are rerun of the two reprocessed samples. By script, we will now pass them.
            results_table.submit()
            self.screenshot("WF4 Rerun Passing")
        else:
            # We set the first one failed, second and third one failed reprocess to step number 3 and 4 respectively.
            # We leave others as passed.
            results_table.grid.set_enum_value(0, "Final QC Status", "Failed")
            results_table.grid.set_enum_value(1, "Final QC Status", "Failed - Reprocess")
            results_table.grid.set_enum_value(2, "Final QC Status", "Failed - Reprocess")
            self.screenshot("WF4 Manual Failure Overrides")
            results_table.submit()

            reprocess_samples_dialog: Dialog = Dialog.get_dialog_with_title("Reprocess Samples", self.driver)
            reprocess_samples_dialog_grid: windowobj.VeloxGrid = reprocess_samples_dialog.grid
            # move the mouse out of the way, otherwise we may get a tooltip covering the grid
            self.driver.move_mouse_to(0, 0)
            # wait a few seconds in case there is a tooltip covering the grid
            self.driver.wait_seconds(3)
            self.screenshot("WF4 Reprocessing Steps About to be Chosen")
            # click into the cell and give it a second or two to load the dropdown values
            reprocess_samples_dialog_grid.click_cell(0, "Reprocessing Step")
            self.driver.wait_seconds(3)
            self.screenshot("WF4 Reprocessing Steps Row One Clicked")
            reprocess_samples_dialog_grid.set_value(0, "Reprocessing Step", "[3] ELN DNA Library Preparation (DNA)")
            reprocess_samples_dialog_grid.set_value(1, "Reprocessing Step", "[4] ELN Quality Control (DNA Library)")
            self.screenshot("WF4 Reprocessing Steps Chosen")

            reprocess_samples_dialog.click_bottom_dialog_button("OK")

        exp.eln_toolbar.complete_experiment()
        self.driver.wait_seconds(10)
        qc_event.end()

        if not is_rerun:
            qc_event = self.perf_logger.start("QC prepping for rerun", True)
            logging.info("Now rerun those two failed - reprocess samples back to dna lib prep...")
            self._lib_prep_rerun_plate_id = self._dna_lib_prep(self._dna_extraction_plate_id)
            qc_event.end()
            self.wf4_eln_quality_control(plate_ids=[self._lib_prep_plate_id, self._lib_prep_rerun_plate_id],
                                         is_rerun=True)

    def wf5_pooling(self):
        self._sample_pooling(True)
        self._sample_pooling(False)

    def wf6_sequencing(self, single_run: bool = False):
        if single_run:
            run_mode = SequencingRunMode.HiSeqRapidRun
            perf = self.perf_logger.start("Sequencing " + run_mode.display_name)
            self._sequencing(run_mode)
            ElnExperiment(self.driver).eln_toolbar.complete_experiment()
            self.driver.wait(2)
            self.do.home_page()
            perf.end()
        else:
            for run_mode in SequencingRunMode:
                perf = self.perf_logger.start("Sequencing " + run_mode.display_name)
                self._sequencing(run_mode)
                ElnExperiment(self.driver).eln_toolbar.cancel_experiment()
                self.driver.wait(2)
                self.do.home_page()
                perf.end()

    def _sequencing(self, run_mode: SequencingRunMode):
        logging.info("Starting Illumina Sequencing (" + run_mode.display_name + ")")
        self.do.home_page()

        pq_event = self.perf_logger.start("Process Queue", True)

        # step 1
        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        process_queue.click_queued_button()
        process_queue.click_process_step("ELN TruSeq DNA Sequencing from Blood", "Illumina Sequencing")
        process_queue.scan_values(self._pools[0: max(len(self._pools), run_mode.num_of_pools)])
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("Sequencing " + run_mode.display_name + " - Process Queue")
        process_queue.click_start_workflow_button()

        exp: ElnExperiment = ElnExperiment(self.driver)
        pq_event.end()
        sequencing_detail_entry: ElnEntry = exp.get_eln_entry_with_title("Illumina Sequencing Run Details")
        self.driver.scroll_into_view(sequencing_detail_entry.main_element)
        sequencing_detail_entry.form.set_string_field("Sequencing Run Mode", run_mode.display_name)
        sequencing_detail_entry.submit()

        # get "Manage Flow Cell Assignments" CSP entry
        exp.wait_until_entry_ready("Manage Flow Cell Assignments")
        manage_flow_cell_assignments_entry: FlowCellEntry = FlowCellEntry.wrap(
            exp.get_eln_entry_with_title("Manage Flow Cell Assignments"))
        manage_flow_cell_assignments_entry.set_flow_cell_id("ASDFGHXX")
        self.screenshot("Sequencing " + run_mode.display_name)

        if run_mode.expected_lane_count:
            # verify lane count
            num_of_lanes: int = manage_flow_cell_assignments_entry.num_of_lanes
            if num_of_lanes != run_mode.expected_lane_count:
                raise ValueError(run_mode.display_name + " expecting " + str(run_mode.expected_lane_count) +
                                 "lanes, but " + str(num_of_lanes) + " lanes were found.")

        if run_mode.should_auto_assign:
            # verify auto-assignment
            if not manage_flow_cell_assignments_entry.has_assignments:
                raise ValueError(run_mode.display_name + " expecting lanes to be auto-assigned, "
                                                         "but lanes were not auto-assigned.")
        else:
            manage_flow_cell_assignments_entry.click_auto_assign()

        manage_flow_cell_assignments_entry.submit()

        if run_mode.has_on_submit_prompts:
            Dialog.get_dialog_with_title("Select Sequencing Workflow", self.driver).filter_and_select("GenerateFASTQ")
            Dialog.get_dialog_with_title("Select Assay", self.driver).filter_and_select("Nextera XT")

            fastq_dialog: Dialog = Dialog.get_dialog_with_title("GenerateFASTQ", self.driver)
            fastq_dialog.get_form().set_string_field("Reagent Cartridge Barcode", "TEST" + str(time.time_ns()))
            fastq_dialog.click_bottom_dialog_button("OK")

            if run_mode.has_sample_details_prompt:
                Dialog.get_dialog_with_title("Enter Sample Details", self.driver).click_bottom_dialog_button("OK")

        self.driver.wait_seconds(5)
        exp.wait_until_entry_ready("Generate Sample Sheet")
        self.driver.scroll_into_view(exp.get_eln_entry_with_title("Generate Sample Sheet").main_element)
        self.screenshot("Sequencing " + run_mode.display_name + " sample sheet")
        self.driver.wait_seconds(3)

    def _sample_pooling(self, cancel: bool):
        logging.info("Starting Sample Pooling")
        self.do.home_page()
        pq_event = self.perf_logger.start("Process Queue", True)
        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        process_queue.click_queued_button()
        process_queue.click_process_step("ELN TruSeq DNA Sequencing from Blood", "Sample Pooling")
        process_queue.click_plates_button()
        process_queue.scan_values([self._lib_prep_plate_id, self._lib_prep_rerun_plate_id])
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("Sample Pooling - Process Queue")
        process_queue.click_start_workflow_button()

        exp: ElnExperiment = ElnExperiment(self.driver)
        pq_event.end()
        exp.activate_entry("Setup DNA Library Pooling")
        exp.wait_until_entry_ready("Setup DNA Library Pooling")
        self.driver.wait_seconds(3) # something ends up masking the menus, so wait a bit first
        pooling_entry: PoolingEntry = PoolingEntry.wrap(exp.get_eln_entry_with_title("Setup DNA Library Pooling"))
        self.driver.scroll_into_view(pooling_entry.main_element)
        pooling_entry.set_number_of_tubes(4)
        # wait for entry to refresh a bit
        self.driver.wait_seconds(3)
        pooling_entry.move_to_tube(0, 23, 0)
        self.driver.wait_seconds(3)
        pooling_entry.move_to_tube(24, 47, 1)
        self.driver.wait_seconds(3)
        pooling_entry.move_to_tube(48, 71, 2)
        self.driver.wait_seconds(3)
        pooling_entry.move_to_tube(72, 93, 3)
        self.driver.wait_seconds(3)
        self.screenshot("Sample Pooling")
        pooling_entry.submit()

        exp.submit_entry("DNA Library Pooling amounts per Sample")
        if cancel:
            exp.eln_toolbar.cancel_experiment()
        else:
            result_aliquot_entry = exp.get_eln_table_entry_with_title("Aliquoted DNA Library Samples")
            self.driver.scroll_into_view(result_aliquot_entry.main_element)
            self._pools = []
            for i in range(4):
                self._pools.append(result_aliquot_entry.grid.get_cell_value(i, "Sample ID"))
            exp.eln_toolbar.complete_experiment()
        self.driver.wait_seconds(10)

    def _dna_lib_prep(self, plate_id: str) -> str:
        logging.info("Starting DNA Library Prep")
        self.do.home_page()
        pq_event = self.perf_logger.start("Process Queue", True)
        process_queue: ProcessQueue = MainPage(self.driver).process_queue
        process_queue.click_queued_button()
        process_queue.click_process_step("ELN TruSeq DNA Sequencing from Blood", "DNA Library Preparation")
        process_queue.click_plates_button()
        process_queue.scan_values([plate_id])
        # wait half a second, then take a screenshot of the queue before moving on
        self.driver.wait_seconds(0.5)
        self.screenshot("DNA Library Prep - Process Queue")
        process_queue.click_start_workflow_button()

        # steps 2-3
        # get "DNA Library Preparation Reagents" entry and submit it
        exp = ElnExperiment(self.driver)
        pq_event.end()

        # look for an entry with a name "Sample Details" and submit it
        entry_list: list[ElnEntry] = exp.tab_panel.current_eln_page.eln_entry_list
        for entry in entry_list:
            if entry.entry_name == "Sample Details":
                entry.submit()
                break

        # not sure when this stopped being a template entry...
        # exp.activate_entry("Reagent Tracking")
        exp.submit_entry("Reagent Tracking")

        # may prompt with "New Part(s)" dialog a few times -- pick Consumable
        while Dialog.dialog_exists("Please Select", DialogExistsSearchType.CONTAINS, self.driver):
            Dialog.get_top_most_dialog(self.driver).filter_and_select_containing("Consumable")
        if Dialog.dialog_exists("New Part", DialogExistsSearchType.CONTAINS, self.driver) or \
                Dialog.dialog_exists("New Item", DialogExistsSearchType.CONTAINS, self.driver):
            new_part_dialog: Dialog = Dialog.get_top_most_dialog(self.driver)
            grid: windowobj.VeloxGrid = new_part_dialog.grid
            now: int = time.time_ns()
            grid.set_value(0, "Part Number", "HGFDSAA" + str(now))
            grid.set_value(1, "Part Number", "HGFDSAB" + str(now))
            grid.set_value(2, "Part Number", "HGFDSAC" + str(now))
            grid.set_value(0, "Quantity / Volume per Item", "999")
            grid.set_value(1, "Quantity / Volume per Item", "999")
            grid.set_value(2, "Quantity / Volume per Item", "999")
            new_part_dialog.click_bottom_dialog_button("OK")

        # step 4
        # get "Instrument Tracking" entry and submit it
        exp.get_eln_entry_with_title("Instrument Tracking").submit()

        # step 5
        # perform aliquot
        # activate "Setup DNA Library Plate" entry
        exp.activate_entry("Setup DNA Library Plate")
        exp.wait_until_entry_ready("Setup DNA Library Plate")
        setup_dna_lib_plate_entry: Plater3DEntry = Plater3DEntry.wrap(exp.get_eln_entry_with_title(
            "Setup DNA Library Plate"))
        # This scrolling is flakey in firefox. not sure why... it's the same code as above lol.
        self.driver.scroll_into_view(setup_dna_lib_plate_entry.main_element)
        #  select all samples and add to the plate
        setup_dna_lib_plate_entry.move_all_to_well('A', 1, Plater3DFillByMethod.FILL_BY_ROW_SE)
        self.screenshot("DNA Lib Prep - Setup DNA Library Plate")
        setup_dna_lib_plate_entry.submit()

        # it might yell about insufficient volume
        if Dialog.dialog_exists("Submitting Entry", DialogExistsSearchType.EXACT, self.driver):
            Dialog.get_dialog_with_title("Submitting Entry", self.driver).close()

        output_samples_entry_name: str = "Derived DNA Library Samples"
        aliquot_dna_lib_samples_entry: ElnTableEntry = exp.get_eln_table_entry_with_title(output_samples_entry_name)
        self.driver.scroll_into_view(aliquot_dna_lib_samples_entry.main_element)
        # move the mouse out of the way, otherwise we may get a tooltip covering the grid
        self.driver.move_mouse_to(0, 0)
        # wait a few seconds in case there is a tooltip covering the grid
        self.driver.wait_seconds(3)
        new_plate_id: str = aliquot_dna_lib_samples_entry.grid.get_cell_value(0, "Storage Location Barcode")
        single_sample = (aliquot_dna_lib_samples_entry.grid.last_row_number == 1)
        aliquot_dna_lib_samples_entry.submit()

        # perform indexing
        # activate index samples entry
        exp.activate_entry("Index Samples")
        exp.wait_until_entry_ready("Index Samples")
        # get "Index Samples" entry as Indexer CSP entry
        index_samples_entry: IndexerEntry = IndexerEntry.wrap(exp.get_eln_entry_with_title("Index Samples"))
        self.driver.scroll_into_view(index_samples_entry.main_element)
        # we'll have a single sample on when we're reprocessing, so use a different index type to keep things unique
        index_samples_entry.set_index_type("TruSeq" if single_sample else "IDT")
        index_samples_entry.move_all_to_well("a", 1)
        index_samples_entry.submit()

        # gets confused sometimes and doesn't think the entry is validated, so sleep a bit before completing
        self.driver.wait().until(lambda d: self.driver.is_stale(index_samples_entry.main_element))
        # self.driver.wait_seconds(2)

        # complete workflow
        exp.eln_toolbar.complete_experiment()
        self.driver.wait_seconds(10)

        return new_plate_id

    def _run_selenium_script(self) -> None:

        logging.info("TruSeq DNA Sequencing from Blood process starting!")

        start = self.perf_logger.start("TruSeq DNA Sequencing from Blood process")

        self.do.switch_group("Seamless LIMS")

        perf = self.perf_logger.start("Request Creation")
        if self.driver.target_sapio_version == SapioVersion.LATEST or \
                self.driver.target_sapio_version > SapioVersion.V24_12:
            self.create_96_samples_from_file_using_forms()
        else:
            self.create_96_samples_from_file_using_experiments()
        perf.end()

        perf = self.perf_logger.start("Workflow 1: ELN DNA Extraction")
        self.wf1_eln_dna_extraction()
        perf.end()

        perf = self.perf_logger.start("Workflow 2: QC")
        self.wf2_eln_quality_control()
        perf.end()

        perf = self.perf_logger.start("Workflow 3: DNA Library Preparation")
        self.wf3_dna_lib_prep()
        perf.end()

        perf = self.perf_logger.start("Workflow 4: QC")
        self.wf4_eln_quality_control()
        perf.end()

        perf = self.perf_logger.start("Workflow 5: Sample Pooling")
        self.wf5_pooling()
        perf.end()

        perf = self.perf_logger.start("Workflow 6: Illumina Sequencing")
        self.wf6_sequencing(self._single_sequencing_run)
        perf.end()

        start.end()

        self.do.logout()

