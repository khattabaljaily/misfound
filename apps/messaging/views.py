from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from apps.reports.models import Report
from .forms import MessageForm
from .models import Conversation, Message


@login_required
def start_conversation(request, report_pk):
    report = get_object_or_404(Report, pk=report_pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if report.reporter == request.user:
        return redirect('reports:detail', pk=report.pk)

    conversation, _ = Conversation.objects.get_or_create(report=report, claimant=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation, sender=request.user, body=form.cleaned_data['body']
            )

    conversation_url = reverse('messaging:conversation', args=[conversation.pk])
    if is_ajax:
        return JsonResponse({'success': True, 'redirect': conversation_url})
    return redirect(conversation_url)


def _can_access(user, conversation):
    return user == conversation.claimant or user == conversation.report.reporter


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related('report', 'report__reporter', 'claimant'), pk=pk
    )
    if not _can_access(request.user, conversation):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message.objects.create(
                conversation=conversation, sender=request.user, body=form.cleaned_data['body']
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('messaging/_message.html', {'message': message, 'user': request.user})
                return JsonResponse({'html': html})
            return redirect('messaging:conversation', pk=pk)
    else:
        form = MessageForm()

    conversation.messages.exclude(sender=request.user).update(read=True)

    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'form': form,
    })


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        Q(claimant=request.user) | Q(report__reporter=request.user)
    ).select_related('report', 'claimant').distinct()
    return render(request, 'messaging/inbox.html', {'conversations': conversations})
