#!/usr/bin/env python

from setuptools import setup

LONG_DESCRIPTION = '''A pure-Python implementation of the AES (FIPS-197)
block-cipher algorithm and common modes of operation (CBC, CFB, CTR, ECB,
OFB) with no dependencies beyond standard Python libraries. See README.md
for API reference and details.'''

setup(
    long_description=LONG_DESCRIPTION,
)
