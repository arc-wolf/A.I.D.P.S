import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def client():
    """Flask test client fixture"""
    from main import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_scanner():
    """Mock network scanner"""
    with pytest.MonkeyPatch().context() as m:
        m.setattr("backend.discovery.network_scan.NetworkScanner.arp_scan", 
                  lambda self, subnet, timeout: [{'ip': '192.168.1.1', 'mac': 'aa:bb:cc:dd:ee:ff'}])
        yield

@pytest.fixture
def sample_device():
    """Sample device data"""
    return {
        'ip': '192.168.1.100',
        'mac': 'aa:bb:cc:dd:ee:ff',
        'hostname': 'test-linux',
        'os_type': 'linux',
        'ssh_enabled': True
    }

