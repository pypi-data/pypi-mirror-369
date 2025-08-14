import platform
import sys
import os

def main():
    print("Python version:", sys.version)
    print("OS:", platform.system(), platform.release())
    print("Current working directory:", os.getcwd())
    print("Environment variables:", dict(os.environ))
