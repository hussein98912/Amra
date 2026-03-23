from django.urls import path
from .views import *

urlpatterns = [
    path("create/", CreateTicketAPIView.as_view(), name="ticket-create"),
    path("my/", MyTicketsAPIView.as_view(), name="my-tickets"),
    path("<int:pk>/", TicketDetailAPIView.as_view(), name="ticket-detail"),
    path("<int:pk>/status/", UpdateTicketStatusAPIView.as_view(), name="ticket-status"),
]