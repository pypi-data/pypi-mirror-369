import logging
import sys
from pathlib import Path

from sapioseleniumlib.util.driver import BrowserType
from sapioseleniumlib.util.script import VeloxSeleniumScript
from sapioseleniumlib.widgets.eln import ElnExperimentPage
from sapioseleniumlib.widgets.eln import FlowCytometryEntry
from sapioseleniumlib.widgets.windowobj import VeloxDialog
from testconfig import username, password, headless, HOMEPAGE_URL


class FlowCytometryScript(VeloxSeleniumScript):
    def _run_selenium_script(self) -> None:
        start = self.perf_logger.start("Starting FlowCytometryScript")

        self.do.switch_group("Seamless ELN")
        self.do.create_ad_hoc_experiment()

        pe = self.perf_logger.start("Creating Flow Cytometry entry")
        exp = ElnExperimentPage(self.driver)
        logging.info("Creating Flow Cytometry entry")
        exp.add_entry_to_top(["Flow Cytometry"])
        flow_entry: FlowCytometryEntry = FlowCytometryEntry.wrap(
            exp.get_eln_entry_with_title("Flow Cytometry"))
        pe.end()

        pe = self.perf_logger.start("Uploading FCS file")
        logging.info("Uploading FCS file")
        flow_entry.click_upload_fcs_files_buttons()

        upload_fcs_dialog: VeloxDialog = VeloxDialog.get_dialog_with_title(
            "Upload FCS File for New Sample", self.driver)
        fcs_file = "export_COVID19 samples 21_04_20_ST3_COVID19_ICU_013_A ST3 210420_078_Live_cells.fcs"
        self.driver.drop_file(Path(fcs_file), upload_fcs_dialog.body)
        create_new_sample_dialog = VeloxDialog.get_dialog_with_title("Create New Sample", self.driver)
        create_new_sample_dialog.click_bottom_dialog_button("OK")
        pe.end()

        logging.info("Setting gating parameters")
        flow_entry.set_gating_settings("FSC-A", "FSC-H", "Auto",
                                       "No Normalization")

        logging.info("Draw Ellipse Gate")
        flow_entry.click_draw_gate()

        create_gate_dialog = VeloxDialog.get_dialog_with_title("Create Gate", self.driver)
        create_gate_dialog_form = create_gate_dialog.get_form()
        create_gate_dialog_form.send_tabs_after_edit = True
        create_gate_dialog_form.set_string_field("Name (Gate Label)", "My Ellipse")
        create_gate_dialog_form.set_string_field("Shape to Draw", "Ellipse")
        create_gate_dialog.click_bottom_dialog_button("Start Drawing")
        flow_entry.draw_lower_left_gate()
        flow_entry.click_gating_save()

        logging.info("Creating AI Gate")
        flow_entry.click_create_ai_gate()

        enter_new_ai_dialog = VeloxDialog.get_dialog_with_title("Enter Auto Gate Parameters", self.driver)
        enter_new_ai_form = enter_new_ai_dialog.get_form()
        enter_new_ai_form.send_tabs_after_edit = True
        enter_new_ai_form.set_string_field("Description", "My AI Gate")
        enter_new_ai_form.set_string_field("Percentile X", "50")
        enter_new_ai_form.set_string_field("Percentile Y", "50")
        enter_new_ai_dialog.click_bottom_dialog_button("OK")

        self.driver.wait_until_clickable(lambda d: exp.page_source)
        self.driver.wait_seconds(2)
        self.screenshot("Gates")

        logging.info("Performing AI QC")
        flow_entry.click_perform_ai_qc()
        VeloxDialog.get_dialog_with_title("Enter QC Parameter Details", self.driver).click_bottom_dialog_button("OK")
        flow_entry.wait_for_qc()
        self.screenshot("QC")

        self.driver.wait_seconds(5)

        start.end()


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

test = FlowCytometryScript(BrowserType.CHROME, HOMEPAGE_URL, username, password, headless)
test.run()
