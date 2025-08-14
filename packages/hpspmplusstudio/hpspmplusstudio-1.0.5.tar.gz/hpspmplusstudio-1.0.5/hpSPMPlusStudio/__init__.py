"""Package for API the HpSPM+ software.Copyright (C) NanoMagnetics Instruments - All Rights Reserved (2024) License - MIT"""
import os
import platform 
import pathlib
from .NMIImporter import Decarators
from .NMIImporter import BuiltInImporter
from .NMIManager.Managers.DeviceManager import NMIDevice
from .RequestManager.NMICommand import*
from .RequestManager.NMIEndpoint import*

from .Utils import SystemReadingsChannels
from ._version import __version__




def package_path() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

def doc_path() -> pathlib.Path:
    return package_path() / "Docs"

def sample_path() -> pathlib.Path:
    return package_path() / "Samples"

def library_version() -> tuple[int,int,int,int]:
    major, minor, revision = __version__.split(".")
    return (int(major), int(minor), int(revision), 0)

def help(): 
    try:
        print("hpSPM+ API package:")
        print(f"Version: {__version__}")
        print("\nDocs:")
        print(doc_path())
        for doc in os.listdir(doc_path()):
            print(f"  {doc}")
        print("\nSamples:")
        print(sample_path())
        for doc in os.listdir(sample_path()):
            print(f"  {doc}")
    except Exception as e:
        pass
        
    