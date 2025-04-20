import requests
import certifi
import urllib3
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID

API_URL = "https://mb-api.abuse.ch/api/v1/"

def check_ssl_inspection(domain: str):
    """Connects to the target domain and inspects the SSL certificate to determine if SSL inspection is active."""
    result = {
        "verified": False,
        "issuer_cn": "Unknown",
        "issuer_o": "Unknown",
        "subject_cn": "Unknown",
        "not_before": "N/A",
        "not_after": "N/A",
        "serial": "N/A",
        "ssl_inspection": "Unknown"
    }

    try:
        # Try to connect securely with verification
        response = requests.get(API_URL, timeout=10, verify=certifi.where(), stream=True)
        result["verified"] = True
    except Exception:
        # If it fails, retry without verification
        response = requests.get(API_URL, timeout=10, verify=False, stream=True)

    try:
        # Extract certificate in DER format
        sock = response.raw._connection.sock
        der_cert = sock.getpeercert(binary_form=True)

        # Parse certificate using cryptography
        cert = x509.load_der_x509_certificate(der_cert, default_backend())
        issuer = cert.issuer
        subject = cert.subject

        # Extract standard fields
        result["issuer_cn"] = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.COMMON_NAME) else "N/A"
        result["issuer_o"] = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else "N/A"
        result["subject_cn"] = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COMMON_NAME) else "N/A"
        result["not_before"] = cert.not_valid_before_utc.strftime('%Y-%m-%d %H:%M:%S')
        result["not_after"] = cert.not_valid_after_utc.strftime('%Y-%m-%d %H:%M:%S')
        result["serial"] = str(cert.serial_number)

        # Determine if inspection is active
        if "Fortinet" in result["issuer_o"] or "Fortinet" in result["issuer_cn"]:
            result["ssl_inspection"] = "enabled"
        else:
            result["ssl_inspection"] = "disabled"

    except Exception as e:
        result["ssl_inspection"] = "Unknown"

    return result
