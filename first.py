
import sys
import os

def test_hello():
    print("Hello, World!")
    print("Python version:", sys.version)
    print("Current working directory:", os.getcwd())
    print("Files in this directory:", os.listdir())
    print("Hello, World! for python")



if __name__ == "__main__":
    test_hello()
