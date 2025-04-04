from django.apps import AppConfig

class MonitoringModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.external.learning_analytics.visualization_reporting_submodule'
    label = 'learning_analytics_visualization_reporting_submodule'