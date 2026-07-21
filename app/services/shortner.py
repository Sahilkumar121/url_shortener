import hashlib

ALPHABATE = "0123456789abcdefghijklmnopqrstUVwxyzABCDEFGHIJKLMNOPQURSTUVWXYZ"
BASE = len(ALPHABATE)


def generate_unique_code(long_url: str, length: int = 6):
    hash_hex = hashlib.md5(long_url.encode("utf-8")).hexdigest()

    hash_int = int(hash_hex[:8], 16)

    if hash_int == 0:
        return ALPHABATE[0]
    else:
        encoded = []
        while hash_int > 0:
            hash_int, remiander = divmod(hash_int, BASE)
            encoded.append(ALPHABATE[remiander])

        short_code = "".join(reversed(encoded))

    short_code = short_code.rjust(length, ALPHABATE[0])

    return short_code[:length]
