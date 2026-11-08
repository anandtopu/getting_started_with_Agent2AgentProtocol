"""Generate a private lab CA and short-lived TLS identities; never commit secrets."""

import ipaddress
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from common.config import PORTS, ROOT


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    directory.parent.chmod(0o700)
    now = datetime.now(timezone.utc)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Maplewood lab CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()), critical=False
        )
        .add_extension(
            x509.KeyUsage(False, False, False, False, False, True, True, False, False),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    (directory / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    for identity in (*PORTS, "keycloak", "client"):
        leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        leaf_name = x509.Name(
            [
                x509.NameAttribute(
                    NameOID.COMMON_NAME,
                    "maplewood-concierge" if identity == "client" else identity,
                )
            ]
        )
        builder = (
            x509.CertificateBuilder()
            .subject_name(leaf_name)
            .issuer_name(name)
            .public_key(leaf_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=7))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()), critical=False
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()), critical=False
            )
            .add_extension(
                x509.KeyUsage(True, False, True, False, False, False, False, False, False),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        ExtendedKeyUsageOID.CLIENT_AUTH
                        if identity == "client"
                        else ExtendedKeyUsageOID.SERVER_AUTH
                    ]
                ),
                critical=False,
            )
        )
        if identity != "client":
            builder = builder.add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName(n) for n in ("localhost", identity)]
                    + [x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
                ),
                critical=False,
            )
        (directory / (identity + ".pem")).write_bytes(
            builder.sign(key, hashes.SHA256()).public_bytes(serialization.Encoding.PEM)
        )
        private_path = directory / (identity + "-key.pem")
        private_path.write_bytes(
            leaf_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        # Parent secrets directory is owner-only. Individually mounted files must
        # be readable by the unprivileged container UID, which differs on hosts.
        private_path.chmod(0o644)
    # CA private key is intentionally not retained; re-run to issue a new lab trust domain.


if __name__ == "__main__":
    generate(ROOT / "deploy/secrets/tls")
    print("Created lab TLS certificates under ignored deploy/secrets/tls (valid seven days).")
