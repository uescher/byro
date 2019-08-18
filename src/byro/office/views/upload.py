from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView, ListView

from byro.bookkeeping.models import RealTransactionSource, Transaction


class UploadForm(forms.ModelForm):
    class Meta:
        model = RealTransactionSource
        fields = ('source_file',)


class UploadListView(ListView):
    template_name = 'office/upload/list.html'
    context_object_name = 'uploads'
    model = RealTransactionSource


class CsvUploadView(FormView):
    template_name = 'office/upload/add.html'
    model = RealTransactionSource
    form_class = UploadForm

    def form_valid(self, form):
        form.save()
        try:
            form.instance.process()
            messages.success(self.request, _('The upload was processed successfully.'))
        except Exception as e:
            messages.error(
                self.request,
                _('The upload was added successfully, but could not be processed: ')
                + str(e),
            )
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path


class UploadProcessView(DetailView):
    model = RealTransactionSource

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            obj.process()
            messages.success(self.request, _('The upload was processed successfully.'))
        except Exception as e:
            messages.error(
                self.request, _('The upload could not be processed: ') + str(e)
            )
        return redirect('office:finance.uploads.list')


class UploadMatchView(DetailView):
    model = RealTransactionSource

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        errors = success = 0
        for t in Transaction.objects.filter(bookings__source=obj):
            try:
                t.process_transaction()
                success += 1
            except Exception as e:
                errors += 1
                print(e) # FIXME
        messages.info(
            self.request,
            _( '{success} successful matches.'.format(success=success)),
        )
        return redirect('office:finance.uploads.list')
