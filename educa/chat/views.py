from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


@login_required
def course_chat_room(request, course_id):
    try:
        # извлечь курс с заданным id, к которому
        # присоединился текущий пользователь
        course = request.user.courses_joined.get(id=course_id)
    except:
        # пользователь не является студентом курса либо
        # курс не существует
        return HttpResponseForbidden()
    return render(request, 'chat/room.html', {'course': course})

"""
Это представление course_chat_room. В данном представлении используется
декоратор @login_required, чтобы предотвращать доступ любого неаутенти-
фикацированного пользователя к представлению. Представление получает
обязательный параметр course_id, который используется для извлечения
курса с заданным id.
Доступ к курсам, на которые пользователь зачислен, обеспечивается по-
средством взаимосвязи Courses_Joined, и из этого подмножества курсов из-
влекается курс с заданным id. Если курс с указанным id не существует либо
пользователь на него не зачислен, то возвращается ответ HttpResponseForbidden,
который транслируется в HTTP-ответ со статусом 403.
Если курс с заданным id существует и пользователь на него зачислен, то
прорисовывается шаблон chat/room.html с переданным в контекст шаблона
объектом course."""

