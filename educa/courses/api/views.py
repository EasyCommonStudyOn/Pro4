"""
В приведенном выше исходном коде используются типовые представле-
ния ListAPIView и RetrieveAPIView фреймворка REST. URL-параметр pk встав-
лен в представление детальной информации, чтобы извлекать объект по
данному первичному ключу.
Оба представления имеют следующие атрибуты:
• queryset: базовый набор запросов QuerySet, используемый для извлече-
ния объектов;
• serializer_class: класс сериализации объектов.
"""
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from ..models import Subject, Course
from ..api.serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from ..api.permissions import IsEnrolled


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True,
            methods=['post'],
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    @action(detail=True,
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
"""
Работа данного метода описывается следующим образом.
1. Декоратор action используется с параметром detail=True, чтобы зада-
вать действие, которое выполняется над одним объектом.
2. Затем указывается, что для этого действия разрешен только метод GET.
3. Далее используется новый класс-сериализатор CourseWithContentsSerializer,
который включает прорисованное содержимое курса.
4. Используются как разрешения IsAuthenticated, так и конкретно-при-
кладные разрешения IsEnrolled. Тем самым обеспечивается, чтобы
доступ к содержимому курса могли получать только те пользователи,
которые были зачислены на курс.
5. В конце применяется существующее действие retrieve(), чтобы воз-
вращать объект Course."""

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# class CourseEnrollView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
#     """
#     Здесь вставлено разрешение IsAuthenticated. Оно будет предотвращать до-
# ступ анонимных пользователей к представлению"""
#
#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})
#
#
# """
# Представление CourseEnrollView обрабатывает зачисление пользователей
# на курсы. Приведенный выше исходный код выполняет следующую работу.
# 1. Создается конкретно-прикладное представление как подкласс APIView.
# 2. Определяется метод post() для действий POST. В этом представлении
# никакой другой HTTP-метод не разрешен.
# 3. Ожидается URL-параметр pk, содержащий ИД курса. Курс извлекается
# по заданному параметру pk, и если он не найден, то вызывается исклю-
# чение 404.
# 4. Текущий пользователь добавляется во взаимосвязь students многие-ко-
# многим объекта Course, и возвращается успешный ответ."""
