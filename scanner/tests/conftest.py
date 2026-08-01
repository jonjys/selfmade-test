"""Gör paketet importerbart oavsett var pytest startas ifrån.

Utan detta fungerar `pytest tests/` från scanner-katalogen men inte
`pytest scanner/tests/` från repo-roten, eftersom a11yscan då inte ligger på
sökvägen. Den sortens fälla kostar mer tid än den ser ut att göra, särskilt i
CI där man sällan står i rätt katalog.
"""

import sys
from pathlib import Path

SCANNER_ROT = Path(__file__).resolve().parent.parent
if str(SCANNER_ROT) not in sys.path:
    sys.path.insert(0, str(SCANNER_ROT))
