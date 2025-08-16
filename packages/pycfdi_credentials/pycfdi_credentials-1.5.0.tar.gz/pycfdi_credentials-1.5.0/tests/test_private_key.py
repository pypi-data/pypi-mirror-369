import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pycfdi_credentials import PrivateKey
from pycfdi_credentials.private_key import PrivateKeyException
from pycfdi_credentials.utils import pem_to_der, read_file

CERTIFICATES = (
    "FIEL_AAA010101AAA",
    "CSD01_AAA010101AAA",
)


@pytest.mark.parametrize("cert_name", CERTIFICATES)
def test_load_der(cert_name: str):
    der_original = read_file(f"tests/assets/{cert_name}/private_key.key")
    private_key = PrivateKey(der_original, passphrase=b"12345678a")
    assert private_key.private_key is not None


@pytest.mark.parametrize("cert_name", CERTIFICATES)
def test_to_pem_traditional(cert_name: str):
    der_original = read_file(f"tests/assets/{cert_name}/private_key.key")
    private_key = PrivateKey(der_original, passphrase=b"12345678a")
    pem_original = read_file(f"tests/assets/{cert_name}/private_key.key.traditional")
    pem_generated = private_key.to_pem()
    assert pem_generated == pem_original


@given(new_pass=st.text())
@pytest.mark.parametrize("cert_name", CERTIFICATES)
def test_to_pem_encrypted(cert_name: str, new_pass: str):
    assume(new_pass != "12345678a")
    new_pass_bytes = new_pass.encode()
    pem_original = read_file(f"tests/assets/{cert_name}/private_key.key.traditional")
    private_key_unencrypted = PrivateKey(pem_original)
    pem_encrypted = private_key_unencrypted.to_pem(passphrase=new_pass_bytes)
    private_key = PrivateKey(pem_encrypted, passphrase=new_pass_bytes)
    assert private_key.is_equivalent(private_key_unencrypted)


@given(new_pass=st.text())
@pytest.mark.parametrize("cert_name", CERTIFICATES)
def test_to_der_encrypted(cert_name: str, new_pass: str):
    assume(new_pass != "12345678a")
    new_pass_bytes = new_pass.encode()
    der_original = read_file(f"tests/assets/{cert_name}/private_key.key")
    private_key = PrivateKey(der_original, passphrase=b"12345678a")
    pem_encrypted = private_key.to_pem(passphrase=new_pass_bytes)
    der_encrypted = pem_to_der(pem_encrypted)
    private_key_2 = PrivateKey(der_encrypted, passphrase=new_pass_bytes)
    assert private_key.is_equivalent(private_key_2)


@given(new_pass=st.text(), wrong_pass=st.text())
@pytest.mark.parametrize("cert_name", CERTIFICATES)
def test_no_open_wrong_password(cert_name: str, new_pass: str, wrong_pass: str):
    assume(new_pass != wrong_pass)
    assume(new_pass != "")
    assume(wrong_pass != "")
    new_pass_bytes = new_pass.encode()
    wrong_pass_bytes = wrong_pass.encode()
    der_original = read_file(f"tests/assets/{cert_name}/private_key.key")
    private_key = PrivateKey(der_original, passphrase=b"12345678a")
    pem_encrypted = private_key.to_pem(passphrase=new_pass_bytes)
    with pytest.raises(PrivateKeyException):
        PrivateKey(pem_encrypted, passphrase=wrong_pass_bytes)
