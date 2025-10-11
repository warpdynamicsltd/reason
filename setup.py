#import reason
from setuptools import setup, find_packages, Extension


setup(
    name="reason",
    version="1.0.0",
    package_data={"reason": ["assets/lark/reason.lark", "assets/lark/tptp.lark", "assets/bin/vampire"]},
    packages=find_packages(),
    ext_modules=[
            Extension(
                "reason.cpp",
                ["reason/cpp/demo.cpp"],
                language="c++",
                extra_compile_args=["-std=c++20"]
            ),
    ]
)
