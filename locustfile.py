import struct

from locust import TaskSet, task

import random


import time
import uuid
import socket
from locust import Locust, TaskSet, events, task
import google.protobuf
import protobuf.msg_pb2
#   创建套接字
from protobuf import msg_pb2

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#   设置ip和端口
host = "wifi.stormbirds.cn"
port = 8855
print("开始连接服务器",host)
#   连接到服务器
mySocket.connect((host, port))
msg = msg_pb2.Msg()

head = msg.head
msgIdStr = str(uuid.uuid4())
head.msgId = msgIdStr
print("消息ID：",msgIdStr)
head.msgType = 1001
# head.msgContentType =
head.fromId = str(uuid.uuid4())
head.toId = str(uuid.uuid4())
head.timestamp = int(time.time())
# head.statusReport
head.extend = "{\"token\":\"\"}"

totallen = len(msg.SerializeToString())
pack1 = struct.pack('>I', totallen) # the first part of the message is length
mySocket.sendall(pack1)
mySocket.sendall(msg.SerializeToString())
# mySocket.send(msg.SerializeToString())
print("发送握手消息：",msg.SerializeToString())
print("连接到服务器",host)
while True:
    #   接收消息
    print("----------------------读取:")
    Head_data = mySocket.recv(4)  # 接收数据头 4个字节,
    data_len = int.from_bytes(Head_data, byteorder='big')
    print("接受到数据：", data_len)
    protobufdata = mySocket.recv(data_len)

    tmessage = msg_pb2.Msg()
    tmessage.ParseFromString(protobufdata)
    print(tmessage)
