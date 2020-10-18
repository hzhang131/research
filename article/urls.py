from django.urls import path

from .views import HomePageView, SRView, SRFNView, SRCView, SRFView, process

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('search', SRView.as_view(), name='search_results'),
    path('nodes', SRFNView.as_view(), name='search_results_fornodes'),
    path('cached', SRCView.as_view(), name='search_results_cached'),
    path('folder', SRFView.as_view(), name='search_results_folder'),
    path('process', process, name='process'),
]
