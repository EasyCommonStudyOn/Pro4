import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'
        # присоединиться к группе чат-комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # принять соединение
        await self.accept()
        """
        но ему необходимо вызывать асинхронные методы канального слоя.
В новом методе connect() выполняется следующая работа.
1. Из области видимости извлекается id курса, чтобы выяснить, с каким
курсом связана чат-комната. При этом параметр course_id извлекается
из URL-адреса посредством инструкции доступа self.scope['url_route']
['kwargs']['course_id']. Каждый потребитель имеет область видимости
с информацией о его соединении, переданных в URL-адресе аргументах
и аутентифицированном пользователе, если таковой имеется.
2. Формируется имя группы с id курса, которому группа соответствует.
Напомним, что у вас будет группа каналов для чат-комнаты каждого
курса. Имя группы сохраняется в атрибуте room_group_name потребителя.
3. Выполняется присоединение к группе, добавляя текущий канал в груп-
пу. Из атрибута channel_name потребителя берется имя канала. Метод
group_add канального слоя используется для добавления канала в груп-
пу. Обертка async_to_sync() применяется для использования асинхрон-
ного метода канального слоя.
4. Вызов self.accept() сохраняется, чтобы принять WebSocket-соединение."""

    async def disconnect(self, close_code):
        # покинуть группу чат-комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # получить сообщение из WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # отправить сообщение в WebSocket
        # отправить сообщение в группу чат-комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': timezone.now().isoformat(),
            }
        )

    # получить сообщение из группы чат-комнаты
    async def chat_message(self, event):
        # отправить сообщение в веб-сокет
        await self.send(text_data=json.dumps(event))


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
