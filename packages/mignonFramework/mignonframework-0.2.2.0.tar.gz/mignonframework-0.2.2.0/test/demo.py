import sys
import time

from mignonFramework import execJS, Logger, ConfigManager

log = Logger(True)
config = ConfigManager()

class Data:
    helloJs: str

if __name__ == "__main__":

    data = Data()



    @log
    @execJS(data.helloJs)
    def helloT(strs, num , dicts):
        return None


    print(helloT(strs="a", num=1, dicts={
        "num": 2
    }))
