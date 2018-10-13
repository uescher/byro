from django import forms
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from byro.documents.models import Document, get_document_category_names


class DocumentUploadForm(forms.ModelForm):

    class Meta:
        model = Document
        exclude = ('content_hash', 'member')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = get_document_category_names()

        self.fields['category'] = forms.ChoiceField(choices=sorted(categories.items()), initial='byro.documents.misc')


class DocumentUploadView(FormView):
    template_name = 'office/documents/add.html'
    model = Document
    form_class = DocumentUploadForm

    @transaction.atomic
    def form_valid(self, form):
        form.save()
        form.instance.log(self, '.saved', file_name=form.instance.document.name, content_size=form.instance.document.size, content_hash=form.instance.content_hash)
        try:
            messages.success(self.request, _('The upload was processed successfully.'))
        except Exception as e:
            messages.error(self.request, _('The upload was added successfully, but could not be processed: ') + str(e))
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path
