import sys
import time
from mignonFramework import execJS, Logger, ConfigManager, inject

log = Logger(True)
config = ConfigManager()


@inject(config)
class Data:
    helloJs: str
    name: str
    age: int

if __name__ == "__main__":

    data: Data = config.getInstance(Data)

    @log
    @execJS(data.helloJs)
    def helloT(strs, num):
        return None


    print(helloT(data.name, data.age))
