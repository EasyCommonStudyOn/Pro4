from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, \
    UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from django.db.models import Count
from .models import Subject
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
from django.core.cache import cache


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)

        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin,
                       PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


"""
В приведенном выше исходном коде создаются примесные классы Owner-
Mixin и OwnerEditMixin. Эти примеси будут использоваться вместе со встроен-
ными в Django представлениями ListView, CreateView, UpdateView и DeleteView.
Примесный класс OwnerMixin реализует метод get_queryset(), который ис-
пользуется представлениями для получения базового набора запросов QuerySet.
Указанный примесный класс будет переопределять этот метод с целью
фильтрации объектов по атрибуту owner, чтобы извлекать объекты, принад-
лежащие текущему пользователю (request.user).
Примесный класс OwnerEditMixin реализует метод form_valid(), который
используется представлениями, использующими примесный класс Django
ModelFormMixin, то есть представлениями с формами или модельными форма-
ми, такими как CreateView и UpdateView. Метод form_valid() исполняется, когда
переданная на обработку форма является валидной.
По умолчанию поведение этого метода состоит в сохранении экземпляра
(в случае модельных форм) и перенаправлении пользователя на адрес Success_
url. Указанный метод переопределяется для того, чтобы автоматически
устанавливать текущего пользователя в атрибуте owner сохраняемого объ-
екта. Тем самым при сохранении объекта автоматически устанавливается
его владелец.
Примесный класс OwnerMixin можно использовать в представлениях, кото-
рые взаимодействуют с любой моделью, содержащей атрибут owner.
Далее определяется примесный класс OwnerCourseMixin, который наследует
от OwnerMixin и предоставляет следующие атрибуты дочерним представле-
ниям:
• model: модель, используемая для наборов запросов; этот атрибут ис-
пользуется всеми представлениями;
• fields: поля модели, служащие для компоновки модельной формы
представлений CreateView и UpdateView;
• Success_url: используется представлениями CreateView, UpdateView
и DeleteView, чтобы перенаправлять пользователя после успешной пере-
дачи формы на обработку или удаления объекта. При этом использу-
ется URL-адрес с именем manage_course_list,Далее определяется примесный класс OwnerCourseEditMixin со следующим
атрибутом:
• template_name: шаблон, который будет использоваться для представле-
ний CreateView и UpdateView.
Наконец, создаются следующие ниже представления, которые являются
подклассами примесного класса OwnerCourseMixin:
• ManageCourseListView: выводит список созданных пользователем кур-
сов. Указанное представление наследует от OwnerCourseMixin и ListView
и определяет специальный атрибут template_name для шаблона, который
будет выводить список курсов;
• CourseCreateView: использует модельную форму для создания нового
объекта Course. В указанном представлении используются поля, опре-
деленные в примесном классе OwnerCourseMixin, чтобы компоновать мо-дельную форму; это представление также является подклассом класса
CreateView. Оно использует шаблон, определенный в примесном классе
OwnerCourseEditMixin;
• CourseUpdateView: обеспечивает возможность редактировать существу-
ющий объект Course. В указанном представлении используются поля,
определенные в примесном классе OwnerCourseMixin, чтобы компоно-
вать модельную форму; это представление также является подклассом
класса UpdateView. Оно использует шаблон, определенный в примесном
классе OwnerCourseEditMixin;
• CourseDeleteView: наследует от OwnerCourseMixin и типового DeleteView.
В указанном представлении определяется специальный атрибут template_
name для шаблона, который будет подтверждать удаление курса.
"""


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({
            'course': self.course,
            'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({
            'course': self.course,
            'formset': formset})


"""
Представление CourseModuleUpdateView обрабатывает набор форм, служа-
щий для добавления, обновления и удаления модулей определенного курса.
Это представление наследует от следующих примесей и представлений:
• TemplateResponseMixin: этот примесный класс отвечает за прорисовку
шаблонов и возврат HTTP-ответа. Для него требуется атрибут template_
name, указывающий на подлежащий прорисовке шаблон и предостав-
ляющий метод render_to_response(), чтобы передавать ему контекст
и прорисовывать шаблон;
• View: предоставляемое веб-фреймворком Django базовое представле-
ние на основе класса."""


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


"""
Это представление ModuleContentListView. Указанное представление полу-
чает объект Module с заданным ИД, который принадлежит текущему пользо-
вателю, и прорисовывает шаблон с данным модулем"""

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user) \
                .update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                total_courses=Count('courses'))
        cache.set('all_subjects', subjects)
        """
        В приведенном выше исходном коде делается попытка получить ключ
all_students из кеша с по мощью метода cache.get(). Этот метод возвращает
None, если данный ключ не найден. Если ключ не найден (еще не кеширован
или кеширован, но истек тайм-аут), то выполняется запрос, чтобы извлечь
все объекты Subject и их число курсов, и результат кешируется с по мощью
метода cache.set()."""
        all_courses = Course.objects.annotate(
            total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object})
        return context
