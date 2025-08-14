# -*- coding: utf-8 -*-
import pytest

import windows.crypto
import windows.generated_def as gdef
import windows.crypto.generation

from .pfwtest import *

pytestmark = pytest.mark.usefixtures('check_for_gc_garbage')

## Cert info:
#  Name: PythonForWindowsTest
#  Serial: '1b 8e 94 cb 0b 3e eb b6 41 39 f3 c9 09 b1 6b 46'

TEST_CERT = b"""
MIIBwTCCASqgAwIBAgIQG46Uyws+67ZBOfPJCbFrRjANBgkqhkiG9w0BAQsFADAfMR0wGwYDVQQD
ExRQeXRob25Gb3JXaW5kb3dzVGVzdDAeFw0xNzA0MTIxNDM5MjNaFw0xODA0MTIyMDM5MjNaMB8x
HTAbBgNVBAMTFFB5dGhvbkZvcldpbmRvd3NUZXN0MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQCRHwC/sRfXh5pc4poc85aidrudbPdya+0OeonQlf1JQ1ekf7KSfADV5FLkSQu2BzgBK9DIWTGX
XknBJIzZF03UZsVg5D67V2mnSClXucc0cGFcK4pDDt0tHeabA2GPinVe7Z6qDT4ZxPR8lKaXDdV2
Pg2hTdcGSpqaltHxph7G/QIDAQABMA0GCSqGSIb3DQEBCwUAA4GBACcQFdOlVjYICOIyAXowQaEN
qcLpN1iWoL9UijNhTY37+U5+ycFT8QksT3Xmh9lEIqXMh121uViy2P/3p+Ek31AN9bB+BhWIM6PQ
gy+ApYDdSwTtWFARSrMqk7rRHUveYEfMw72yaOWDxCzcopEuADKrrYEute4CzZuXF9PbbgK6"""

## Cert info:
#  Name: фжющдфя
#  Serial: '17 f7 d2 1b 78 01 b5 9d 43 4a 4e 54 2a 1a 30 4b'

UNICODE_CERT_NAME = u'\u0444\u0436\u044e\u0449\u0434\u0444\u044f' # фжющдфя

UNICODE_TEST_CERT = b"""
MIIDAjCCAeqgAwIBAgIQF/fSG3gBtZ1DSk5UKhowSzANBgkqhkiG9w0BAQsFADAZMRcwFQYDVQQD
DA7RhNC20Y7RidC00YTRjzAeFw0yMDA3MTcxMDA4MjdaFw0yMTA3MTcxMDI4MjdaMBkxFzAVBgNV
BAMMDtGE0LbRjtGJ0LTRhNGPMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7cX6C0O1
UQJa+e6z7wZVGV2/xdbZoir4oWglqv3Ax95x0sERgdjTj9ZmCyvgyzwSxi80Q8N6TUi0tUS1o0ig
SpjF97lD1wVZlb+mVW6vi16G5JUGH2WBtIZ8j4hW3rTBg7R8V9I2VXw3u/36udnWgkKvEOQPSicw
5T1FrJeAQniRJHjSo20yh5jx7d1O4gtJBJEUjEkW8YFq9g7c/ThwWYv9p20q/Du2XUC2M9OQOdT4
6rJUkb5btXPNWgdkMz9VCVwG0VTbJicEkCwRnBngbTC77IodN3pD+hoJk/9ecWOVMlrYJDQ2w5rL
ZnhN7akhVCX8b+UWoXw0fUV8yTtlaQIDAQABo0YwRDAOBgNVHQ8BAf8EBAMCB4AwEwYDVR0lBAww
CgYIKwYBBQUHAwMwHQYDVR0OBBYEFHwVaUqnE2RvcX/tkioXZS5MJKN+MA0GCSqGSIb3DQEBCwUA
A4IBAQAdqc5lFyatDq+MYg08MedFd1DSgaR2ZbMXcOxvc7WPFH6RnW/w1kX9nWeHWaMO6tfLPfbk
BPxbCYYEwVPEguQ+aV94RDOJgMXeqRnSguhdGD4QO8M08Cd8HhykXX0gbSjKR10i/b98oHqyoPmR
Cne9Uuv9W6DTMTyZM4er8MLIa/UzfpVb0Edxa9rYqYYixRnX8/9cTx83g4XSxA0ghwftcpwjijMD
H0umvThot/cF/neBIX69JxP6zT951ce5gmo/hYXAt/1RnDULCJtsKaIU7hOIOxilVxjV4rHjybw5
nPYyGwKCd0BAEG5tpTXlCeGbE5aw85o4mASH/Xp5DSMx"""


TEST_PFX_PASSWORD = "TestPassword"

TEST_PFX = b"""
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
"""

@pytest.fixture()
def rawcert():
    return b64decode(TEST_CERT)

@pytest.fixture()
def raw_unicodecert():
    return b64decode(UNICODE_TEST_CERT)

@pytest.fixture()
def rawpfx():
    return b64decode(TEST_PFX)

PFW_TEST_TMP_KEY_CONTAINER = "PythonForWindowsTMPContainerTest"
RANDOM_CERTIF_NAME = "PythonForWindowsGeneratedRandomCertifTest"
RANDOM_PFX_PASSWORD = "PythonForWindowsGeneratedRandomPFXPassword"

@pytest.fixture()
def randomkeypair(keysize=1024):
    r"""Generate a cert / pfx. Based on samples\crypto\encryption_demo.py"""
    cert_store = windows.crypto.CertificateStore.new_in_memory()
    # Create a TMP context that will hold our newly generated key-pair
    with windows.crypto.CryptContext(PFW_TEST_TMP_KEY_CONTAINER, None, gdef.PROV_RSA_FULL, 0, retrycreate=True) as ctx:
        key = gdef.HCRYPTKEY()
        keysize_flags = keysize << 16
        # Generate a key-pair that is exportable
        windows.winproxy.CryptGenKey(ctx, gdef.AT_KEYEXCHANGE, gdef.CRYPT_EXPORTABLE | keysize_flags, key)
        # It does NOT destroy the key-pair from the container,
        # It only release the key handle
        # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379918(v=vs.85).aspx
        windows.winproxy.CryptDestroyKey(key)

    # Descrption of the key-container that will be used to generate the certificate
    KeyProvInfo = gdef.CRYPT_KEY_PROV_INFO()
    KeyProvInfo.pwszContainerName = PFW_TEST_TMP_KEY_CONTAINER
    KeyProvInfo.pwszProvName = None
    KeyProvInfo.dwProvType = gdef.PROV_RSA_FULL
    KeyProvInfo.dwFlags = 0
    KeyProvInfo.cProvParam = 0
    KeyProvInfo.rgProvParam = None
    #KeyProvInfo.dwKeySpec = AT_SIGNATURE
    KeyProvInfo.dwKeySpec = gdef.AT_KEYEXCHANGE

    crypt_algo = gdef.CRYPT_ALGORITHM_IDENTIFIER()
    crypt_algo.pszObjId = gdef.szOID_RSA_SHA256RSA.encode("ascii") # do something else (bytes in generated ctypes ?)

    # This is fucking dumb, there is no .format on bytes object...
    certif_name = "".join(("CN=", RANDOM_CERTIF_NAME))
    # Generate a self-signed certificate based on the given key-container and signature algorithme
    certif = windows.crypto.generation.generate_selfsigned_certificate(certif_name, key_info=KeyProvInfo, signature_algo=crypt_algo)
    # Add the newly created certificate to our TMP cert-store
    cert_store.add_certificate(certif)
    # Generate a pfx from the TMP cert-store
    pfx = windows.crypto.generation.generate_pfx(cert_store, RANDOM_PFX_PASSWORD)
    yield certif, pfx
    # Destroy the TMP key container
    prov = gdef.HCRYPTPROV()
    windows.winproxy.CryptAcquireContextW(prov, PFW_TEST_TMP_KEY_CONTAINER, None, gdef.PROV_RSA_FULL, gdef.CRYPT_DELETEKEYSET)



def test_certificate(rawcert):
    cert = windows.crypto.Certificate.from_buffer(rawcert)
    assert cert.serial == '1b 8e 94 cb 0b 3e eb b6 41 39 f3 c9 09 b1 6b 46'
    assert cert.name == u'PythonForWindowsTest'
    assert cert.issuer == u'PythonForWindowsTest'
    assert cert.thumbprint == 'EF 0C A8 C9 F9 E0 96 AF 74 18 56 8B C1 C9 57 27 A0 89 29 6A'
    assert cert.encoded == rawcert
    assert cert.version == 2
    assert cert == cert
    assert cert is cert.duplicate()
    cert.chains # TODO: craft a certificate with a chain for test purpose
    cert.store.certs
    cert.properties

def test_unicode_certificate(raw_unicodecert):
    cert = windows.crypto.Certificate.from_buffer(raw_unicodecert)
    assert cert.serial == '17 f7 d2 1b 78 01 b5 9d 43 4a 4e 54 2a 1a 30 4b'
    assert cert.name == UNICODE_CERT_NAME
    assert cert.issuer == UNICODE_CERT_NAME


def test_pfx(rawcert, rawpfx):
    pfx = windows.crypto.import_pfx(rawpfx, TEST_PFX_PASSWORD)
    orig_cert = windows.crypto.Certificate.from_buffer(rawcert)
    certs = pfx.certs
    assert len(certs) == 1
    # Test cert comparaison
    assert certs[0] == orig_cert


def test_open_pfx_bad_password(rawpfx):
    with pytest.raises(WindowsError) as ar:
        pfx = windows.crypto.import_pfx(rawpfx, "BadPassword")


def test_encrypt_decrypt(rawcert, rawpfx):
    message_to_encrypt = b"Testing message \xff\x01"
    cert = windows.crypto.Certificate.from_buffer(rawcert)
    # encrypt should accept a cert or iterable of cert
    res = windows.crypto.encrypt(cert, message_to_encrypt)
    res2 = windows.crypto.encrypt([cert, cert], message_to_encrypt)
    del cert
    assert message_to_encrypt not in res

    # Open pfx and decrypt
    pfx = windows.crypto.import_pfx(rawpfx, TEST_PFX_PASSWORD)
    decrypt = windows.crypto.decrypt(pfx, res)
    decrypt2 = windows.crypto.decrypt(pfx, res2)

    assert message_to_encrypt == decrypt
    assert decrypt == decrypt2



def test_randomkeypair(randomkeypair):
    randcert, randrawpfx = randomkeypair
    assert randcert.name == RANDOM_CERTIF_NAME
    randpfx = windows.crypto.import_pfx(randrawpfx, RANDOM_PFX_PASSWORD) # Check password is good too


def test_encrypt_decrypt_multiple_receivers(rawcert, rawpfx, randomkeypair):
    message_to_encrypt = b"\xff\x00 Testing message \xff\x01"
    # Receiver 1: random key pair
    randcert, randrawpfx = randomkeypair
    randpfx = windows.crypto.import_pfx(randrawpfx, RANDOM_PFX_PASSWORD)
    # Receiver 1: PFW-test-keypair
    pfx = windows.crypto.import_pfx(rawpfx, TEST_PFX_PASSWORD)
    cert = windows.crypto.Certificate.from_buffer(rawcert)
    assert cert.name != randcert.name
    assert cert.encoded != randcert.encoded
    # Encrypt the message with 2 differents certificates
    encrypted = windows.crypto.encrypt([cert, randcert], message_to_encrypt)
    # Decrypt with each PFX and check the result is valid/the same
    decrypted = windows.crypto.decrypt(pfx, encrypted)
    decrypted2 = windows.crypto.decrypt(randpfx, encrypted)
    assert decrypted == decrypted2 == message_to_encrypt



def test_crypt_obj():
    path = r"C:\windows\system32\kernel32.dll"
    x = windows.crypto.CryptObject(path)
    x.crypt_msg.certs
    x.crypt_msg.signers
    x.signers_and_certs
    # TODO: Need some better ideas

def test_certificate_from_store():
    assert windows.crypto.CertificateStore.from_system_store(u"Root")


def test_sign_verify(rawcert, rawpfx):
    message_to_sign = b"Testing message \xff\x01"
    # Load PFX (priv+pub key) & certif (pubkey only)
    pfx = windows.crypto.import_pfx(rawpfx, TEST_PFX_PASSWORD)
    cert = windows.crypto.Certificate.from_buffer(rawcert)
    signed_blob = windows.crypto.sign(pfx.certs[0], message_to_sign)
    assert message_to_sign in signed_blob
    decoded_blob = windows.crypto.verify_signature(cert, signed_blob)
    assert decoded_blob == message_to_sign


def test_sign_verify_fail(rawcert, rawpfx):
    message_to_sign = b"Testing message \xff\x01"
    # Load PFX (priv+pub key) & certif (pubkey only)
    pfx = windows.crypto.import_pfx(rawpfx, TEST_PFX_PASSWORD)
    cert = windows.crypto.Certificate.from_buffer(rawcert)
    signed_blob = windows.crypto.sign(pfx.certs[0], message_to_sign)
    assert message_to_sign in signed_blob
    # Tamper the signed mesasge content
    signed_blob = signed_blob.replace(b"message", b"massage")
    with pytest.raises(windows.winproxy.WinproxyError) as excinfo:
        decoded_blob = windows.crypto.verify_signature(cert, signed_blob)
    assert excinfo.value.winerror == gdef.STATUS_INVALID_SIGNATURE


# str(windows.crypto.encrypt(TEST_CERT, "Hello crypto")).encode("base64")
# Target serial == TEST_CERT.Serial == 1b 8e 94 cb 0b 3e eb b6 41 39 f3 c9 09 b1 6b 46
TEST_CRYPTMSG = b"""MIIBJAYJKoZIhvcNAQcDoIIBFTCCARECAQAxgc0wgcoCAQAwMzAfMR0wGwYDVQQDExRQeXRob25G
b3JXaW5kb3dzVGVzdAIQG46Uyws+67ZBOfPJCbFrRjANBgkqhkiG9w0BAQcwAASBgA1fwFY8w4Bb
fOMer94JhazbJxaUnV305QzF27w4GwNQ2UIpl9KWJoJJaF7azU3nVhP33agAxlxmr9fP48B6DeE1
pbu1jX9tEWlTJC6O0TmKcRPjblEaU6VJXXlpKlKZCmwCUuHR9VtcXGnxEU1Hy7FmHM96lvDRmYQT
Y0MnRJLyMDwGCSqGSIb3DQEHATAdBglghkgBZQMEASoEEEdEGEzKBrDO/zC8z6q6HLaAEGbjGCay
s6u32YhUxQ4/QhI="""

def test_cryptmsg_from_data():
    rawdata = b64decode(TEST_CRYPTMSG)
    cryptmsg = windows.crypto.CryptMessage.from_buffer(rawdata)
    rawtarget = b"\x1b\x8e\x94\xcb\x0b>\xeb\xb6A9\xf3\xc9\t\xb1kF"
    assert cryptmsg.get_recipient_data(0).SerialNumber.data[::-1] == rawtarget


# Dpapi

def test_dpapi_protect_unprotect():
    message_to_protect = b"Testing DPAPI message \xff\x01 but also \x02\xfe\xee"
    protected = windows.crypto.protect(message_to_protect)
    assert message_to_protect not in protected
    assert windows.crypto.unprotect(protected) == message_to_protect

def test_dpapi_protect_unprotect_with_entropy():
    message_to_protect = b"Testing DPAPI message \xff\x01 but also \x02\xfe\xee with entropy <3"
    protect_entropy = b"This is a password ? \x01\xff\x99"
    protected = windows.crypto.protect(message_to_protect, entropy=protect_entropy)
    assert message_to_protect not in protected
    with pytest.raises(WindowsError) as ar:
        windows.crypto.unprotect(protected)
    with pytest.raises(WindowsError) as ar:
        windows.crypto.unprotect(protected, entropy=b"Not the good password")
    assert windows.crypto.unprotect(protected, entropy=protect_entropy) == message_to_protect
