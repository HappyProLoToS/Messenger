from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver
from time import strftime


class Handler(LineOnlyReceiver):
    factory: 'Server'
    login: str

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)
        print("Disconnected")

    def connectionMade(self):
        self.login = None
        self.factory.clients.append(self)
        self.sendLine("Введите логин".encode())
        print("Connected")

    def lineReceived(self, line: bytes):
        message = line.decode()

        if message == "":
            self.sendLine("Введите сообщение...".encode())
        else:
            if self.login is not None:
                self.factory.send_message_to_clients(self, message)
            else:
                if message.startswith("login:"):
                    login = message.replace("login:", "")

                    for registered_user in self.factory.clients:
                        if registered_user.login == login:
                            self.sendLine(f"Логин <{login}> уже занят, попробуйте другой...".encode())
                            return

                    self.login = login

                    print(f"New user: {login}")
                    self.sendLine(f"Добро пожаловать, {login}!".encode())
                    self.factory.send_history(self)
                else:
                    self.sendLine("Неверный логин".encode())


class Server(ServerFactory):
    protocol = Handler
    clients: list
    history: list

    def __init__(self):
        self.clients = []
        self.history = []

    def startFactory(self):
        print("Server started...")

    def send_message_to_clients(self, sender: Handler, message: str):
        timenow = strftime("%H:%M")
        message = f"{timenow} <{sender.login}>: {message}"

        self.history.append(message)

        for user in self.clients:
            if user.login is not None:
                user.sendLine(message.encode())

    def send_history(self, client: Handler, count=10):
        pack = self.history[-count:]

        for message in pack:
            client.sendLine(message.encode())


reactor.listenTCP(
    1111, Server()
)
reactor.run()
