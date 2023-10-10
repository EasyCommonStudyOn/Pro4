"""Это сериализатор модели Subject. Сериализаторы определяются аналогич-
но классам Django Form и ModelForm. Meta-класс позволяет указывать подлежа-
щую сериализации модель и поля, которые необходимо включать в сериа-
лизацию. Если не задать атрибут fields, то будут включены все поля модели."""

from rest_framework import serializers
from ..models import Subject, Course, Module, Content


class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()


class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner',
                  'modules']


"""
В новом исходном коде определяется класс ModuleSerializer, чтобы обеспе-
чивать сериализацию модели Module. Затем в класс CourseSerializer добавля-
ется атрибут modules, чтобы вложить сериализатор ModuleSerializer. При этом
задается параметр many=True, указывая на то, что сериализуется несколько
объектов. Параметр read_only сообщает, что это поле доступно только для
чтения и не должно включаться ни в какие входные данные для создания
или обновления объектов."""


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']


class ModuleWithContentsSerializer(
    serializers.ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description',
                  'contents']


class CourseWithContentsSerializer(
    serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner',
                  'modules']
