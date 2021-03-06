from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.forms.formsets import formset_factory
from django.core.mail import send_mail
import re

 
from create.forms import CreateForm
from create.forms import QuestionForm
from create.models import CreateRecData
from create.models import Question, Answer

@ensure_csrf_cookie
def home(request):
        if request.method == 'POST':
                form = CreateForm(request.POST)
                if form.is_valid():
                        request.session['_create_info_post'] = request.POST
                        request.session.set_expiry(request.session.get_expiry_age())
                        return HttpResponseRedirect('/create/questions/1')
        else:
                form = CreateForm()

        data = {'form': form}
        return render(request, 'create/home.html', data)

def questions_1(request):
        if request.session.get('_create_info_post') is None:
                return HttpResponseRedirect('/create/success')
        else:
                if request.method == 'POST':
                        form = QuestionForm(request.POST, page = 1)
                        if form.is_valid():
                                info_post = request.session.get('_create_info_post')
                                form_new = CreateRecData(name=info_post['name'], rollno=info_post['rollno'], email=info_post['email'], mobileno=info_post['mobileno'], URL_to_Poster_or_Video=request.POST['url_field'])
                                form_new.save()
                                info_page_1 = request.POST
                                i=0
                                for key, data in info_page_1.items():
                                        if re.search(r'\d+', key) is None:
                                                continue 
                                        i = int(re.search(r'\d+', key).group())
                                        if i>=1:
                                                new_answer= Answer(answer=data, question=Question.objects.get(id=i), creator=form_new)
                                                new_answer.save()

                                request.session['_create_info_success'] = 'success'
                                return HttpResponseRedirect('/create/success')
                else:
                        form = QuestionForm(page = 1)

                data = {'form': form}
                return render(request, 'create/question.html', data)

def success(request):       
        if request.session.get('_create_info_success') is None:
                raise Http404("User session expired/Fill form first")
        else:
                info_post = request.session.get('_create_info_post')
                send_mail('ISTE NITK Recruitments 2016','Hello ' + info_post['name'] + '!\n\nThank You for filling up the recruitment form. We have received your submission. We look forward to meeting you in the interaction.\n\nIf you haven\'t applied then please report back to us.\n\nSee you soon! :)\n\nTeam ISTE-NITK','istenitkchapter@gmail.com',[info_post['email']],fail_silently=False,)
                del request.session['_create_info_post']
                del request.session['_create_info_success']
                return render(request, 'create/success.html')
