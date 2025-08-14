import sys
import time
import mignonFramework
from mignonFramework import Logger
from mignonFramework import execJS

log = Logger(True)

if __name__ == "__main__":
    for i in range(1, 100):
        time.sleep(0.1)
        sys.stdout.write(f"\r {i}")
    print("aAA")