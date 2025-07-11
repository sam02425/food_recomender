import os
import tempfile
import pytest
from src.agents.older.Face_Ag import EnhancedFaceRecognitionAgent

@pytest.fixture
def agent():
    # Use a temp directory for face images
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = EnhancedFaceRecognitionAgent(
            customer_data_path=os.path.join(tmpdir, 'customers.csv'),
            face_images_dir=tmpdir
        )
        yield agent


def test_authenticate_new_customer(agent):
    # Simulate a new customer with random image bytes
    fake_image = b'\x89PNG\r\n\x1a\n' + os.urandom(1024)
    result = agent.authenticate_customer(fake_image)
    assert isinstance(result, dict)
    assert 'authenticated' in result
    assert result['authenticated'] is False or result['authenticated'] is True
    assert 'timestamp' in result
    # If new customer, should have new_customer True
    if not result['authenticated']:
        assert result.get('new_customer', False) is True


def test_authenticate_error_handling(agent):
    # Pass invalid data to trigger error
    result = agent.authenticate_customer(None)
    assert isinstance(result, dict)
    assert result['authenticated'] is False
    assert 'error' in result