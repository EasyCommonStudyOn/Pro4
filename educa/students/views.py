from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin,
                              FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])


"""
Это представление StudentEnrollCourseView. Оно обслуживает зачисляемых
на курсы студентов. Указанное представление наследует от примеси LoginRequiredMixin,
поэтому получать доступ к данному представлению могут только
вошедшие на сайт пользователи. Оно также наследует от встроенного в Django
представления FormView, так как в его функции входит передача формы
на обработку. Форма CourseEnrollForm используется для атрибута form_class.
Помимо этого, для хранения данного объекта Course определяется атрибут
course. Если форма валидна, то текущий пользователь добавляется к зачис-
ленным на курс студентам.
Метод get_success_url() возвращает URL-адрес, на который пользователь
будет перенаправлен, если форма была успешно передана на обработку. Этот
метод эквивалентен атрибуту success_url. Затем URL-адрес с именем student_
course_detail переворачивается."""


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


"""
Это представление для просмотра курсов, на которые зачислены студенты.
Оно наследует от примесного класса LoginRequiredMixin, чтобы обеспечивать
доступ к представлению только вошедшим на платформу пользователям.
А также наследует от типового представления ListView, чтобы отображать
список объектов Course. Далее переопределяется метод get_queryset(), чтобы
извлекать только те курсы, на которые студент зачислен; для этого выполня-
ется фильтрация набора запросов QuerySet по полю ManyToManyField студента."""


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # получить объект Сourse
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # взять текущий модуль
            context['module'] = course.modules.get(
                id=self.kwargs['module_id'])
        else:
            # взять первый модуль
            context['module'] = course.modules.all()[0]
        return context
"""
Это представление StudentCourseDetailView. В нем переопределяется ме-
тод get_queryset(), чтобы ограничивать базовый набор запросов QuerySet
курсами, на которые зачислен студент. Кроме того, переопределяется метод
get_context_data(), чтобы устанавливать модуль курса в контекст, если задан
URL-параметр module_id. В противном случае задается первый модуль курса.
Благодаря этому студенты смогут перемещаться по модулям внутри курса."""

