import adafruit_hashlib
import adafruit_binascii
import hmac

SHA1 = adafruit_hashlib.sha1()
TEST = __name__ == "__main__"

def gen_sha1(inData):
    SHA1.update(inData)
    return SHA1.digest()

if TEST:
    print(f"hash test: {adafruit_binascii.hexlify(gen_sha1(b'test'))}")
# should be a94a8fe5ccb19ba61c4c0873d391e987982fbbd3

def HMAC(k, m):
    return hmac.HMAC(k, m, digestmod="sha1").digest()


if TEST:
    KEY = b'abcd'
    MESSAGE = b'efgh'
    print("===========================================")
    print("HMAC test: ", adafruit_binascii.hexlify(HMAC(KEY, MESSAGE)))
    # should be e5dbcf9263188f9fce90df572afeb39b66b27198


# Base32 decoder, since base64 lib wouldnt fit


def base32_decode(encoded):
    missing_padding = len(encoded) % 8
    if missing_padding != 0:
        encoded += '=' * (8 - missing_padding)
    encoded = encoded.upper()
    chunks = [encoded[i:i + 8] for i in range(0, len(encoded), 8)]

    out = []
    for chunk in chunks:
        bits = 0
        bitbuff = 0
        for c in chunk:
            if 'A' <= c <= 'Z':
                n = ord(c) - ord('A')
            elif '2' <= c <= '7':
                n = ord(c) - ord('2') + 26
            elif c == '=':
                continue
            else:
                raise ValueError("Not base32")
            # 5 bits per 8 chars of base32
            bits += 5
            # shift down and add the current value
            bitbuff <<= 5
            bitbuff |= n
            # great! we have enough to extract a byte
            if bits >= 8:
                bits -= 8
                byte = bitbuff >> bits  # grab top 8 bits
                bitbuff &= ~(0xFF << bits)  # and clear them
                out.append(byte)  # store what we got
    return out


if TEST:
    print("===========================================")
    print("Base32 test: ", bytes(base32_decode("IFSGCZTSOVUXIIJB")))
    # should be "Adafruit!!"


# Turns an integer into a padded-with-0x0 bytestr


def int_to_bytestring(i, padding=8):
    result = []
    while i != 0:
        result.insert(0, i & 0xFF)
        i >>= 8
    result = [0] * (padding - len(result)) + result
    return bytes(result)


# HMAC -> OTP generator, pretty much same as
# https://github.com/pyotp/pyotp/blob/master/src/pyotp/otp.py


def generate_otp(int_input, secret_key, digits=6):
    if int_input < 0:
        raise ValueError('input must be positive integer')
    hmac_hash = bytearray(
        HMAC(bytes(base32_decode(secret_key)),
             int_to_bytestring(int_input))
    )
    offset = hmac_hash[-1] & 0xf
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff))
    str_code = str(code % 10 ** digits)
    while len(str_code) < digits:
        str_code = '0' + str_code

    return str_code