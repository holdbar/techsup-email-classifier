from django.shortcuts import render
from django.views.generic import FormView

from core.forms import EmailForm
from core.email_processor import EmailProcessor

class EmailClassifierView(FormView):
    template_name = "email_classifier.html"
    form_class = EmailForm

    def post(self, request, *args, **kwargs):
        print(request.POST)
        email = request.POST.get('email')
        context = self.get_context_data()
        processor = EmailProcessor()
        processor.process(email)
        context.update({'result': processor.result})
        return render(self.request, self.template_name, context)