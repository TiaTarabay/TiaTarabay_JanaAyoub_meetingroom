

import os
import sys

# Add project root to Python path so autodoc can import your services
sys.path.insert(0, os.path.abspath('..'))



project = 'Smart Meeting Room System'
author = 'Tia & Jana'
release = '1.0.0'



extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []



html_theme = 'alabaster'
html_static_path = ['_static']
