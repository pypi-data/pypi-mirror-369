import datetime
import os
from datetime import timedelta, timezone

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.extensions import SubjectAlternativeName
from typing import List, Optional, Tuple


def load_ca_cert(ca_cert: str, ca_key: str) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """Loads an existing CA certificate and key from files."""
    with open(ca_cert, "rb") as cert_file, open(ca_key, "rb") as key_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        key = serialization.load_pem_private_key(key_file.read(), None, default_backend())
    return key, cert


def generate_ca_cert(subject: str) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """Generates a self-signed CA certificate."""
    ca_subject = x509.Name([x509.NameAttribute(x509.OID_COMMON_NAME, subject)])
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    cert = x509.CertificateBuilder()
    cert = cert.subject_name(ca_subject)
    cert = cert.issuer_name(ca_subject)
    cert = cert.public_key(key.public_key())
    cert = cert.serial_number(x509.random_serial_number())
    cert = cert.not_valid_before(datetime.datetime.now(timezone.utc))
    cert = cert.not_valid_after(datetime.datetime.now(timezone.utc) + timedelta(days=365))
    cert = cert.add_extension(SubjectAlternativeName([x509.DNSName("ZTP CA")]), critical=False)
    cert = cert.sign(key, hashes.SHA256(), default_backend())
    return key, cert


def generate_server_cert(
    ca_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    subject: str,
    sans: Optional[List[str]] = None,
) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """Generates a server certificate signed by the CA."""

    server_subject = x509.Name(
        [
            x509.NameAttribute(x509.OID_COMMON_NAME, subject),
        ]
    )
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    cert = x509.CertificateBuilder()
    cert = cert.subject_name(server_subject)
    cert = cert.issuer_name(ca_cert.subject)
    cert = cert.public_key(key.public_key())
    cert = cert.serial_number(x509.random_serial_number())
    cert = cert.not_valid_before(datetime.datetime.now(timezone.utc))
    cert = cert.not_valid_after(datetime.datetime.now(timezone.utc) + timedelta(days=365))
    # Build Subject Alternative Names: default to CN if not provided
    if sans is None:
        alt_names = [server_subject.get_attributes_for_oid(x509.OID_COMMON_NAME)[0].value]
    else:
        alt_names = sans
    cert = cert.add_extension(SubjectAlternativeName([x509.DNSName(name) for name in alt_names]), critical=False)
    cert = cert.sign(ca_key, hashes.SHA256(), default_backend())
    return key, cert


def create_pem_file(key, cert, filename):
    """Creates a PEM file containing the private key and certificate."""
    pem_data = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ) + cert.public_bytes(
        encoding=serialization.Encoding.PEM,
    )
    with open(filename, "wb") as pem_file:
        pem_file.write(pem_data)


def create_key_file(key, filename, directory):
    """Creates a .key file containing the private key."""
    key_data = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(os.path.join(directory, f"{filename}.key"), "wb") as key_file:
        key_file.write(key_data)


def create_cert_file(cert, filename, directory):
    """Creates a .crt file containing the certificate."""
    crt_data = cert.public_bytes(
        encoding=serialization.Encoding.PEM,
    )
    with open(os.path.join(directory, f"{filename}.crt"), "wb") as crt_file:
        crt_file.write(crt_data)
