from django.urls import path
from . import views

urlpatterns = [
    path("convert/", views.convert_html, name='convert'),
    path("matrix/", views.matrix_html, name='matrix'),
    path("dimsum/", views.dimsum_html, name='dimsum'),
    path("translation/", views.translation_html, name='translation'),
    path("regression/", views.regression_html, name='regression')
]
