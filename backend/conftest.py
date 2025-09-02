"""
Global pytest configuration and fixtures for myunsejeomju backend tests.
"""
import os
import pytest
import django
from django.conf import settings
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management import call_command
from django.db import transaction


def pytest_configure():
    """
    Configure Django settings for pytest.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myunsejeomju.settings')
    django.setup()






@pytest.fixture
def transactional_db(db):
    """
    Fixture that provides database access within a transaction.
    The transaction is rolled back after the test.
    """
    return db


@pytest.fixture
def non_atomic_db():
    """
    Fixture that provides database access without transaction management.
    Useful for testing transaction-based code.
    """
    pass