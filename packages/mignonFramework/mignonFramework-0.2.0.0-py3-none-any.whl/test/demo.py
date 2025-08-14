import sys
import time
import mignonFramework
from mignonFramework import Logger
from mignonFramework import execJS

log = Logger(True)

if __name__ == "__main__":

    @log
    @execJS("./resources/js/test.jsx")
    def helloT(strs, num , dicts):
        return None


    print(helloT(strs="a", num=1, dicts={
        "num": 2
    }))
