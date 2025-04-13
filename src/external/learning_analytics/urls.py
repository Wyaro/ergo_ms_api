from django.urls import path

# Import base views
from src.external.learning_analytics.views import (
    EmployerSendView,
    EmployerGetView,
    EmployerPutView,
    EmployerDeleteView,
    DatabaseTablesView,
    ClearTablesView,
)



urlpatterns = [
    path('employers/', EmployerGetView.as_view(), name='employers'),
    path('employers_send/', EmployerSendView.as_view(), name='employers_send'),
    path('employers_put/<int:pk>/', EmployerPutView.as_view(), name='employers_put'),
    path('employers_delete/<int:pk>/', EmployerDeleteView.as_view(), name='employers_delete'),
    path('tables/', DatabaseTablesView.as_view(), name='database-tables'),
    path('tables/clear/', ClearTablesView.as_view(), name='clear-tables'),

]