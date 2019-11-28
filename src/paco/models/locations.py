from paco.models import schemas


def get_parent_by_interface(context, interface=schemas.IProject):
    """
    Walk up the tree until an object provides the requested Interface
    """
    max = 999
    while context is not None:
        if interface.providedBy(context):
            return context
        if schemas.IProject.providedBy(context):
            return None
        else:
            context = context.__parent__
        max -= 1
        if max < 1:
            raise TypeError("Maximum location depth exceeded. Model is borked!")


