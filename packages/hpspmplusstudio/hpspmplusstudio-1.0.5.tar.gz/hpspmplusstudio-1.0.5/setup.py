from hpSPMPlusStudio._version import __version__
from setuptools import setup, find_packages

# requirements.txt dosyasını okuyarak bağımlılıkları al
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="hpspmplusstudio",
    version=__version__,
    author="NanoMagnetics Instruments",
    author_email="nmi.swteam@nano.com.tr",
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,  # Bu satır eklenmeli
    package_data={
        "": ["hpSPMPlusStudio/Docs/*", "hpSPMPlusStudio/Samples/*"],  # Belirli dosya ve klasörleri dahil eder
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)