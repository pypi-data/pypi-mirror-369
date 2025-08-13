import logging
import sys

from sapioseleniumlib.script.truseq_dna import TruSeqDnaSequencingFromBlood
from sapioseleniumlib.util.driver import BrowserType
from sapioseleniumlib.util.script import SeleniumScriptMultiProcessor
from testconfig import HOMEPAGE_URL, username, password

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger().setLevel(logging.INFO)

scripts = []
for i in range(3):
    script = TruSeqDnaSequencingFromBlood(BrowserType.CHROME, HOMEPAGE_URL, username, password,
                                          True, run_id="TruSeqDNABlood_" + str(i + 1))
    scripts.append(script)

processor = SeleniumScriptMultiProcessor(scripts)
processor.start()
