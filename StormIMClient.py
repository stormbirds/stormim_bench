import json
import struct
import time
import uuid
import socket

import select
from locust import Locust, exception, events

from protobuf import msg_pb2


class StormIMClient:
    mySocket = None
    my_id = str(uuid.uuid4())
    start_time = None

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #   连接到服务器
        self.mySocket.connect((self.host, self.port))
        self.mySocket.settimeout(5.0)
        self.send_handshake_msg()

    def stop_client(self):
        self.mySocket.close()

    def send_handshake_msg(self, timeout_in_seconds=5):
        msg = msg_pb2.Msg()
        head = msg.head
        msg_id_str = str(uuid.uuid4())
        head.msgId = msg_id_str
        head.msgType = 1001
        head.fromId = self.my_id
        head.timestamp = int(time.time())
        head.extend = "{\"token\":\"\"}"

        total_len = len(msg.SerializeToString())
        pack1 = struct.pack('>H', total_len)
        self.start_time = time.time()
        try:
            self.mySocket.send(pack1)
            self.mySocket.sendall(msg.SerializeToString())
        except Exception as e:
            total_time = int((time.time() - self.start_time) * 1000)
            events.request_failure.fire(request_type="StormIMClient",
                                        name="send_handshake_msg",
                                        response_time=total_time,
                                        exception=e)
            self.start_time = time.time()
        else:
            total_time = int((time.time() - self.start_time) * 1000)
            events.request_success.fire(request_type="StormIMClient",
                                        name="send_handshake_msg",
                                        response_time=total_time,
                                        response_length=0)
            self.start_time = time.time()
            self.recv()

    def send_heartbeat_msg(self):
        msg = msg_pb2.Msg()
        head = msg.head
        msg_id_str = str(uuid.uuid4())
        head.msgId = msg_id_str
        head.msgType = 1002
        head.fromId = self.my_id
        head.timestamp = int(time.time())

        total_len = len(msg.SerializeToString())
        pack1 = struct.pack('>H', total_len)
        self.start_time = time.time()
        try:
            self.mySocket.send(pack1)
            self.mySocket.sendall(msg.SerializeToString())
        except Exception as e:
            total_time = int((time.time() - self.start_time) * 1000)
            events.request_failure.fire(request_type="StormIMClient",
                                        name="send_heartbeat_msg",
                                        response_time=total_time,
                                        exception=e)
            self.start_time = time.time()
        else:
            total_time = int((time.time() - self.start_time) * 1000)
            events.request_success.fire(request_type="StormIMClient",
                                        name="send_heartbeat_msg",
                                        response_time=total_time,
                                        response_length=0)
            self.start_time = time.time()
            self.recv()

    def recv(self):
        try:
            total_len = self.mySocket.recv(2)
            total_len_recv = struct.unpack('>H', total_len)[0]
            message = self.mySocket.recv(total_len_recv)

            message_body = msg_pb2.Msg()
            message_body.ParseFromString(message)
            if message_body.head.msgType == 1001:
                response_time = (time.time() - self.start_time) * 1000
                status = json.loads(message_body.head.extend)
                events.request_success.fire(
                    request_type='StormIMClient',
                    name='RESPONSE HANDSHAKE',
                    response_time=response_time,
                    response_length=total_len_recv,
                )
                print("接受到握手消息消息报告状态：", status["status"])
            elif message_body.head.msgType == 1002:
                response_time = (time.time() - self.start_time) * 1000
                events.request_success.fire(
                    request_type='StormIMClient',
                    name='RESPONSE HEARTBEAT',
                    response_time=response_time,
                    response_length=total_len_recv,
                )
                print("接受到心跳消息报告：")
        except Exception as e:
            total_time = int((time.time() - self.start_time) * 1000)
            events.request_failure.fire(request_type="StormIMClient",
                                        name="RESPONSE MSG",
                                        response_time=total_time,
                                        exception=e)
            self.start_time = time.time()


class StormIMLocust(Locust):
    client = None
    port = None

    def __init__(self):
        super(StormIMLocust, self).__init__()
        if self.host is None or self.port is None:
            raise exception.LocustError(
                "You must specify the base host and port. Either in the host attribute in the Locust class, "
                "or on the command line using the --host --port options.")
        self.client = StormIMClient(self.host, self.port)
