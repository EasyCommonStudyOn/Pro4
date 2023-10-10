import json
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # принять соединение
        self.accept()

    def disconnect(self, close_code):
        pass

    # получить сообщение из WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # отправить сообщение в WebSocket
        self.send(text_data=json.dumps({'message': message}))


"""
Это потребитель ChatConsumer. Приведенный выше класс наследует от
встроенного в Channels класса WebsocketConsumer, чтобы реализовать базового
WebSocket-потребителя. В указанном потребителе реализуются следующие
методы:
• connnect(): вызывается при получении нового соединения. Любая связь
принимается с по мощью self.accept(). Кроме того, соединение можно
отклонить, вызвав self.close();
• disconnect(): вызывается при закрытии сокета. Здесь используется pass,
потому что при закрытии соединения клиентом никаких действий вы-
полнять не нужно;
• receive(): вызывается при получении данных. При этом ожидается, что
будет получен текст в виде text_data (в случае двоичных данных он по-
ступает в виде binary_data). Полученные текстовые данные трактуются
как JSON. Поэтому для загрузки полученных JSON-данных в словарь Python
используется метод json.loads(). Выполняется обращение к ключу
message, который ожидаемо будет присутствовать в полученной струк-
туре JSON. Для того чтобы отразить сообщение назад, оно отправляется
обратно в веб-сокет с по мощью self.send(), снова преобразовывая его
в формат JSON посредством метода json.dumps()"""
