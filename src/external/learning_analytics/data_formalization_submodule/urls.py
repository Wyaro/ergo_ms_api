from django.urls import path
from src.external.learning_analytics.data_formalization_submodule.views import (
    SpecialityView,
    CurriculumView,
    TechnologyView,
    CompetencyView,
    BaseDisciplineView,
    DisciplineView,
    VacancyView,
    ACMView,
    VCMView,
    UCMView,
    LoadSampleData
)

urlpatterns = [
    path('specialities/', SpecialityView.as_view({'get': 'list', 'post': 'create'}), name='specialities'),
    path('specialities/<int:pk>/', SpecialityView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='speciality-detail'),

    path('curriculums/', CurriculumView.as_view({'get': 'list', 'post': 'create'}), name='curriculums'),
    path('curriculums/<int:pk>/', CurriculumView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='curriculum-detail'),

    path('technologies/', TechnologyView.as_view({'get': 'list', 'post': 'create'}), name='technologies'),
    path('technologies/<int:pk>/', TechnologyView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='technology-detail'),

    path('competencies/', CompetencyView.as_view({'get': 'list', 'post': 'create'}), name='competencies'),
    path('competencies/<int:pk>/', CompetencyView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='competency-detail'),

    path('base_disciplines/', BaseDisciplineView.as_view({'get': 'list', 'post': 'create'}), name='base_disciplines'),
    path('base_disciplines/<int:pk>/', BaseDisciplineView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='base_discipline-detail'),

    path('disciplines/', DisciplineView.as_view({'get': 'list', 'post': 'create'}), name='disciplines'),
    path('disciplines/<int:pk>/', DisciplineView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='discipline-detail'),

    path('vacancies/', VacancyView.as_view({'get': 'list', 'post': 'create'}), name='vacancies'),
    path('vacancies/<int:pk>/', VacancyView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='vacancy-detail'),

    path('acms/', ACMView.as_view({'get': 'list', 'post': 'create'}), name='acms'),
    path('acms/<int:pk>/', ACMView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='acm-detail'),

    path('vcms/', VCMView.as_view({'get': 'list', 'post': 'create'}), name='vcms'),
    path('vcms/<int:pk>/', VCMView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='vcm-detail'),

    path('ucms/', UCMView.as_view({'get': 'list', 'post': 'create'}), name='ucms'),
    path('ucms/<int:pk>/', UCMView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='ucm-detail'),

    path('technologies/loadsampledata/', LoadSampleData.as_view(), name='load-sample-technologies'),
]