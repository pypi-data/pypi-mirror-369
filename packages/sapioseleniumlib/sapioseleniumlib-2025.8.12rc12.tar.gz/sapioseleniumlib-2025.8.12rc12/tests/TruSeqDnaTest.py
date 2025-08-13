import logging
import sys
from datetime import datetime

from sapioseleniumlib.script.truseq_dna import TruSeqDnaSequencingFromBlood
from sapioseleniumlib.util.driver import BrowserType, SapioSeleniumDriver
from sapioseleniumlib.widgets.pages import MainPage
from sapioseleniumlib.widgets.panels import ProcessQueue
from testconfig import HOMEPAGE_URL, username, password

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)


def run_test():
    # run_id should be "TruSeqDNABlood-" and then the current timestamp as a string
    run_id = "TruSeqDNABlood-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

    test = TruSeqDnaSequencingFromBlood(BrowserType.CHROME,
                                        HOMEPAGE_URL,
                                        username, password,
                                        True, run_id=run_id,
                                        # browser_binary_location="/usr/bin/firefox",
                                        # grid_url='https://grid.example.com')
                                        # debugger_address='localhost:9333',
                                        # target_sapio_version=SapioVersion.V23_12
                                        )

    test.run()


def do_broken_thing():
    driver: SapioSeleniumDriver = SapioSeleniumDriver(BrowserType.CHROME, HOMEPAGE_URL, False,
                                                      debugger_address='localhost:9333', enable_debug_tools=True,
                                                      # target_sapio_version=SapioVersion.V23_12
                                                      )

    # we're assuming that the browser is already logged in and navigated to our experiment

    process_queue: ProcessQueue = MainPage(driver).process_queue
    process_queue.click_queued_button()
    process_queue.click_process_step("ELN TruSeq DNA Sequencing from Blood", "DNA Extraction")
    process_queue.click_plates_button()


# call do_broken_thing to debug the broken thing that you are testing
do_broken_thing()

# call run_test to run the full TruSeq test
# run_test()
