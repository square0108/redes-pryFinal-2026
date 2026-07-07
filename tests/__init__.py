import sys
import os

root_pry = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if root_pry not in sys.path:
    sys.path.insert(0, root_pry)