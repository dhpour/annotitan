from django.shortcuts import render, redirect
from datetime import datetime
from django.views import generic
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from .models import Dataset, Record, Vote, ActiveDataset
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
from .forms import LoginForm
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Case, When, IntegerField, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
def singleRecord(request, dataset_pk, pk):
    
    user = request.user
    record = get_object_or_404(Record, pk=pk)
    vote = None
    print('dataset_pk: ', dataset_pk)
    print('request: ', user)

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
    return render(request, "asrann/single_record.html", context)

def vote(request, dataset_pk, pk):
    
    votes = {
        'up': 1,
        'down': -1
    }
    vote = request.POST.get('vote')
    record = get_object_or_404(Record, pk=pk)
    if vote:
        vote = votes[vote] * request.user.customuser.score_weight
        dt = timezone.now()
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
    return goto_next(request, dataset_pk, pk, record.add_date)

def goto_next(request, dataset_pk, pk, add_date):
    
    user = request.user
    try:
        #record = Record.objects.filter(~Q(vote__added_by=user)).filter(add_date__gt=add_date).filter(score__lt=SCORE_THRESHOLD).order_by("-score")
        record = Record.objects.filter(~Q(vote__added_by=user)).filter(score__lt=SCORE_THRESHOLD).order_by("-score")
        return HttpResponseRedirect(reverse("asrann:record", args=(dataset_pk, record[0].id,)))
    except (IndexError, Record.DoesNotExist):
        return HttpResponseRedirect(reverse("asrann:records", args=(dataset_pk,)))
    
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
    
def test(request):
    
    print('DIR: ', os.listdir())
    print("MEDIA_URL: ", settings.MEDIA_URL)
    print("MEDIA_URL: ", settings.MEDIA_ROOT)
    return render(request, "asrann/test.html", {"audio_file": "/asrann/media/0000101109.mp3"})

def serve_audio_from_tar(request, dataset_pk, pk):

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

def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/asrann')
        
        form = LoginForm()
        return render(request,'asrann/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
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

def tagging(request):
    
    try:
        dataset = get_object_or_404(ActiveDataset)
        record = Record.objects.filter(~Q(vote__added_by=request.user)).filter(score__lt=SCORE_THRESHOLD).order_by("-score")
        return HttpResponseRedirect(reverse("asrann:vote", args=(dataset.dataset.id, record[0].id)))
    except (IndexError, Record.DoesNotExist, Dataset.DoesNotExist):
        return HttpResponseRedirect(reverse("asrann:records", args=(dataset.dataset.id,)))
    
def report(request):
    try:
        your_records = Record.objects.filter(vote__added_by=request.user).count()
        if request.user.is_staff:
            active = ActiveDataset.objects.get()
            all_recs = Record.objects.filter(dataset=active.dataset).count()
            score_list = Record.objects.all().values_list(
                'score', flat = True
            ).distinct()
            response = "all records: {all_recs}<br>".format(all_recs=all_recs)
            distinct_scores = {}
            for score in score_list:
                distinct_scores[score] = Record.objects.filter(score=score).count()
                response += "score {score}: {distinct_score}<br>".format(score=score, distinct_score=distinct_scores[score])
            #print(response)
            vote_list = Record.objects.annotate(
                total_votes=Count('vote'),
                up_votes=Sum(Case(When(vote__vote__gt=0, then=F('vote__vote')), default=0, output_field=IntegerField())),
                down_votes=Sum(Case(When(vote__vote__lt=0, then=F('vote__vote')*-1), default=0, output_field=IntegerField())),
            ).order_by("-score", "-total_votes")

            page = request.GET.get('page', 1)
            paginator = Paginator(vote_list, 10)
            try:
                vote_list = paginator.page(page)
            except PageNotAnInteger:
                vote_list = paginator.page(1)
            except EmptyPage:
                vote_list = paginator.page(paginator.num_pages)

            context = {
                'your_records_count': your_records,
                'active_dataset': active.dataset,
                'active_dataset_records': all_recs,
                'score_list': distinct_scores,
                'group_by_vote': vote_list
            }
            return render(request,'asrann/report.html', context)
        
        return render(request,'asrann/report.html', {'your_records_count': your_records})
    
    except (IndexError, ActiveDataset.DoesNotExist, Record.DoesNotExist):
        return HttpResponse('Server error', status=500)
