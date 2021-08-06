from django.contrib import admin, auth
from django.contrib.auth import views as DjangoAuthViews
from django.urls import path, reverse_lazy, re_path
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from oauth2_provider import views as oauth_views
from api import views as api_views
from accounts.view import api, user_login, home, signup, confirm_sms, sms_login, logout_view



app_name = "accounts"

urlpatterns = [
    path('', home, name="home" ),
    path('login/', user_login, name="user_login"),
    path('accounts/login/', user_login, name="login"),
    path('signup/', signup, name="signup"),
    path('password_reset/', DjangoAuthViews.PasswordResetView.as_view(
        template_name="registration/password_reset/password_reset.html",
        html_email_template_name='registration/emails/email_password_reset.html',
        extra_email_context = {"site_name": "www.accounts.kit-app.ru",
                                "protocol": "https",
                                "domain": "accounts.kit-app.ru"
                                },
        success_url=reverse_lazy('password_reset_done')), name ='password_reset'),
    path('password_reset/done/', DjangoAuthViews.PasswordResetDoneView.as_view(
        template_name="registration/password_reset/password_reset_done.html"),
        name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', DjangoAuthViews.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset/password_reset_confirm.html",
        success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('password_reset_complete/', DjangoAuthViews.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset/password_reset_complete.html"),
        name='password_reset_complete'),
    path('admin/', admin.site.urls),
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # path('logout/', DjangoAuthViews.LogoutView.as_view(),name="logout"),
    path('logout/', logout_view, name="logout"),

    path('sms_login/', sms_login, name="sms_login"),
    path('confirm_sms/<phone_number>/', confirm_sms, name='confirm_sms' ),

]

api_urls = [
    path('api/getProfile/', api),
    path('api/getMyBalance/', api_views.getMyBalance, name="getMyBalance"),
    path('api/login/', api_views.authenticate, name="apiLogin"),
    path('api/getField/', api_views.getField, name="getField"),
    path('api/setField/', api_views.setField, name="setField"),
    path('api/getTransactions/', api_views.getTransactions, name="getTransactions"),
    path('api/setTransaction/', api_views.setTransaction, name="setTransaction"),
]

oauth_urlpatterns = [
    re_path(r"^o/authorize/$", oauth_views.AuthorizationView.as_view(template_name="registration/authorize.html"), name="authorize"),
    re_path(r"^o/token/$", oauth_views.TokenView.as_view(), name="token"),
    re_path(r"^o/revoke_token/$", oauth_views.RevokeTokenView.as_view(), name="revoke-token"),
    re_path(r"^o/introspect/$", oauth_views.IntrospectTokenView.as_view(), name="introspect"),
]

urlpatterns += oauth_urlpatterns
urlpatterns += api_urls

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
