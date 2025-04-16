from django.urls import path
from src.external.learning_analytics.data_formalization_submodule.views import (
    SpecialityGetView,
    SpecialitySendView,
    SpecialityPutView,
    SpecialityDeleteView,
    CurriculumGetView,
    CurriculumSendView,
    CurriculumPutView,
    CurriculumDeleteView,
    TechnologyGetView,
    TechnologySendView,
    TechnologyPutView,
    TechnologyDeleteView,
    CompetencyGetView,
    CompetencySendView,
    CompetencyPutView,
    CompetencyDeleteView,
    BaseDisciplineGetView,
    BaseDisciplineSendView,
    BaseDisciplinePutView,
    BaseDisciplineDeleteView,
    DisciplineGetView,
    DisciplineSendView,
    DisciplinePutView,
    DisciplineDeleteView,
    VacancyGetView,
    VacancySendView,
    VacancyPutView,
    VacancyDeleteView,
    ACMGetView,
    ACMSendView,
    ACMPutView,
    ACMDeleteView,
    VCMGetView,
    VCMSendView,
    VCMPutView,
    VCMDeleteView,
    UCMGetView,
    UCMSendView,
    UCMPutView,
    UCMDeleteView,
)

# Определение маршрутов для API
urlpatterns = [
    # Speciality
    path('specialities/', SpecialityGetView.as_view(), name='specialities_get'),
    path('specialities/create/', SpecialitySendView.as_view(), name='specialities_create'),
    path('specialities/<int:pk>/update/', SpecialityPutView.as_view(), name='specialities_update'),
    path('specialities/<int:pk>/delete/', SpecialityDeleteView.as_view(), name='specialities_delete'),

    # Curriculum
    path('curriculums/', CurriculumGetView.as_view(), name='curriculums_get'),
    path('curriculums/create/', CurriculumSendView.as_view(), name='curriculums_create'),
    path('curriculums/<int:pk>/update/', CurriculumPutView.as_view(), name='curriculums_update'),
    path('curriculums/<int:pk>/delete/', CurriculumDeleteView.as_view(), name='curriculums_delete'),

    # Technology
    path('technologies/', TechnologyGetView.as_view(), name='technologies_get'),
    path('technologies/create/', TechnologySendView.as_view(), name='technologies_create'),
    path('technologies/<int:pk>/update/', TechnologyPutView.as_view(), name='technologies_update'),
    path('technologies/<int:pk>/delete/', TechnologyDeleteView.as_view(), name='technologies_delete'),

    # Competency
    path('competencies/', CompetencyGetView.as_view(), name='competencies_get'),
    path('competencies/create/', CompetencySendView.as_view(), name='competencies_create'),
    path('competencies/<int:pk>/update/', CompetencyPutView.as_view(), name='competencies_update'),
    path('competencies/<int:pk>/delete/', CompetencyDeleteView.as_view(), name='competencies_delete'),

    # BaseDiscipline
    path('base_disciplines/', BaseDisciplineGetView.as_view(), name='base_disciplines_get'),
    path('base_disciplines/create/', BaseDisciplineSendView.as_view(), name='base_disciplines_create'),
    path('base_disciplines/<int:pk>/update/', BaseDisciplinePutView.as_view(), name='base_disciplines_update'),
    path('base_disciplines/<int:pk>/delete/', BaseDisciplineDeleteView.as_view(), name='base_disciplines_delete'),

    # Discipline
    path('disciplines/', DisciplineGetView.as_view(), name='disciplines_get'),
    path('disciplines/create/', DisciplineSendView.as_view(), name='disciplines_create'),
    path('disciplines/<int:pk>/update/', DisciplinePutView.as_view(), name='disciplines_update'),
    path('disciplines/<int:pk>/delete/', DisciplineDeleteView.as_view(), name='disciplines_delete'),

    # Vacancy
    path('vacancies/', VacancyGetView.as_view(), name='vacancies_get'),
    path('vacancies/create/', VacancySendView.as_view(), name='vacancies_create'),
    path('vacancies/<int:pk>/update/', VacancyPutView.as_view(), name='vacancies_update'),
    path('vacancies/<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancies_delete'),

    # ACM
    path('acms/', ACMGetView.as_view(), name='acms_get'),
    path('acms/create/', ACMSendView.as_view(), name='acms_create'),
    path('acms/<int:pk>/update/', ACMPutView.as_view(), name='acms_update'),
    path('acms/<int:pk>/delete/', ACMDeleteView.as_view(), name='acms_delete'),

    # VCM
    path('vcms/', VCMGetView.as_view(), name='vcms_get'),
    path('vcms/create/', VCMSendView.as_view(), name='vcms_create'),
    path('vcms/<int:pk>/update/', VCMPutView.as_view(), name='vcms_update'),
    path('vcms/<int:pk>/delete/', VCMDeleteView.as_view(), name='vcms_delete'),

    # UCM
    path('ucms/', UCMGetView.as_view(), name='ucms_get'),
    path('ucms/create/', UCMSendView.as_view(), name='ucms_create'),
    path('ucms/<int:pk>/update/', UCMPutView.as_view(), name='ucms_update'),
    path('ucms/<int:pk>/delete/', UCMDeleteView.as_view(), name='ucms_delete'),
]