from . import modelmixins
from .viewsets import ViewSetMixin
from .modelviews import ModelAPIView


class ModelAPIViewset(ViewSetMixin, ModelAPIView):
    pass


class ReadOnlyModelViewSet(modelmixins.RetrieveModelMixin,
                           modelmixins.ListModelMixin,
                           ModelAPIViewset):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class ModelViewSet(modelmixins.CreateModelMixin,
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
