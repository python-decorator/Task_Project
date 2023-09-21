
# myApp/views.py
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from .forms import CustomAuthenticationForm, PositionForm
from .models import Task
from django.views import View
from django.db import transaction

# myApp/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

class TempView(TemplateView):
    template_name = "home.html"


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    authentication_form = CustomAuthenticationForm # forms.py
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


# 1. @login_required(login_url='login') # Sólo para funciones
# 2. LoginRequiredMixin -> Error: Page Not Found
#   http://127.0.0.1:8000/accounts/login/?next=/task-create/
# myProject/urls.py -> path("accounts/", include("django.contrib.auth.urls")),
#   Error: TemplateDoesNotExist -> registration/login.html
# LoginRequiredMixin -> settings.py => LOGIN_URL = 'login'
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task # => task_form.html
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

""" 
from django.utils.decorators import method_decorator  

@method_decorator(login_required, name='dispatch')
class TaskCreate(CreateView):
    model = Task # => task_form.html
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TaskCreate, self).dispatch(*args, **kwargs) """


class TaskList(LoginRequiredMixin, ListView):
    model = Task # => task_list.html
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context
    

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task # task_form.html
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task # task_confirm_delete.html
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

# myApp/views.py


class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data) # Diccionario
            print(form.cleaned_data["position"]) # String con nº items
            position_list = form.cleaned_data["position"].split(',')
            print(position_list) # Lista con nº orden
            with transaction.atomic():
                self.request.user.set_task_order(position_list)

        return redirect(reverse_lazy('tasks'))
    

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

# myApp/views.py
def custom_404(request, exception):
    return render(request, '404.html', status=404)

