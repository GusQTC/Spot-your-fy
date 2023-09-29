"""Run the tests as root"""
from tests_flask import test_client


def test_landing(test_client):
    """Check index page loads"""
    landing = test_client.get("/")
    assert landing.status_code == 200
