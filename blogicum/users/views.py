from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()


class CreateUserView(CreateView):
    template_name = 'registration/registration_form.html'
    model = User
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
