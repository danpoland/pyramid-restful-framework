class BasePermission:
    """
    All permission classes should inherit from this class.
    """

    #: Override message to customize the message associated with the exception.
    message = None

    def has_permission(self, request, view):
        """
        Checked on every request to a view. Return ``True`` if permission is granted else ``False``.

        :param request: The request sent to the view.
        :param view: The instance of the view being accessed.
        :return: Boolean
        """

        return True

    def has_object_permission(self, request, view, obj):
        """
        Checked when a request is for a specific object. Return ``True`` if permission is granted else ``False``.

        :param request: The request sent to the view.
        :param view:  The instance of the view being accessed.
        :param obj: The object being accessed.
        :return: Boolean
        """

        return True
