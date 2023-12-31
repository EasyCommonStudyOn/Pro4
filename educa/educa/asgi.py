import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import educa.chat.routing
from educa import chat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educa.settings')

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
"""
В приведенном выше исходном коде добавляется новый маршрут для про-
токола websocket. Маршрутизатор URLRouter используется для соотнесения
соединений websocket с шаблонами URL-адресов, определенными в списке
websocket_urlpatterns файла routing.py приложения chat. Помимо этого, ис-
пользуется предоставляемый приложением-оберткой Channels класс Auth-
MiddlewareStack, который поддерживает встроенную в Django стандартную
аутен тификацию, при которой детальная информация о пользователе хра-
нится в сеансе"""

"""
Теперь, когда приложение-обертка Сhannels установлено в проекте, можно
разработать чат-сервер для ведения дискуссий по курсам. Для того чтобы реа-
лизовать чат-сервер в проекте, необходимо предпринять следующие шаги.
1. Настроить потребителя: потребители – это отдельные фрагменты
кода, которые могут оперировать веб-сокетами в ключе, очень похожи-
ми на традиционные HTTP-представления. Вы создадите потребителя
для чтения сообщений из канала связи и записи с ообщений в канал.
2. Сконфигурировать маршрутизацию: приложение-обертка Сhannels
предоставляет классы маршрутизации, которые позволяют комбини-
ровать и ставить потребителей в стек. Вы сконфигурируете маршрути-
зацию URL-адресов для своего чата-потребителя.
3. Реализовать WebSocket-клиент: при обращении студента к чат-
комнате происходит подсоединение к веб-сокету из браузера и с по-
мощью JavaScript отправляются либо приходят сообщения.
4. Активировать канальный слой: канальные слои позволяют обме-
ниваться данными между разными экземплярами приложения. Они
являются полезной частью создания распределенного реально-времен-
ного приложения. Вы установите канальный слой с использованием
резидентного хранилища Redis."""
