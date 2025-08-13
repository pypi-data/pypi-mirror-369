import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="solvexia_sdk", 
    version="1.3.1",
    author="SolveXia Pty Ltd",
    author_email="support@solvexia.com",
    description="A development kit written in Python to access and work with SolveXia resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/solvexia/solvexia-python-sdk",
    packages=["solvexia_sdk", "solvexia_sdk.file", "solvexia_sdk.process", "solvexia_sdk.datasteps", "solvexia_sdk.processrun",
    "solvexia_sdk.table", "solvexia_sdk.user", "solvexia_sdk.usergroup"],
    install_requires=[
        'filesplit>=4.1.0',
        'readme-renderer>=29.0',
        'requests>=2.25.1',
        'requests-toolbelt>=0.9.1',
    ],
    license="GNU General Public License v3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)