import django_filters
from .models import PortfolioProject, ProjectTechnology


class PortfolioProjectFilter(django_filters.FilterSet):
    """
    Filter for portfolio projects
    """
    category = django_filters.ChoiceFilter(choices=PortfolioProject.CATEGORY_CHOICES)
    status = django_filters.ChoiceFilter(choices=PortfolioProject.STATUS_CHOICES)
    client = django_filters.CharFilter(field_name='client_name', lookup_expr='icontains')
    technologies = django_filters.CharFilter(method='filter_technologies')
    duration_min = django_filters.NumberFilter(field_name='duration_weeks', lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name='duration_weeks', lookup_expr='lte')
    team_size_min = django_filters.NumberFilter(field_name='team_size', lookup_expr='gte')
    team_size_max = django_filters.NumberFilter(field_name='team_size', lookup_expr='lte')
    featured = django_filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = PortfolioProject
        fields = ['category', 'status', 'client', 'technologies', 'featured']

    def filter_technologies(self, queryset, name, value):
        """
        Filter by multiple technologies (comma-separated)
        """
        if value:
            tech_names = [tech.strip() for tech in value.split(',')]
            return queryset.filter(technologies__name__in=tech_names).distinct()
        return queryset


class ProjectTechnologyFilter(django_filters.FilterSet):
    """
    Filter for project technologies
    """
    category = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProjectTechnology
        fields = ['category', 'name']