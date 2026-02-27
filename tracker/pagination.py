"""
Pagination configuration for tracker app.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Standard pagination with 10 items per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results to return per page.'
    max_page_size = 100
    page_query_description = 'A page number within the paginated result set.'
