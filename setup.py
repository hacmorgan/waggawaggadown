#!/usr/bin/env python3


"""
Install Wagga Wagga Down
"""


from setuptools import setup


setup(
    name="waggawaggadown",
    description="Silly small zombie game set in Wagga",
    author="Hamish Morgan",
    author_email="ham430@gmail.com",
    url="http://github.com/hacmorgan/waggawaggadown",
    packages=["wwd"],
    package_data={},
    install_requires=[
        "numpy",
        "Pillow",
        "pygame",
    ],
    scripts=[],
)
