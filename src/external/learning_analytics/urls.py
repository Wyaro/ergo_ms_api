from django.urls import path

# Import base views
from src.external.learning_analytics.views import (
    EmployerSendView,
    EmployerGetView,
    EmployerPutView,
    EmployerDeleteView,
    CompetentionSendView,
    CompetentionGetView,
    CompetentionPutView,
    CompetentionDeleteView,
    TechnologySendView,
    TechnologyGetView,
    TechnologyPutView,
    TechnologyDeleteView,
    DatabaseTablesView,
    ClearTablesView,
)

# Import data formalization submodule views
from src.external.learning_analytics.data_formalization_submodule.views import (
    AcademicCompetenceMatrixSendView,
    AcademicCompetenceMatrixGetView,
    AcademicCompetenceMatrixPutView,
    AcademicCompetenceMatrixDeleteView,
    CompetencyProfileOfVacancySendView,
    CompetencyProfileOfVacancyGetView,
    CompetencyProfileOfVacancyPutView,
    CompetencyProfileOfVacancyDeleteView,
    UserCompetenceMatrixSendView,
    UserCompetenceMatrixGetView,
    UserCompetenceMatrixPutView,
    UserCompetenceMatrixDeleteView
)

urlpatterns = [
    path('technologies/', TechnologyGetView.as_view(), name='technologies'),
    path('technologies_send/', TechnologySendView.as_view(), name='technologies_send'),
    path('technologies_put/<int:pk>/', TechnologyPutView.as_view(), name='technologies_put'),
    path('technologies_delete/<int:pk>/', TechnologyDeleteView.as_view(), name='technologies_delete'),
    path('competentions/', CompetentionGetView.as_view(), name='competentions'),
    path('competentions_send/', CompetentionSendView.as_view(), name='competentions_send'),
    path('competentions_put/<int:pk>/', CompetentionPutView.as_view(), name='competentions_put'),
    path('competentions_delete_/<int:pk>/', CompetentionDeleteView.as_view(), name='competentions_delete_'),
    path('employers/', EmployerGetView.as_view(), name='employers'),
    path('employers_send/', EmployerSendView.as_view(), name='employers_send'),
    path('employers_put/<int:pk>/', EmployerPutView.as_view(), name='employers_put'),
    path('employers_delete/<int:pk>/', EmployerDeleteView.as_view(), name='employers_delete'),
    path('tables/', DatabaseTablesView.as_view(), name='database-tables'),
    path('tables/clear/', ClearTablesView.as_view(), name='clear-tables'),

    path('academic_competence_matrix/', AcademicCompetenceMatrixGetView.as_view(), name='academic_competence_matrix'),
    path('academic_competence_matrix_send/', AcademicCompetenceMatrixSendView.as_view(), name='academic_competence_matrix_send'),
    path('academic_competence_matrix_put/<int:pk>/', AcademicCompetenceMatrixPutView.as_view(), name='academic_competence_matrix_put'),
    path('academic_competence_matrix_delete/<int:pk>/', AcademicCompetenceMatrixDeleteView.as_view(), name='academic_competence_matrix_delete'),
    path('competency_profile_of_vacancy/', CompetencyProfileOfVacancyGetView.as_view(), name='competency_profile_of_vacancy'),
    path('competency_profile_of_vacancy_send/', CompetencyProfileOfVacancySendView.as_view(), name='competency_profile_of_vacancy_send'),
    path('competency_profile_of_vacancy_put/<int:pk>/', CompetencyProfileOfVacancyPutView.as_view(), name='competency_profile_of_vacancy_put'),
    path('competency_profile_of_vacancy_delete/<int:pk>/', CompetencyProfileOfVacancyDeleteView.as_view(), name='competency_profile_of_vacancy_delete'),
    path('user_competence_matrix/', UserCompetenceMatrixGetView.as_view(), name='user_competence_matrix'),
    path('user_competence_matrix_send/', UserCompetenceMatrixSendView.as_view(), name='user_competence_matrix_send'),
    path('user_competence_matrix_put/<int:pk>/', UserCompetenceMatrixPutView.as_view(), name='user_competence_matrix_put'),
    path('user_competence_matrix_delete/<int:pk>/', UserCompetenceMatrixDeleteView.as_view(), name='user_competence_matrix_delete'),
]