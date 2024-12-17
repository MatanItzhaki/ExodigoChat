import json
import socket
import threading

import requests as requests
from flask import Flask, request, Response

from mq.message import Message
from mq.mqConsumer import MQConsumer
from mq.mqPublisher import MQPublisher
from user import User


class Client:
    def __init__(self, username: str, user_response_consumer: MQConsumer, user_requests_publisher: MQPublisher,
                 message_consumer: MQConsumer, message_publisher: MQPublisher, port: int):
        self.__user_response_consumer = user_response_consumer
        self.__user_requests_publisher = user_requests_publisher
        self.__message_consumer = message_consumer
        self.__message_publisher = message_publisher
        self.__username = username
        self.__ip_address = socket.gethostbyname(socket.gethostname())
        self.__port = port
        self.__app = Flask(__name__)
        self.__known_users: dict[str, User] = {}
        self.__waiting_messages: dict[str, [str]] = {}

    def __send_user_request(self, request_type: str, request_data: str = "") -> None:
        message = Message({"type": request_type, "username": self.__username,
                           "ip address": self.__ip_address, "port": self.__port,
                           "data": request_data})
        self.__user_requests_publisher.publish_message(message)

    def __send_message(self, dest_username: str, message_data: str) -> None:
        message = Message({"source user": self.__username, "dest user": dest_username,
                           "data": message_data})
        self.__message_publisher.publish_message(message)

    def __send_direct_message(self, dest_username: str, message_data: str) -> None:
        if dest_username not in self.__known_users.keys():
            self.__waiting_messages[dest_username] = [] if dest_username not in self.__waiting_messages else None
            self.__waiting_messages[dest_username].append(message_data)
            self.__send_user_request("get user", dest_username)
            print("Not found user details, request from server")
            return

        dest_user = self.__known_users[dest_username]
        url = f"http://{dest_user.ip_address}:{dest_user.port}/message"
        message = {
            "source user": self.__username,
            "data": message_data
        }

        response = requests.post(url, data=json.dumps(message))
        print("Successful sending direct message to: " + dest_user.username) if response.status_code == 200 \
            else print("Some error happened when sanding direct message to: " + dest_user.username)

    def __handle_user_response(self, message: Message) -> None:
        if message.content["dest user"] != self.__username:
            return

        if message.content["status code"] != 200:
            print("Some error happened when sanding request message to server: " + message.content["data"] +
                  ", status code: " + message.content["status code"])
            return

        dest_username = message.content["username"]
        dest_ip = message.content["ip address"]
        dest_port = message.content["port"]
        self.__known_users[dest_username] = User(dest_username, dest_ip, dest_port)

        if dest_username in self.__waiting_messages.keys():
            for waiting_message in self.__waiting_messages[dest_username]:
                self.__send_direct_message(dest_username, waiting_message)
            self.__waiting_messages.pop(dest_username)

    def __handle_message(self, message: Message) -> None:
        if message.content["dest user"] != self.__username:
            return

        source_user = message.content["source user"]
        print("Received new message from " + source_user + ": " + message.content["data"])

    def __handle_direct_message(self) -> Response:
        message = json.loads(request.data.decode())
        print("Received new direct message from " + message["source user"] + ": " + message["data"])
        return Response(status=200)

    def __init_direct_api(self) -> None:
        self.__app.add_url_rule('/message', view_func=self.__handle_direct_message, methods=['POST'])
        self.__app.run(host=self.__ip_address, port=self.__port, debug=False, use_reloader=False)

    def start(self) -> None:
        try:
            self.__send_user_request("login")

            message_thread = threading.Thread(target=self.__user_response_consumer.start,
                                              args=(self.__handle_user_response,))
            message_thread.start()

            message_thread = threading.Thread(target=self.__message_consumer.start, args=(self.__handle_message,))
            message_thread.start()

            direct_message_thread = threading.Thread(target=self.__init_direct_api)
            direct_message_thread.start()

            while True:
                print("Enter dest username")
                dest_username = input()
                print("Enter message")
                message_data = input()
                print("Direct? [y/n]")
                direct = input()
                self.__send_direct_message(dest_username, message_data) if direct == "y" \
                    else self.__send_message(dest_username, message_data)
        finally:
            self.__send_user_request("logout")
            self.__user_response_consumer.close()
            self.__user_requests_publisher.close()
            self.__message_consumer.close()
            self.__message_publisher.close()
