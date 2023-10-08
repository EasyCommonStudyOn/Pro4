"""
Приведенная выше форма будет использоваться для зачисления студентов
на курсы. Поле course предназначено для курса, на который пользователь
будет зачислен; следовательно, это поле ModelChoiceField.
"""

from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), widget=forms.HiddenInput)
