"""TLS configuration shared by servers and clients. Verification is never disabled."""

import os
import ssl
from pathlib import Path


def server_options():
    certificate, key = os.environ.get("MAPLEWOOD_TLS_CERT"), os.environ.get("MAPLEWOOD_TLS_KEY")
    if bool(certificate) != bool(key):
        raise ValueError("TLS requires both a certificate and private key")
    return (
        {"ssl_certfile": certificate, "ssl_keyfile": key, "ssl_version": ssl.PROTOCOL_TLS_SERVER}
        if certificate
        else {}
    )


def client_context():
    return ssl.create_default_context(cafile=os.environ.get("MAPLEWOOD_TLS_CA"))


def grpc_credentials(server=False):
    import grpc

    ca = os.environ.get("MAPLEWOOD_TLS_CA")
    if not ca:
        return None
    root = Path(ca).read_bytes()
    prefix = "MAPLEWOOD_TLS_" if server else "MAPLEWOOD_CLIENT_"
    certificate = Path(os.environ[prefix + "CERT"]).read_bytes()
    key = Path(os.environ[prefix + "KEY"]).read_bytes()
    if server:
        return grpc.ssl_server_credentials(
            [(key, certificate)], root_certificates=root, require_client_auth=True
        )
    return grpc.ssl_channel_credentials(root, key, certificate)
