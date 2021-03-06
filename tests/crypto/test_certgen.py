#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2020 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
""" Tests for certificate management (generating certificate, CSR, validating certificate, chains)
"""
from os import path
from typing import List

import pytest

from spsdk.crypto import generate_rsa_private_key, generate_rsa_public_key, save_rsa_private_key, \
    save_rsa_public_key, validate_ca_flag_in_cert_chain, Certificate, Encoding
from spsdk.crypto import _get_encoding_type, load_private_key, load_certificate, load_public_key
from spsdk.crypto import validate_certificate_chain, validate_certificate, is_ca_flag_set
from spsdk.crypto import generate_certificate, save_crypto_item, x509


def gen_name_struct(name: str) -> x509.Name:
    """Set the issuer/subject distinguished name.

    :param name: name of issuer/subject
    :return: ordered list of attributes of certificate
    """
    return x509.Name([
        x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, "CZ"),
        x509.NameAttribute(x509.oid.NameOID.STATE_OR_PROVINCE_NAME, "RpR"),
        x509.NameAttribute(x509.oid.NameOID.LOCALITY_NAME, "1maje"),
        x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, name)
    ])


def get_certificate(data_dir, cert_file_name: str) -> Certificate:
    cert = load_certificate(path.join(data_dir, cert_file_name))
    return cert


def get_certificates(data_dir, cert_file_names: List[str]) -> List[Certificate]:
    cert_list = [
        get_certificate(data_dir, cert_name)
        for cert_name in cert_file_names
    ]
    return cert_list


def keys_generation(data_dir):
    priv_key = generate_rsa_private_key()
    pub_key = generate_rsa_public_key(priv_key)
    save_rsa_private_key(priv_key, path.join(data_dir, "priv.pem"))
    save_rsa_public_key(pub_key, path.join(data_dir, "pub.pem"))


@pytest.mark.parametrize(
    "file_name, expect_cer",
    [
        ("priv.pem", False),
        ("ca.pem", True),
        ("pub.pem", False),
        ("CA1_key.der", False),
        ("ca1_crt.der", True),
        ("ca_key.pem", False),
        ("NXPEnterpriseCA4.crt", True),
        ("NXPInternalPolicyCAG2.crt", True),
        ("NXPROOTCAG2.crt", True),
    ]
)
def test_is_cert(data_dir, file_name, expect_cer):
    cert_path = path.join(data_dir, file_name)
    result = bool(load_certificate(cert_path))
    assert result is expect_cer


@pytest.mark.parametrize(
    "file_name, password, expect_priv_key",
    [
        ('CA1_sha256_2048_65537_v3_ca_key.pem', b'test', True),
        ('ca.pem', b'test', False)
    ]
)
def test_is_key_priv(data_dir, file_name, password, expect_priv_key):
    key_path = path.join(data_dir, file_name)
    result = bool(load_private_key(key_path, password))
    assert result is expect_priv_key


@pytest.mark.parametrize(
    "file_name,  expect_pub_key",
    [
        ("ca.pem", False),
        ("pub.pem", True),
        ("priv.pem", False),
        ("CA1_key.der", False),
        ("ca1_crt.der", False),
        ("ca_key.pem", False),
        ("NXPEnterpriseCA4.crt", False),
        ("NXPInternalPolicyCAG2.crt", False),
        ("NXPROOTCAG2.crt", False)
    ]
)
def test_is_key_pub(data_dir, file_name, expect_pub_key):
    key_path = path.join(data_dir, file_name)
    result = bool(load_public_key(key_path))
    assert result is expect_pub_key


@pytest.mark.parametrize(
    "file_name, expected_encoding",
    [
        ("ca.pem", Encoding.PEM),
        ("pub.pem", Encoding.PEM),
        ("priv.pem", Encoding.PEM),
        ("CA1_key.der", Encoding.DER),
        ("ca1_crt.der", Encoding.DER),
        ("ca_key.pem", Encoding.PEM),
        ("NXPEnterpriseCA4.crt", Encoding.PEM),
        ("NXPInternalPolicyCAG2.crt", Encoding.PEM),
        ("NXPROOTCAG2.crt", Encoding.PEM)
    ]
)
def test_get_encoding_type(data_dir, file_name, expected_encoding):
    file = path.join(data_dir, file_name)
    assert _get_encoding_type(file) == expected_encoding


def test_validate_cert(data_dir):
    nxp_ca = get_certificate(data_dir, "NXPROOTCAG2.crt")
    nxp_international = get_certificate(data_dir, "NXPInternalPolicyCAG2.crt")
    nxp_enterprise = get_certificate(data_dir, "NXPEnterpriseCA4.crt")
    satyr = get_certificate(data_dir, "satyr.crt")

    assert validate_certificate(nxp_enterprise, nxp_international)
    assert validate_certificate(nxp_international, nxp_ca)
    assert validate_certificate(satyr, nxp_enterprise)


def test_validate_invalid_cert(data_dir):
    nxp_ca = get_certificate(data_dir, "NXPROOTCAG2.crt")
    nxp_international = get_certificate(data_dir, "NXPInternalPolicyCAG2.crt")
    nxp_enterprise = get_certificate(data_dir, "NXPEnterpriseCA4.crt")
    satyr = get_certificate(data_dir, "satyr.crt")

    assert not validate_certificate(satyr, nxp_ca)
    assert not validate_certificate(nxp_enterprise, nxp_ca)
    assert not validate_certificate(satyr, nxp_international)


def test_certificate_chain_verification(data_dir):
    chain = ["satyr.crt", "NXPEnterpriseCA4.crt", "NXPInternalPolicyCAG2.crt", "NXPROOTCAG2.crt"]
    chain_cert = [get_certificate(data_dir, file_name) for file_name in chain if file_name.startswith('NXP')]
    assert all(validate_certificate_chain(chain_cert))

    list_cert_files = ["img.pem", "srk.pem", "ca.pem"]
    chain_prov = get_certificates(data_dir, list_cert_files)
    assert all(validate_certificate_chain(chain_prov))


def test_certificate_chain_verification_error(data_dir):
    chain = ["ca.pem", "NXPInternalPolicyCAG2.crt", "NXPEnterpriseCA4.crt", "NXPROOTCAG2.crt"]
    chain_cert = get_certificates(data_dir, chain)
    assert not all(validate_certificate_chain(chain_cert))

    list_cert_files = ["satyr.crt", "img.pem", "srk.pem"]
    chain_prov = get_certificates(data_dir, list_cert_files)
    assert not all(validate_certificate_chain(chain_prov))


def test_is_ca_flag_set(data_dir):
    ca_certificate = get_certificate(data_dir, "ca.pem")
    assert is_ca_flag_set(ca_certificate)
    no_ca_certificate = get_certificate(data_dir, "img.pem")
    assert not is_ca_flag_set(no_ca_certificate)


def test_validate_ca_flag_in_cert_chain(data_dir):
    chain = ["ca.pem", "srk.pem"]
    chain_cert = get_certificates(data_dir, chain)
    assert validate_ca_flag_in_cert_chain(chain_cert)
    invalid_chain = ["img.pem", "srk.pem"]
    chain_cert_invalid = get_certificates(data_dir, invalid_chain)
    assert not validate_ca_flag_in_cert_chain(chain_cert_invalid)


def test_certificate_generation(tmpdir):
    ca_priv_key = generate_rsa_private_key()
    save_rsa_private_key(ca_priv_key, path.join(tmpdir, "ca_private_key.pem"))
    ca_pub_key = generate_rsa_public_key(ca_priv_key)
    save_rsa_public_key(ca_pub_key, path.join(tmpdir, "ca_pub_key.pem"))
    assert path.isfile(path.join(tmpdir, "ca_private_key.pem"))
    assert path.isfile(path.join(tmpdir, "ca_pub_key.pem"))

    subject = issuer = gen_name_struct("highest")
    ca_cert = generate_certificate(subject, issuer, ca_pub_key, ca_priv_key, if_ca=True)
    save_crypto_item(ca_cert, path.join(tmpdir, "ca_cert.pem"))
    assert path.isfile(path.join(tmpdir, "ca_cert.pem"))

    srk_priv_key = generate_rsa_private_key()
    save_rsa_private_key(srk_priv_key, path.join(tmpdir, "srk_priv_key.pem"))
    assert path.isfile(path.join(tmpdir, "srk_priv_key.pem"))
    srk_pub_key = generate_rsa_public_key(srk_priv_key)
    save_rsa_public_key(srk_pub_key, path.join(tmpdir, "srk_pub_key.pem"))
    assert path.isfile(path.join(tmpdir, "srk_pub_key.pem"))
    srk_subject = gen_name_struct('srk')
    srk_cert = generate_certificate(srk_subject, issuer, srk_pub_key, ca_priv_key, if_ca=False)
    save_crypto_item(srk_cert, path.join(tmpdir, "srk1.pem"))
    assert path.isfile(path.join(tmpdir, "srk1.pem"))
