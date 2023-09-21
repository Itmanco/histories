from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from . import forms

# Create your views here.


class SignUp(CreateView):
    context_object_name = 'signup'
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'



