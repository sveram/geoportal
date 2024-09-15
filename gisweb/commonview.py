import sys

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from geoportal import settings
from gisweb.forms import ResetPasswordForm, ChangePasswordForm
from gisweb.models import Person


def add_data_user(request, context):
    if 'person' not in request.session:
        if not request.user.is_authenticated:
            raise Exception('User is not authenticated in the system')
        context['person'] = Person.objects.get(user=request.user)


class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # def send_email_reset_pwd(self, request, user, url=''):
    #     data = {}
    #     try:
    #         user.token = uuid.uuid4()
    #         user.save(request, 'edit')
    #         mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    #         print(mailServer.ehlo())
    #         mailServer.starttls()
    #         print(mailServer.ehlo())
    #         mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    #         print('Connected..')
    #
    #         email_to = user.email
    #         # Construct the simple message
    #         message = MIMEMultipart()
    #         message['From'] = settings.EMAIL_HOST_USER
    #         message['To'] = email_to
    #         message['Subject'] = "Password Reset"
    #
    #         content = render_to_string('send_email.html', {
    #             'link_resetpwd': f"{url}/change/password/{str(user.token)}/",
    #             'link_home': url,
    #             'user': user
    #         })
    #         message.attach(MIMEText(content, 'html'))
    #
    #         mailServer.sendmail(settings.EMAIL_HOST_USER, email_to, message.as_string())
    #         print('Email sent successfully')
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return data

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user = form.get_user()
                url = self.request.META['HTTP_ORIGIN']
                # data = self.send_email_reset_pwd(request, user, url)
            else:
                print(form.errors)
                data['error'] = form.errors
        except Exception as ex:
            data['error'] = str(ex)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Password Reset'
        return context


# class MyPasswordChangeView(FormView):
#     form_class = ChangePasswordForm
#     template_name = 'registration/changepwd.html'
#     success_url = reverse_lazy('gisweb:login')
#
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#
#     def get(self, request, *args, **kwargs):
#         token = self.kwargs['token']
#         # if Person.objects.filter(token=token).exists():
#         #     return super().get(request, *args, **kwargs)
#         return HttpResponseRedirect('/')
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             form = ChangePasswordForm(request.POST)
#             if form.is_valid():
#                 pass
#                 # user = Person.objects.get(token=self.kwargs['token'])
#                 # user.user.set_password(request.POST['password'])
#                 # user.token = uuid.uuid4()
#                 # user.save(request, 'edit')
#             else:
#                 data['error'] = form.errors
#         except Exception as ex:
#             data['error'] = str(ex)
#         return JsonResponse(data, safe=False)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Change Password'
#         return context

class ChangePasswordView(FormView):
    # form_class = ChangePasswordForm
    template_name = 'registration/changepwd.html'

    # success_url = reverse_lazy('gisweb:login')

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        return redirect('password_change_successful')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change Password'
        return context


class CommonViews(TemplateView):
    initial = {}
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            username = request.POST['username'].strip()
            password = request.POST['password'].strip()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    data['result'] = True
                    data['to'] = '/'  # Redirect to home or any other page
                else:
                    raise NameError("User is inactive")
            else:
                raise NameError('Incorrect credentials!')
        except Exception as ex:
            data['result'] = False
            data['error'] = str(ex)

        return JsonResponse(data)
