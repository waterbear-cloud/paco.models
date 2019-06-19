from aim.models import schemas
from aim.models.locations import get_parent_by_interface
from aim.models import vocabulary
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
import zope.schema


def get_all_fields(obj):
    """
    Introspect an object for schemas it implements
    and return a dict of {fieldname: field_obj}
    """
    fields = {}
    try:
        # all interfaces implemented by obj
        interfaces = obj.__provides__.__iro__
    except AttributeError:
        # object without interfaces like a plain dict
        return {}
    for interface in interfaces:
        fields.update(zope.schema.getFields(interface))
    return fields


@implementer(schemas.INamed)
class Named():
    """
    An item which has a name and an optional title.
    A name is a unique, human-readable id.

    Every model is location-aware. This means it has a
    __name__ and __parent__. This lets the object live in
    a hiearchy such as a URL tree for a web application, object database
    or filesystem. AIM uses for the web app.
    """

    name = FieldProperty(schemas.INamed["name"])
    title = FieldProperty(schemas.INamed["title"])

    def __init__(self, name, __parent__):
        self.name = name
        self.__name__ = self.name
        self.__parent__ = __parent__

    @property
    def title_or_name(self):
        "It's a Plone classic!"
        if len(self.title) > 0:
            return self.title
        return self.name

@implementer(schemas.IName)
class Name():
    name = FieldProperty(schemas.IName["name"])

@implementer(schemas.IDeployable)
class Deployable():
    """
    A deployable resource
    """
    enabled = FieldProperty(schemas.IDeployable["enabled"])

    def is_enabled(self):
        """
        Returns True in a deployed state, otherwise False.
        Will walk up the tree, and if anything is set to "enabled: false"
        this will return False.
        """
        state = self.enabled
        # if current resource is already "enabled: false" simlpy return that
        if not state: return False

        context = self
        while context is not None:
            override = getattr(context, 'enabled', True)
            # once we encounter something higher in the tree with "enabled: false"
            # the lower resource is always False and we return that
            if not override: return False
            context = context.__parent__

        # walked right to the top and enabled is still true
        return True


class Regionalized():
    "Mix-in to allow objects to identify which region they are deployed in"

    @property
    def region_name(self):
        # region the resource is deployed in
        env_region = get_parent_by_interface(self, schemas.IEnvironmentRegion)
        return env_region.region

    @property
    def region_full_name(self):
        return vocabulary.aws_regions[self.region_name]['full_name']
