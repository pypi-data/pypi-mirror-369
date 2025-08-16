from datetime import datetime
from typing import Any, Dict

import pytest

from pycfdi_credentials import Certificate, Subject
from pycfdi_credentials.utils import read_file

CERTIFICATES = (
    {
        "name": "FIEL_AAA010101AAA",
        "serial_number": "30001000000300023685",
        "subject": Subject(
            name="ACCEM SERVICIOS EMPRESARIALES SC",
            country_code="MX",
            email="FactElect@sat.gob.mx",
            rfc="AAA010101AAA",
            serial_number_used=" / HEGT761003MDFRNN09",
            rfc_issuer="HEGT7610034S2",
        ),
        "valid_not_before": datetime.fromisoformat("2017-05-16T23:29:17"),
        "valid_not_after": datetime.fromisoformat("2021-05-15T23:29:17"),
        "cert_type": Certificate.CertType.FIEL,
    },
    {
        "name": "CSD01_AAA010101AAA",
        "serial_number": "30001000000300023708",
        "subject": Subject(
            name="ACCEM SERVICIOS EMPRESARIALES SC",
            rfc="AAA010101AAA",
            serial_number_used=" / HEGT761003MDFRNN09",
            rfc_issuer="HEGT7610034S2",
        ),
        "valid_not_before": datetime.fromisoformat("2017-05-18T03:54:56"),
        "valid_not_after": datetime.fromisoformat("2021-05-18T03:54:56"),
        "cert_type": Certificate.CertType.CSD,
    },
)


@pytest.mark.parametrize("cert_info", CERTIFICATES)
def test_get_info(cert_info: Dict[str, Any]):
    cert_name = cert_info["name"]
    certificate = Certificate(read_file(f"tests/assets/{cert_name}/certificate.cer"))
    assert certificate.serial_number == cert_info["serial_number"]
    assert certificate.subject == cert_info["subject"]
    assert certificate.valid_not_before == cert_info["valid_not_before"]
    assert certificate.valid_not_after == cert_info["valid_not_after"]
    assert certificate.cert_type == cert_info["cert_type"]
    assert certificate.pub_key == read_file(
        f"tests/assets/{cert_name}/certificate.cer.pem.pubkey.pem"
    )


@pytest.mark.parametrize("cert_info", CERTIFICATES)
def test_to_pem(cert_info: Dict[str, Any]):
    cert_name = cert_info["name"]
    certificate = Certificate(read_file(f"tests/assets/{cert_name}/certificate.cer"))
    pem_original = read_file(f"tests/assets/{cert_name}/certificate.cer.pem")
    pem_generated = certificate.to_pem()
    assert pem_generated == pem_original


@pytest.mark.parametrize("cert_info", CERTIFICATES)
def test_to_der(cert_info: Dict[str, Any]):
    cert_name = cert_info["name"]
    certificate_original = read_file(f"tests/assets/{cert_name}/certificate.cer")
    certificate = Certificate(certificate_original)
    assert certificate_original == certificate.to_der()


@pytest.mark.parametrize("cert_info", CERTIFICATES)
def test_from_pem(cert_info: Dict[str, Any]):
    cert_name = cert_info["name"]
    pem_original = read_file(f"tests/assets/{cert_name}/certificate.cer.pem")
    certificate = Certificate(pem_original)
    assert pem_original == certificate.to_pem()
