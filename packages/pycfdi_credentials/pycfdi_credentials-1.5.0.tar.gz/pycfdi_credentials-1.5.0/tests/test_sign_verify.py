import pytest
from hypothesis import assume, given, settings, HealthCheck
from hypothesis import strategies as st

from pycfdi_credentials import Certificate, PrivateKey
from pycfdi_credentials.utils import read_file

ALGORITHMS = ["sha256", "sha1", "sha512"]

CERTIFICATES = (
    "FIEL_AAA010101AAA",
    "CSD01_AAA010101AAA",
)


@given(content=st.text(min_size=0, max_size=100))
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.parametrize("cert_data", CERTIFICATES, indirect=True)
@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_sign_verify(cert_data: dict, algorithm: str, content: str):
    """
    Test sign method can sign and verify the signature
    """
    private_key = cert_data["private_key"]
    certificate = cert_data["certificate"]
    content_bytes = content.encode("utf-8")
    signature = private_key.sign(content_bytes, algorithm)
    is_valid = certificate.verify(signature, content_bytes, algorithm)
    assert is_valid is True


@given(content=st.text(min_size=0, max_size=100), fake_content=st.text(min_size=0, max_size=100))
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.parametrize("cert_data", CERTIFICATES, indirect=True)
@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_sign_verify_wrong(cert_data: dict, algorithm: str, content: str, fake_content: str):
    """
    Test sign method can sign and verify the signature
    """
    assume(content != fake_content)
    private_key = cert_data["private_key"]
    certificate = cert_data["certificate"]
    content_bytes = content.encode("utf-8")
    signature = private_key.sign(content_bytes, algorithm)
    fake_content_bytes = fake_content.encode("utf-8")
    is_valid = certificate.verify(signature, fake_content_bytes, algorithm)
    assert is_valid is False


@given(content=st.text(min_size=0, max_size=100))
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.parametrize("cert_data", CERTIFICATES, indirect=True)
@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_sign_consistency(cert_data: dict, algorithm: str, content: str):
    private_key = cert_data["private_key"]
    content_bytes = content.encode("utf-8")
    signature = private_key.sign(content_bytes, algorithm)
    signature_2 = private_key.sign(content_bytes, algorithm)
    assert signature == signature_2
