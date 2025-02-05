from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required


LOGIN_URL='/asrann/login'

app_name = "asrann"
urlpatterns = [
    path("", login_required(views.IndexView.as_view(), login_url=LOGIN_URL), name="index"), #dataset
    path("<uuid:dataset_pk>/", staff_member_required(login_required(views.RecordsView.as_view(), login_url=LOGIN_URL), login_url="/asrann"), name="records"),
    path("tagged/", login_required(views.TaggedView.as_view(), login_url=LOGIN_URL), name="tagged"),
    path("tagging/", login_required(views.tagging, login_url=LOGIN_URL), name="tagging"),
    path("report/", login_required(views.report, login_url=LOGIN_URL), name="report"),
    path("ureport/", staff_member_required(login_required(views.ureport, login_url=LOGIN_URL)), name="ureport"),
    path("record/<uuid:pk>/", login_required(views.singleRecord, login_url=LOGIN_URL), name="record"),
    #path("<int:dataset_pk>/record/<int:pk>/next/", login_required(views.goto_next, login_url=LOGIN_URL), name="next_rec"), 
    #path("<int:dataset_pk>/record/<int:pk>/prev/", login_required(views.goto_prev, login_url=LOGIN_URL), name="prev_rec"),
    path("record/<uuid:pk>/vote/", login_required(views.vote, login_url=LOGIN_URL), name="vote"),
    path('record/<uuid:pk>/audio/', login_required(views.serve_audio_from_tar, login_url=LOGIN_URL), name='serve_audio'),
    path('login/', views.sign_in, name='login'),
    path('register/', views.sign_up, name='register'),
    path('logout/', views.sign_out, name='logout'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',  
        views.activate, name='activate'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)