from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title',
                                              'description'],
                                      extra=2,
                                      can_delete=True)
"""
Это набор форм ModuleFormSet. Он создается с по мощью предоставляемой
веб-фреймворком Django функции inlineformset_factory(). Внутристрочные
наборы форм – это небольшая абстракция поверх наборов форм, упрощаю-
щая работу со связанными объектами. Указанная функция позволяет созда-
вать модельный набор форм динамически для объектов Module, связанных
с объектом Course."""


