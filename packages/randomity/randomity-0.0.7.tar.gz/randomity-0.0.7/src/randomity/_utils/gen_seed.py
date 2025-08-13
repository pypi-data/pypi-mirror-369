import os

def gen_seed_os():
    """
    Generate a seed using the operating system source.
    """
    return int.from_bytes(os.urandom(4), byteorder='big')