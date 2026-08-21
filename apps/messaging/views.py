from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from apps.notifications.services import notify
from apps.reports.models import Report
from .forms import MessageForm
from .models import Conversation, Message

INBOX_PAGE_SIZE = 15


def _other_participant(conversation, sender):
    return conversation.report.reporter if sender == conversation.claimant else conversation.claimant


def _notify_new_message(conversation, message):
    recipient = _other_participant(conversation, message.sender)
    notify(
        recipient, 'message',
        f'رسالة جديدة بخصوص: {conversation.report.title}',
        message.body[:120],
        reverse('messaging:conversation', args=[conversation.pk]),
    )


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
            message = Message.objects.create(
                conversation=conversation, sender=request.user, body=form.cleaned_data['body']
            )
            _notify_new_message(conversation, message)

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
            _notify_new_message(conversation, message)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('messaging/_message.html', {'message': message, 'user': request.user})
                return JsonResponse({'html': html})
            return redirect('messaging:conversation', pk=pk)
    else:
        form = MessageForm()

    conversation.messages.exclude(sender=request.user).update(read=True)
    request.user.notifications.filter(type='message', url=request.path, is_read=False).update(is_read=True)

    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'form': form,
        'other_participant': _other_participant(conversation, request.user),
        'is_reporter': request.user == conversation.report.reporter,
    })


@login_required
def mark_verified(request, pk):
    conversation = get_object_or_404(Conversation.objects.select_related('report'), pk=pk)
    if request.user != conversation.report.reporter:
        return HttpResponseForbidden()
    if request.method != 'POST':
        return HttpResponseForbidden()

    conversation.ownership_verified = True
    conversation.save(update_fields=['ownership_verified'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('messaging:conversation', pk=pk)


@login_required
def inbox(request):
    qs = Conversation.objects.filter(
        Q(claimant=request.user) | Q(report__reporter=request.user)
    ).select_related('report', 'claimant').distinct()
    page_obj = Paginator(qs, INBOX_PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'messaging/inbox.html', {'conversations': page_obj, 'page_obj': page_obj})
