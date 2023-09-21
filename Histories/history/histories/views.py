import os

from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.template import loader
from django.shortcuts import render
from django.contrib import messages
from braces.views import SelectRelatedMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import generic
from .models import History, Comment, Guest
from .forms import HistoryForm, CommentForm, GuestForm

User = get_user_model()


class IndexView(generic.ListView):
    template_name = 'home.html'
    context_object_name = 'latest_histories_list'

    def get_queryset(self):
        local = History.objects.filter(user=self.request.user.id)
        return local.order_by("-created_at")[:10]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        local_user = self.request.user.id
        invitations = Guest.objects.filter(user=local_user)
        context['invitations_list'] = [elem.history for elem in invitations][:10]
        return context


class HistoryInvitationView(LoginRequiredMixin,generic.ListView):
    template_name = 'history_invitations.html'
    context_object_name = 'invitations_list'

    def get_queryset(self):
        local_user = self.request.user
        invitations = Guest.objects.filter(user=local_user)
        return [elem.history for elem in invitations][:10]


class HistoriesView(LoginRequiredMixin,generic.ListView):
    template_name = 'history_list.html'
    context_object_name = 'latest_histories_list'

    def get_queryset(self):
        local = History.objects.filter(user=self.request.user)
        return local.order_by("-created_at")[:10]


class HistoryDetailView(generic.DetailView):
    model = History
    template_name = "history_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HistoryDetailView, self).get_context_data(**kwargs)
        print("HistoryDetailView->Context")
        users_guest = [elem.user for elem in self.object.guestsbyhistory.all()]
        context["users_l"] = [elem for elem in User.objects.all() if elem not in users_guest]
        print(users_guest)
        return context


class CommentDetailView(generic.DetailView):
    model = Comment
    template_name = "comment_detail.html"


class CreateHistory(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):

    model = History
    form_class = HistoryForm
    template_name = 'history_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class CreateComment(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):

    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateComment, self).get_context_data(**kwargs)
        context["history_id"] = self.kwargs.get('hpk')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        if self.kwargs.get('hpk') != -1:
            loc_history = History.objects.get(pk=self.kwargs.get('hpk'))
            loc_history.n_images = loc_history.n_images + 1
            loc_history.save()
            self.object.history = loc_history

        self.object.save()
        return super().form_valid(form)


class HistoryGuests(LoginRequiredMixin, generic.CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'guests_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HistoryGuests, self).get_context_data(**kwargs)
        loc_history = History.objects.get(pk=self.kwargs.get('hpk'))
        context["loc_history"] = loc_history
        users_guest = [elem.user for elem in loc_history.guestsbyhistory.all()]
        context["users_l"] = [elem for elem in User.objects.all() if elem not in users_guest]
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.kwargs.get('hpk') != -1:
            loc_history = History.objects.get(pk=self.kwargs.get('hpk'))
            self.object.history = loc_history

            if self.request.POST.get("g_username") != "":
                newguest = User.objects.filter(username=self.request.POST.get("g_username"))
                guests = [elem.user for elem in loc_history.guestsbyhistory.all()]
                if newguest.count() > 0 and newguest[0] not in guests:
                    self.object.user = newguest[0]
                    print(self.object)
                else:
                    messages.error(self.request, "El usuario ya se encuentra en la lista de invitados.", extra_tags="Invitado existente")
            else:
                messages.error(self.request, "Nombre de usuario no valido.",
                               extra_tags="Nombre de usuario no existe.")

        self.object.save()
        return super().form_valid(form)


class DeleteHistoryGuest(LoginRequiredMixin, generic.DeleteView):
    model = Guest
    http_method_names = ['delete']

    def dispatch(self, request, *args, **kwargs):
        # safety checks go here ex: is user allowed to delete?
        handler = getattr(self, 'delete')
        return handler(request, *args, **kwargs)

    def get_success_url(self):
        success_url = str(reverse_lazy('histories:history_guests', kwargs={'hpk': self.object.history.pk}))
        return success_url

class UpdateHistory(LoginRequiredMixin, generic.UpdateView):
    model = History
    template_name = 'history_update.html'
    fields = ['title','description', 'place']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)


class UpdateComment(LoginRequiredMixin,generic.UpdateView):
    model = Comment
    template_name = 'comment_update.html'
    fields = ['title', 'image', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)


class DeleteComment(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = Comment
    select_related = ('user', 'history')
    template_name = 'comment_confirm_delete.html'
    success_url = reverse_lazy('histories:home')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        if self.image:
            print('delete was called with in view')
            imageloc = self.image.path
            if os.path.isfile(imageloc):
                os.remove(imageloc)
        messages.success(self.request, 'Comment Deleted')
        return super().delete(*args, **kwargs)


class DeleteHistory(LoginRequiredMixin, generic.DeleteView):
    model = History
    template_name = 'history_confirm_delete.html'
    success_url = reverse_lazy('histories:home')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        print('Delete History View')
        # if self.image:
        #     print('delete was called with in view')
        #     imageloc = self.image.path
        #     if os.path.isfile(imageloc):
        #         os.remove(imageloc)
        messages.success(self.request, 'History Deleted')
        return super().delete(*args, **kwargs)
