import sys
import time
from mignonFramework import execJS, Logger, ConfigManager, inject, QueueIter, target

log = Logger(True)
config = ConfigManager()


def callback(que: QueueIter):
    print(f"这里是Callback => {que.current_index}")


que = QueueIter(range(1, 20), 1,
                callback, config, False)


@inject(config)
@target(que, "name", "hello")
@target(que, "age", 0)
class Data:
    helloJs: str
    name: str
    age: int


if __name__ == "__main__":
    data: Data = config.getInstance(Data)
    datas: Data = config.getInstance(Data)




    while que.hasNext():
        time.sleep(0.1)
        sys.stdout.write(f"\r {next(que)}")

    print("=========================")
    que.pages = range(10, 30)
    que.current_index = 11
    while que.hasNext():
        time.sleep(1)
        sys.stdout.write(f"\r {next(que)}")
    print(datas.age, data.name)