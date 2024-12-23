from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Project, Task, TaskComment
from .forms import ProjectForm, TaskForm, CommentForm

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'tasks/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    tasks = project.tasks.all().order_by('status', '-priority', 'due_date')
    return render(request, 'tasks/project_detail.html', {
        'project': project,
        'tasks': tasks
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', pk=pk)
    else:
        form = CommentForm()
    
    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'comments': comments,
        'form': form
    })

@login_required
def update_task_status(request, pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})




@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form, 'action': 'Create'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'tasks/project_form.html', {'form': form, 'action': 'Edit'})

@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            return redirect('tasks:project_detail', pk=project_pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks:task_detail', pk=pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit'})


@login_required
def project_toggle_complete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.mark_completed() if not project.is_completed else setattr(project, 'is_completed', False)
    project.save()
    return redirect('tasks:project_detail', pk=pk)

@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.mark_completed() if not task.is_completed else setattr(task, 'is_completed', False)
    task.save()
    return redirect('tasks:task_detail', pk=pk)