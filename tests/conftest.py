import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest

from bookings_service.app import app as bookings_app, get_db as get_bookings_db
from bookings_service.models import Booking

from reviews_service.app import app as reviews_app, get_db as get_reviews_db
from reviews_service.models import Review


@pytest.fixture
def bookings_client():
    """
    Provide a Flask test client for the Bookings service.

    Before yielding the client, this fixture clears the bookings table
    to ensure that each test runs with a clean database state and does
    not depend on data created by other tests.
    """
    bookings_app.config["TESTING"] = True
    with bookings_app.test_client() as client:
        db = get_bookings_db()
        db.query(Booking).delete()
        db.commit()
        db.close()
        yield client


@pytest.fixture
def reviews_client():
    """
    Provide a Flask test client for the Reviews service.

    The fixture truncates the reviews table before each test, so that
    tests are isolated and can reliably assert on the data they create
    during execution.
    """
    reviews_app.config["TESTING"] = True
    with reviews_app.test_client() as client:
        db = get_reviews_db()
        db.query(Review).delete()
        db.commit()
        db.close()
        yield client
