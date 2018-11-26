from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import views
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import SignUpForm
from .tokens import account_activation_token


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        print(form.errors)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            message = render_to_string("registration/act_acc_email.html", {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = "Activate your account for FRC 3654's team manager."
            to_email = form.cleaned_data.get("email")
            send_mail(subject=mail_subject,
                      message=message,
                      from_email="lavrema@outlook.com",
                      recipient_list=[to_email],)
            return render(request, "registration/check_email.html")
        else:
            return render(request, "registration/signup.html", {"form": form})
    else:
        form = SignUpForm()
        return render(request, "registration/signup.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        is_valid = True
    else:
        is_valid = False

    return render(request, "registration/activate.html", {"valid": is_valid})


def redirect_to_login(request):
    return redirect('accounts:login', permanent=True)


class LoginView(views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

