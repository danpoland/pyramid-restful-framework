from . import modelmixins
from .viewsets import ViewSetMixin
from .modelviews import ModelAPIView

__all__ = ['ModelAPIView', 'ReadOnlyModelViewSet', 'ModelCRUDViewSet']


class ModelAPIViewset(ViewSetMixin, ModelAPIView):
    pass


class ReadOnlyModelViewSet(modelmixins.RetrieveModelMixin,
                           modelmixins.ListModelMixin,
                           ModelAPIViewset):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class ModelCRUDViewSet(modelmixins.CreateModelMixin,
                   modelmixins.RetrieveModelMixin,
                   modelmixins.UpdateModelMixin,
                   modelmixins.DestroyModelMixin,
                   modelmixins.ListModelMixin,
                   ModelAPIViewset):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
