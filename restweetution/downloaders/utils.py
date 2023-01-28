import hashlib

import aiofiles


def compute_signature(buffer: bytes):
    """
    Compute sha1 of file
    @param buffer: byte buffer
    @return: sha1
    """
    return hashlib.sha1(buffer).hexdigest()


async def compute_signature_from_file(filename: str):
    sha1 = hashlib.sha1()
    buf_size = 65536  # let's read stuff in 64kb chunks!

    async with aiofiles.open(filename, mode='rb') as f:
        while True:
            data = await f.read(buf_size)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()
