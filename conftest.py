# conftest.py
import pytest
from django.contrib.auth.models import User
from django.test import Client

@pytest.fixture
def staff_client(db):
    user = User.objects.create_user(username='admin', password='pass', is_staff=True)
    client = Client()
    client.login(username='admin', password='pass')
    return client