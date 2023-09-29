"""Creates the flask client for testing purposes"""
import pytest
from main import app


@pytest.fixture
def fixture_client(name="test_client"):
    """Configures the app for testing

    Sets app config variable ``TESTING`` to ``True``

    :return: App for testing
    """

    # app.config['TESTING'] = True
    test_client = app.test_client()

    yield test_client
