from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import Task, SubTask, Note

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
SubTaskFormSet = inlineformset_factory(Task, SubTask, fields=('title', 'status'), extra=3, can_delete=False)

NoteFormSet = inlineformset_factory(Task, Note, fields=('content',), extra=2, can_delete=False)