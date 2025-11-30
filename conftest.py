import os
import sys

# Ensure the inner project directory is on sys.path so tests import correctly
ROOT = os.path.dirname(__file__)
INNER = os.path.join(ROOT, "IT Ticket Project")
if os.path.isdir(INNER) and INNER not in sys.path:
    sys.path.insert(0, INNER)
