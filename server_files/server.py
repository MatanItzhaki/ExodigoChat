import threading

from mq.message import Message
from mq.mqConsumer import MQConsumer
from mq.mqPublisher import MQPublisher
from user import User


class Server:
    def __init__(self, user_requests_consumer: MQConsumer, user_response_publisher: MQPublisher,
                 message_consumer: MQConsumer, message_publisher: MQPublisher):
        self.__user_requests_consumer = user_requests_consumer
        self.__user_response_publisher = user_response_publisher
        self.__message_consumer = message_consumer
        self.__message_publisher = message_publisher
        self.__connecting_users: dict[str, User] = {}
        self.__waiting_messages: dict[str, [Message]] = {}

    def __login(self, user: User) -> None:
        self.__connecting_users[user.username] = user
        print("hey " + user.username)
        if user.username in self.__waiting_messages.keys():
            for message in self.__waiting_messages[user.username]:
                self.__message_publisher.publish_message(message)
            self.__waiting_messages.pop(user.username)

    def __logout(self, user: User) -> None:
        if user.username in self.__connecting_users:
            self.__connecting_users.pop(user.username)

    def __send_user_details(self, user: User, dest_username: str) -> None:
        if dest_username in self.__connecting_users.keys():
            dest_user = self.__connecting_users[dest_username]
            response = Message({"type": "user details", "status code": 200, "username": dest_username,
                                "ip address": dest_user.ip_address, "port": dest_user.port,
                                "dest user": user.username})
        else:
            response = Message({"type": "user not found", "status code": 404, "dest user": user.username,
                                "data": "user " + dest_username + " not found"})
        self.__user_response_publisher.publish_message(response)

    def __handle_user(self, message: Message) -> None:
        user = User(message.content["username"], message.content["ip address"], message.content["port"])
        message_type = message.content["type"]

        if message_type == "login":
            self.__login(user)
        elif message_type == "get user":
            dest_username = message.content["data"]
            self.__send_user_details(user, dest_username)
        elif message_type == "logout":
            self.__logout(user)

    def __handle_message(self, message: Message) -> None:
        dest_user = message.content["dest user"]
        if dest_user in self.__connecting_users:
            self.__message_publisher.publish_message(message)
        else:
            self.__waiting_messages[dest_user] = [] if dest_user not in self.__waiting_messages.keys() else None
            self.__waiting_messages[dest_user].append(message)

    def start(self) -> None:
        try:
            user_thread = threading.Thread(target=self.__user_requests_consumer.start, args=(self.__handle_user,))
            user_thread.start()
            message_thread = threading.Thread(target=self.__message_consumer.start, args=(self.__handle_message,))
            message_thread.start()

            user_thread.join()
            message_thread.join()
        finally:
            self.__user_requests_consumer.close()
            self.__user_response_publisher.close()
            self.__message_consumer.close()
            self.__message_publisher.close()
