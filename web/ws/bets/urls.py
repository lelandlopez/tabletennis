from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculateBets', views.calculateBets, name='calculateBets'),
    path('scrapeEntire', views.scrapeEntire, name='scrapeEntire'),
    path('scrapeBets', views.scrapeBets, name='scrapeBets'),
    path('placeBet', views.placeBet, name='placeBet'),
    path('getBets', views.getBetsResponse, name='getBets'),
    path('getPlacedBets', views.getPlacedBets, name='getPlacedBets'),
    path('updateModelPerformance', views.updateModelPerformance, name='updateModelPerformance'),
    path('getEstimatedVsActualProfit', views.getEstimatedVsActualProfit, name='getEstimatedVsActualProfit'),
    path('removePlaced', views.removePlaced, name='removePlaced')
]