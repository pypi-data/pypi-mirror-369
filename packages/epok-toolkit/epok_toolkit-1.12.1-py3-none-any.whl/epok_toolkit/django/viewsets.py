# core/viewsets.py
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

class DefaultPagination(PageNumberPagination):
    """
    Clase de paginación por defecto para los ViewSets.
    Puedes personalizarla según tus necesidades.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class BaseOptimizedViewSet(viewsets.ModelViewSet):
    queryset = None
    write_serializer_class = None
    update_serializer_class = None
    simple_serializer_class = None
    full_serializer_class = None
    serializer_class = full_serializer_class
    extensions_auto_optimize = True

    permission_classes = [IsAuthenticated]

    pagination_class = DefaultPagination

    filterset_fields = []
    search_fields = []
    ordering_fields = []
    ordering = []

    def get_queryset(self):
        qs = super().get_queryset()
        model_cls = qs.model
        manager = model_cls._default_manager

        if hasattr(manager, 'simple') and self.action == 'list':
            qs = manager.simple()
        elif hasattr(manager, 'full'):
            qs = manager.full()

        if hasattr(manager, 'created_by'):
            return qs.filter(created_by=self.request.user)
        
        return qs

    def get_serializer_class(self):
        
        match self.action:
            case 'create':
                return self.write_serializer_class
            case 'update' | 'partial_update':
                return self.update_serializer_class
            case 'list':
                return self.simple_serializer_class
            case 'retrieve':
                return self.full_serializer_class
            case _:
                return super().get_serializer_class()
    
    
    def perform_create(self, serializer):
        if hasattr(serializer, 'created_by') and hasattr(serializer, 'updated_by'):
            serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        if hasattr(serializer, 'updated_by'):
            serializer.save(updated_by=self.request.user)
