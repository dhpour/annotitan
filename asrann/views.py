from django.shortcuts import render, redirect
from datetime import datetime
from django.views import generic
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from .models import Dataset, Record, Vote, ActiveDataset, CustomUser
from django.shortcuts import get_object_or_404, render
from django.db.models import F
from django.urls import reverse
import pprint
from django.utils import timezone
from django.db.models import Q
import os
from django.conf import settings
import tarfile
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Case, When, IntegerField, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.core.mail import EmailMessage    
from .token import account_activation_token  
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

SCORE_THRESHOLD = 2


class IndexView(generic.ListView):
    template_name = "asrann/index.html"
    context_object_name = "latest_assigned_datasets"
    paginate_by = 10
    def get_queryset(self):
        """Return the last five published datasets."""
        #self.request.session['prev_stack'] = []
        #self.request.session['next_stack'] = []
        return Dataset.objects.order_by("-add_date") #[:5]

class RecordsView(generic.ListView):
    #model = Dataset
    template_name = "asrann/records.html"
    context_object_name = "dataset_assigned_records"
    paginate_by = 10
    
    def get_queryset(self):
        """Return the last five published datasets."""
        #self.request.session['prev_stack'] = []
        print('kwargs:', self.kwargs)
        return Record.objects.filter(dataset_id=self.kwargs['dataset_pk']) #[:300]

class TaggedView(generic.ListView):
    model = Vote
    template_name = 'asrann/tagged_list.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'all_tagged_by_user'  # Default: object_list
    paginate_by = 10
    
    def get_queryset(self):
        #self.request.session['prev_stack'] = []
        #self.request.session['next_stack'] = []
        user = self.request.user
        return Vote.objects.filter(added_by=user)

#@login_required(login_url=LOGIN_URL)
def singleRecord(request, pk):
    
    user = request.user
    record = get_object_or_404(Record, pk=pk)
    vote = None

    try:
        vote = Vote.objects.get(record=record, added_by=user).vote
    except Vote.DoesNotExist:
        pass
    context = {
        "record": record,
        "vote": vote,
        "audio_file": record.audio_file,
        "static": False
    }
    if not user.customuser.user_tested:
        vote_meter = Vote.objects.filter(record=record).aggregate(Sum('vote'))['vote__sum']
        context["vote_meter"] = vote_meter
        context["remained_tests"] = user.customuser.passed_score

    return render(request, "asrann/single_record.html", context)

def vote(request, pk):
    
    votes = {
        'up': 1,
        'down': -1
    }
    vote = request.POST.get('vote')
    record = get_object_or_404(Record, pk=pk)
    user = request.user
    if vote:
        dt = timezone.now()
        if user.customuser.user_tested:
            vote = votes[vote] * request.user.customuser.score_weight
            v, created = Vote.objects.update_or_create(
                added_by = request.user,
                record = record,
                defaults = {"vote": vote, "vote_date": timezone.now()},
                create_defaults = {
                    "added_by": request.user,
                    "record": record,
                    "vote": vote,
                    "vote_date": timezone.now()
                }
            )
        else:
            vote = votes[vote]
            vote_meter = Vote.objects.filter(record=record).aggregate(Sum('vote'))['vote__sum']
            user_model = User.objects.get(id=user.id)
            passed_score = user_model.customuser.passed_score

            if (vote > 0 and vote_meter > 0) or (vote < 0 and vote_meter < 0):
                custom_user = CustomUser.objects.get(user=user_model)
                if passed_score - 1 <= 0:
                    custom_user.user_tested = True
                custom_user.passed_score = passed_score - 1
                custom_user.save()
    return goto_next(request, pk, record.add_date)

def goto_next(request, pk, add_date):
    
    user = request.user
    try:
        active = get_object_or_404(ActiveDataset.objects.order_by('?')[:1])
        #record = Record.objects.filter(~Q(vote__added_by=user)).filter(add_date__gt=add_date).filter(score__lt=SCORE_THRESHOLD).order_by("-score")
        if not user.customuser.user_tested:
            records = Record.objects.filter(score__gte=SCORE_THRESHOLD)
            record = random.choice(records)
            return HttpResponseRedirect(reverse("asrann:record", args=(record.id,)))    
        records = Record.objects.filter(~Q(vote__added_by=user)).filter(score__lt=SCORE_THRESHOLD, dataset=active.dataset).order_by("-score")
        return HttpResponseRedirect(reverse("asrann:record", args=(records[0].id,)))
    except (IndexError, Record.DoesNotExist):
        return redirect('/asrann/')
    
def goto_prev(request, dataset_pk, pk):
    
    next = request.session.get('next_stack')
    prev = request.session.get('prev_stack')
    #print('got-prev:prev', prev)
    #print('got-next:prev', prev)
    if next and len(next) > 0:
        next.append({
            "record": pk,
            "dataset": dataset_pk
        })
    else:
        next = [{
            "record": pk,
            "dataset": dataset_pk
        }]
    request.session['next_stack'] = next
    if len(prev) > 0:
        last_page = prev.pop()
        #request.session['prev_stack'] = prev
        return HttpResponseRedirect(reverse("asrann:record", args=(last_page['dataset'], last_page['record'],)))
    else:
        return HttpResponseRedirect(reverse("asrann:records", args=(dataset_pk,)))

def serve_audio_from_tar(request, pk):

    try:
        record = Record.objects.get(id=pk)
        tar_file_string_name = "clips_" + "{:03d}".format(record.tar_file) + ".tar"
        dataset_folder = record.dataset.data_folder
        tar_file_path = settings.MEDIA_ROOT + dataset_folder + "/" + tar_file_string_name
        audio_file_name = record.audio_file
        with tarfile.open(tar_file_path, 'r') as tar:
            audio_file = tar.extractfile(audio_file_name)
            response = HttpResponse(content_type='audio/mpeg')
            #response['Content-Disposition'] = f'attachment; filename="{audio_file_name}"'
            response.write(audio_file.read())

        return response
    except Record.DoesNotExist:
        pass

def activate(request, uidb64, token):  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return HttpResponse("<div style='direction: rtl'><p>از تایید ایمیل‌تان ممنونیم. حالا میتوانید <a href='/asrann'>وارد شوید</a></p></div>")
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')  
        
    else:  
        return HttpResponse('Activation link is invalid!')  
    
def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/asrann')
        
        form = LoginForm()
        return render(request,'asrann/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('/asrann')
        
        # form is not valid or user is not authenticated
        messages.error(request,f'Invalid username or password')
        return render(request,'asrann/login.html',{'form': form})
    
def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('/asrann/login/')

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/asrann/')
    
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'asrann/register.html', { 'form': form})  
    
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.lower()
            user.is_active = False
            user.save()
            messages.success(request, 'You have singed up successfully.')
            #login(request, user)
            #return redirect('/asrann/')
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('asrann/acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject,
                        message, 
                        'ravazi.noreply@gmail.com', 
                        [to_email]
            )
            print('\temail:', message)
            email.send()  
            #return HttpResponse('Please confirm your email address to complete the registration')
            return HttpResponse("<div style='direction: rtl'><p>ایمیلی برای شما ارسال شده است. برای استفاده از حساب کاربری‌تان  باید ایمیل‌تان را تایید کنید.</p><a href='/asrann'>وارد شوید</a></div>")
        else:
            return render(request, 'asrann/register.html', {'form': form})
        
def tagging(request):
    
    try:
        active = get_object_or_404(ActiveDataset.objects.order_by('?')[:1])
        if not request.user.customuser.user_tested:
            records = Record.objects.filter(score__gte=SCORE_THRESHOLD)
            record = random.choice(records)
            return HttpResponseRedirect(reverse("asrann:vote", args=(record.id, )))
        
        #records = Record.objects.filter(~Q(vote__added_by=request.user)).filter(score__lt=SCORE_THRESHOLD, dataset=active.dataset).order_by("-score")
        #record = records[0]
        records = Record.objects.filter(~Q(vote__added_by=request.user)).filter(score=0, dataset=active.dataset)
        record = random.choice(records)
        #print('selecting randomly - score: ', record.score)
        return HttpResponseRedirect(reverse("asrann:vote", args=(record.id, )))
    except (IndexError, Record.DoesNotExist, Dataset.DoesNotExist):
        return redirect('/asrann/')
    
def report(request):
    try:
        your_records = Record.objects.filter(vote__added_by=request.user).count()
        if request.user.is_staff:
            page = request.GET.get('page', '1')
            print('\tpage typ:', type(page))
            active_datasets = ActiveDataset.objects.all()
            distinct_scores_all = {}
            combined_records = 0
            datasets_features = []
            if page == '1':
                for active in active_datasets:
                    all_recs = Record.objects.filter(dataset=active.dataset).count()
                    combined_records += all_recs
                    score_list = Record.objects.all().values_list(
                        'score', flat = True
                    ).distinct()
                    response = "all records: {all_recs}<br>".format(all_recs=all_recs)
                    distinct_scores = {}
                    for score in score_list:
                        distinct_scores[score] = Record.objects.filter(score=score, dataset=active.dataset).count()
                        distinct_scores_all[score] = distinct_scores_all.get(score, 0) + distinct_scores[score]
                        response += "score {score}: {distinct_score}<br>".format(score=score, distinct_score=distinct_scores[score])
                    #print(response)
                    datasets_features.append({
                        'active_dataset': active.dataset.name,
                        'active_dataset_records': all_recs,
                        'score_list': distinct_scores
                    })
            vote_list = Record.objects.annotate(
                total_votes=Count('vote'),
                up_votes=Sum(Case(When(vote__vote__gt=0, then=F('vote__vote')), default=0, output_field=IntegerField())),
                down_votes=Sum(Case(When(vote__vote__lt=0, then=F('vote__vote')*-1), default=0, output_field=IntegerField())),
            ).order_by("-score", "-total_votes")

            #page = request.GET.get('page', 1)
            paginator = Paginator(vote_list, 10)
            try:
                vote_list = paginator.page(page)
            except PageNotAnInteger:
                vote_list = paginator.page(1)
            except EmptyPage:
                vote_list = paginator.page(paginator.num_pages)

            context = {
                'your_records_count': your_records,
                'group_by_vote': vote_list,
                'first_page': False
            }
            if page == '1':
                context['first_page'] = True
                context['datasets_features'] = datasets_features
                context['distinct_scores_all'] = distinct_scores_all
                context['combined_records_count'] = combined_records

            return render(request,'asrann/report.html', context)
        
        return render(request,'asrann/report.html', {'your_records_count': your_records})
    
    except (IndexError, ActiveDataset.DoesNotExist, Record.DoesNotExist):
        return HttpResponse('Server error', status=500)
