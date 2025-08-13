import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from sapioseleniumlib.script.truseq_dna import TruSeqDnaSequencingFromBlood
from sapioseleniumlib.util.driver import SapioTestDriverFileManager, BrowserType
from sapioseleniumlib.util.script import SeleniumScriptMultiProcessor
from testconfig import HOMEPAGE_URL, password

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

GRID_URL = "https://grid.example.com"


def scale_test(homepage_url: str, num_users: int = 10):
    # run_id should be "TruSeqDNABlood-" and then the current timestamp as a string
    run_id = "TruSeqDNABlood-" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

    # list of users to run the test with (use the "user+selenium0@example.com" pattern, incrementing the number)
    users = []
    for i in range(0, num_users):
        users.append("user+selenium" + str(i) + "@example.com")

    scripts = []

    for i in range(len(users)):
        file_man: SapioTestDriverFileManager = SapioTestDriverFileManager(
            storage_dir_path=os.path.join(Path.home(), 'sapio_selenium_runs', run_id, "{:03d}".format(i)))

        script = TruSeqDnaSequencingFromBlood(BrowserType.CHROME, homepage_url, users[i], password,
                                              True, file_man=file_man,
                                              run_id="TruSeqDNABlood_" + str(i + 1),
                                              grid_url=GRID_URL)
        script.set_single_sequencing_run(True)

        scripts.append(script)

    processor = SeleniumScriptMultiProcessor(scripts, stagger_seconds=7)
    processor.start()


if __name__ == '__main__':
    scale_test(HOMEPAGE_URL, 1)
