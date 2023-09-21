from django.urls import path
from . import views

app_name = "histories"

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("invitations/", views.HistoryInvitationView.as_view(), name="history_invitations"),
    path('newhistories/', views.HistoriesView.as_view(), name='history_list'),
    path("<int:pk>/", views.HistoryDetailView.as_view(), name="history_detail"),
    path("Comment/<int:pk>/", views.CommentDetailView.as_view(), name="comment_detail"),
    path('newhistory/', views.CreateHistory.as_view(), name='history_create'),
    path('Comment/newcomment/<hpk>', views.CreateComment.as_view(), name='comment_create'),
    path('History/Guests/<hpk>', views.HistoryGuests.as_view(), name='history_guests'),
    path('History/Guests/delete/<pk>', views.DeleteHistoryGuest.as_view(), name='historyGuest_delete'),
    path('edithistory/<int:pk>', views.UpdateHistory.as_view(), name='history_edit'),
    path('editcomment/<int:pk>', views.UpdateComment.as_view(), name='comment_edit'),
    path('deletecomment/<int:pk>/', views.DeleteComment.as_view(), name='comment_delete'),
    path('deletehistory/<int:pk>/', views.DeleteHistory.as_view(), name='history_delete'),
]