"""
As long as your tests are sensibly arranged, they won’t become unmanageable. Good rules-of-thumb include having:

    a separate TestClass for each model or view
    a separate test method for each set of conditions you want to test
    test method names that describe their function
"""
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name  = 'latest_question_list'
    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte = timezone.now()
        )[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/details.html'
    def get_quertyset(self):
        return Question.objects.filter(
            pub_date__lte = timezone.now()
        )


class ResultView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the Voting form
        return render(request, 'polls/details.html', {
            'question' : question,
            'error_message' : "You didn't select a choice.",
        })
    else:
        selected_choice += 1
        selected_choice.save()
        #Always rerun HttpResponseRidirect after successfully dealing with POST
        #data. This helps data from being posted twice if a user hits the back
        #button.
    return HttpResponseRidirect(reverse('polls:results', args(question_id,)))
