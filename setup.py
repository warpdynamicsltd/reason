import reason
from setuptools import setup, find_packages


setup(
    name="reason",
    version="1.0.0",
    package_data={"reason": ["assets/lark/reason.lark", "assets/bin/vampire"]},
    packages=find_packages(),
)
