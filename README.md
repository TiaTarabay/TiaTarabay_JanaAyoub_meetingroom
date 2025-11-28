3️⃣ Create the Sphinx project in docs/

From the root of your repo:

cd docs
sphinx-quickstart .


Answer the prompts roughly like:

Separate source and build dirs? → n (simpler)

Project name → smartmeetingroom_TiaTarabay_JanaAyoub

Author → Tia Tarabay & Jana Ayoub

Language → en (default)

This will create:

docs/conf.py

docs/index.rst

docs/make.bat (for Windows)

docs/_build/ (after you build)

4️⃣ Configure conf.py for autodoc

Open docs/conf.py and:

Add project root to sys.path at the top:

import os
import sys
sys.path.insert(0, os.path.abspath('..'))


Enable autodoc (and napoleon if you want):

Find the extensions = [] line and change it to:

extensions = [
    "sphinx.ext.autodoc",
]


(If later you use Google/NumPy style docstrings, you can add "sphinx.ext.napoleon".)

Save.

5️⃣ Create API .rst files for your services

In docs/, create a file for bookings first, e.g. api_bookings.rst:

Bookings Service API
====================

.. automodule:: bookings_service.app
   :members:
   :undoc-members:
   :show-inheritance:


Later you can also add:

api_users.rst for users_service.app

api_rooms.rst for rooms_service.app

api_reviews.rst for reviews_service.app

Example api_users.rst:

Users Service API
=================

.. automodule:: users_service.app
   :members:
   :undoc-members:
   :show-inheritance:

6️⃣ Include them in index.rst

Open docs/index.rst and make sure it has a toctree like this:

Welcome to smartmeetingroom’s documentation!
============================================

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api_bookings
   api_users
   api_rooms
   api_reviews


You can keep or remove the default sections Sphinx generated.

7️⃣ Build the HTML docs (what your instructor wants to see)

From inside docs/ (still in PowerShell):

.\make.bat html


This builds the HTML into:

docs\_build\html\


Open:

docs\_build\html\index.html


in your browser → this is the HTML documentation they want to see (and screenshot for the report).






What to do next (for Sphinx)

In docs/api_bookings.rst:

Bookings Service API
====================

.. automodule:: bookings_service.app
   :members:
   :undoc-members:
   :show-inheritance:


In docs/index.rst, include api_bookings in the toctree.

From docs/ run:

.\make.bat html



Now in Sphinx you can also create (or extend) docs/api_bookings.rst with:

Bookings Models
===============

.. automodule:: bookings_service.models
   :members:
   :undoc-members:
   :show-inheritance:





   For Sphinx, if you want to expose these too, you can add to api_bookings.rst:

Bookings Schemas
================

.. automodule:: bookings_service.schemas
   :members:
   :undoc-members:
   :show-inheritance:


For Sphinx, you can also create something like docs/db_connection.rst:

Database Connection
===================

.. automodule:: common.db.connection
   :members:
   :undoc-members:
   :show-inheritance:



DOCKER:

Run:

docker compose build
docker compose up


Requirements:

python -m pip install -r requirements.txt





for tests
run pytest
