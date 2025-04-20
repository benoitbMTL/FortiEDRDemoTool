import requests
import ssl
import urllib3
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from datetime import timezone
import certifi
import colorama

colorama.init(autoreset=True)

API_URL = "https://mb-api.abuse.ch/api/v1/"
DEBUG = True

def fetch_cert_info():
    verified = True
    try:
        if DEBUG:
            print("[INFO] Trying secure connection (verify=True)...")
        response = requests.get(API_URL, timeout=10, verify=certifi.where(), stream=True)
        sock = response.raw._connection.sock
    except Exception:
        verified = False
        print(colorama.Fore.RED + "[ERROR] SSL verification failed. Retrying without verification...\n")
        response = requests.get(API_URL, timeout=10, verify=False, stream=True)
        sock = response.raw._connection.sock

    # Récupération et parsing du certificat
    der_cert = sock.getpeercert(binary_form=True)
    cert = x509.load_der_x509_certificate(der_cert, default_backend())

    # Extraction des champs
    issuer = cert.issuer
    subject = cert.subject

    issuer_cn = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.COMMON_NAME) else "N/A"
    issuer_o  = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else "N/A"
    subject_cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COMMON_NAME) else "N/A"

    # Affichage
    print("\n=== Certificate Information ===")
    print(f"{'🔒 Verified':<17}: {'Yes' if verified else 'No'}")
    print(f"{'Common Name (CN)':<17}: {issuer_cn}")
    print(f"{'Organization (O)':<17}: {issuer_o}")
    print(f"{'Subject CN':<17}: {subject_cn}")
    print(f"{'Valid From':<17}: {cert.not_valid_before_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'Valid Until':<17}: {cert.not_valid_after_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'Serial Number':<17}: {cert.serial_number}")

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    fetch_cert_info()
