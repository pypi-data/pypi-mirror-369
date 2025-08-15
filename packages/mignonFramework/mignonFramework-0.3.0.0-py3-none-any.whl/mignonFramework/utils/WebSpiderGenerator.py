"""
思路:
1.先通过Curl2Request生成普通的request方法
会根据是否为json调整
要求需修改Curl方法,分别对post和get有特殊支持
2. 通过Queue自动回调.
背景: 每次调用Queue的hasNext函数后都会赋值, 为1 或者为0
"""