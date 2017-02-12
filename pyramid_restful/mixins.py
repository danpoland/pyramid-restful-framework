

__all__ = [
    'ListMixin',
    'RetrieveMixin',
    'CreateMixin',
    'UpdateMixin',
    'DestroyMixin'
]


class ListMixin:
    """

    """

    def list(self, request, *args, **kwargs):
        raise NotImplementedError('list method not implemented.')


class RetrieveMixin:
    """

    """

    def retrieve(self, request, *args, **kwargs):
        raise NotImplementedError('retrieve method not implemented.')


class CreateMixin:
    """

    """

    def create(self, request, *args, **kwargs):
        raise NotImplementedError('create method not implemented.')


class UpdateMixin:
    """

    """

    def update(self, request, *args, **kwargs):
        raise NotImplementedError('create method not implemented.')

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyMixin:
    """

    """

    def destroy(self, request, *args, **kwargs):
        raise NotImplementedError('destroy method not implemented.')
