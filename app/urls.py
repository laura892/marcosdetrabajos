from rest_framework import routers
from django.urls import path
from rest_framework.documentation import include_docs_urls

from . import views


urlpatterns = [
    path('get_messages/', view=views.get_messages , name = 'get-messages'),
    path('create_message/', view=views.create_message , name = 'create-message'),
]