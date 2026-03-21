from django.db import models
from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from .models import Task
from django.urls import path
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from .forms import NoteFormSet, SubTaskFormSet, TaskForm
from .models import Task, Category, Priority
from django.db import transaction
from django.db.models import Q, Count

class HomePageView(ListView):
    model = Task
    context_object_name = 'home'
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # [cite: 413]
        
        # 1. Main Stats
        total = Task.objects.count()
        completed = Task.objects.filter(status="Completed").count()
        in_progress = Task.objects.filter(status="In Progress").count()
        pending = Task.objects.filter(status="Pending").count()
        
        context["total_tasks"] = total
        context["completed_tasks"] = completed
        context["in_progress_tasks"] = in_progress
        context["pending_tasks"] = pending

        # 2. Rates
        # Safe division to avoid ZeroDivisionError
        context["completion_rate"] = int((completed / total * 100)) if total > 0 else 0
        
        # Delinquency (Tasks past deadline that are not completed)
        now = timezone.now()
        delinquent_tasks = Task.objects.filter(deadline__lt=now).exclude(status="Completed").count()
        delinquent_rate = int((delinquent_tasks / total * 100)) if total > 0 else 0
        context["delinquency_rate"] = delinquent_rate
        
        # Compliancy (Tasks completed on or before deadline)
        compliant_tasks = Task.objects.filter(status="Completed", updated_at__lte=models.F('deadline')).count()
        context["compliancy_rate"] = int((compliant_tasks / total * 100)) if total > 0 else 0

        # 3. Task Summary by Priority
        context["prio_optional"] = Task.objects.filter(priority__name__icontains="Optional").count()
        context["prio_low"] = Task.objects.filter(priority__name__icontains="Low").count()
        context["prio_medium"] = Task.objects.filter(priority__name__icontains="Medium").count()
        context["prio_high"] = Task.objects.filter(priority__name__icontains="High").count()
        context["prio_critical"] = Task.objects.filter(priority__name__icontains="Critical").count()

        # 4. Task Summary by Category
        context["cat_work"] = Task.objects.filter(category__name__icontains="Work").count()
        context["cat_project"] = Task.objects.filter(category__name__icontains="Project").count()
        context["cat_school"] = Task.objects.filter(category__name__icontains="School").count()
        context["cat_personal"] = Task.objects.filter(category__name__icontains="Personal").count()
        context["cat_finance"] = Task.objects.filter(category__name__icontains="Finance").count()

        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page'] # Remove the old page number
        context['query_params'] = query_params.urlencode() # Send the rest to the template

        return context

class TaskListView(ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task_list.html'
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset()
        
        # 1. Search [cite: 158-160]
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        # 2. Filters
        status = self.request.GET.get('status')
        if status and status != 'All':
            qs = qs.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority and priority != 'All':
            qs = qs.filter(priority__id=priority)

        category = self.request.GET.get('category')
        if category and category != 'All':
            qs = qs.filter(category__id=category)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # [cite: 412-413]
        # Pass data to populate the filter dropdowns
        context['categories'] = Category.objects.all()
        context['priorities'] = Priority.objects.all()
        # Pass the total count for the table header
        context['total_filtered'] = self.get_queryset().count()
        return context

    def get_ordering(self):
        allowed_sorts = ["title", "deadline", "status", "priority"] # [cite: 531-532]
        sort_by = self.request.GET.get("sort_by")
        if sort_by in allowed_sorts:
            return sort_by
        return "-created_at"

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['subtasks'] = SubTaskFormSet(self.request.POST)
            data['notes'] = NoteFormSet(self.request.POST)
        else:
            data['subtasks'] = SubTaskFormSet()
            data['notes'] = NoteFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        subtasks = context['subtasks']
        notes = context['notes']
        with transaction.atomic(): # Ensures everything saves together cleanly
            self.object = form.save()
            if subtasks.is_valid() and notes.is_valid():
                subtasks.instance = self.object
                subtasks.save()
                notes.instance = self.object
                notes.save()
        return super().form_valid(form)

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('task-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['subtasks'] = SubTaskFormSet(self.request.POST, instance=self.object)
            data['notes'] = NoteFormSet(self.request.POST, instance=self.object)
        else:
            data['subtasks'] = SubTaskFormSet(instance=self.object)
            data['notes'] = NoteFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        subtasks = context['subtasks']
        notes = context['notes']
        with transaction.atomic():
            self.object = form.save()
            if subtasks.is_valid() and notes.is_valid():
                subtasks.instance = self.object
                subtasks.save()
                notes.instance = self.object
                notes.save()
        return super().form_valid(form)

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'task_del.html'
    success_url = reverse_lazy('task-list')

class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'category_list.html'

    def get_queryset(self):
        # This counts the tasks related to each category, filtered by status
        return Category.objects.annotate(
            total_tasks=Count('task'),
            pending=Count('task', filter=Q(task__status='Pending')),
            in_progress=Count('task', filter=Q(task__status='In Progress')),
            completed=Count('task', filter=Q(task__status='Completed'))
        ).order_by('-total_tasks') # Sorts by most tasks first

class PriorityListView(ListView):
    model = Priority
    context_object_name = 'priorities'
    template_name = 'priority_list.html'

    def get_queryset(self):
        # This counts the tasks related to each priority, filtered by status
        return Priority.objects.annotate(
            total_tasks=Count('task'),
            pending=Count('task', filter=Q(task__status='Pending')),
            in_progress=Count('task', filter=Q(task__status='In Progress')),
            completed=Count('task', filter=Q(task__status='Completed'))
        ).order_by('-total_tasks')