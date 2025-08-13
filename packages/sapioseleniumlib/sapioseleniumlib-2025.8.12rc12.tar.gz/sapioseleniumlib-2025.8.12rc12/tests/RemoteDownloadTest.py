import logging
import sys

from sapioseleniumlib.util.driver import BrowserType
from sapioseleniumlib.util.script import VeloxSeleniumScript
from sapioseleniumlib.widgets.eln import ElnExperimentPage
from sapioseleniumlib.widgets.windowobj import VeloxDialog, VeloxButton
from testconfig import HOMEPAGE_URL, username, password, headless


class RemoteDownloadScript(VeloxSeleniumScript):
    def _run_selenium_script(self) -> None:
        # switch group so we can generate a QC file
        self.do.switch_group("Sapio Admin")

        # grab the experiment (we should already be there)
        exp = ElnExperimentPage(self.driver)

        # get the samples entry and click the fake output button
        samples_entry = exp.get_eln_table_entry_with_title("Samples")
        fake_output_button: VeloxButton = samples_entry.toolbar.get_button_with_icon("printqcoutputfilesamplesentry")
        fake_output_button.click()

        # select the Qubit assay type from the dialog and let it download
        output_file_prompt: VeloxDialog = VeloxDialog.get_dialog_with_title(
            "Generate Output File By Selecting An Assay Type", self.driver)
        output_file_prompt.filter_and_select("Qubit")

        self.driver.wait_seconds(5)

        # grab the file and see what's up
        file = self.driver.file_man.get_last_downloaded_file()
        logging.info(f"Downloaded file: {file}")

        self.driver.wait_seconds(5)


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

test = RemoteDownloadScript(BrowserType.CHROME, HOMEPAGE_URL, username, password, headless)
test.run()
