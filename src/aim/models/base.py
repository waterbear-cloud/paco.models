from aim.models import schemas
from aim.models import vocabulary
from aim.models.exceptions import InvalidCFNMapping
from aim.models.locations import get_parent_by_interface
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models.references import Reference, get_model_obj_from_ref
import json
import troposphere
import zope.schema
import zope.schema.interfaces


def interface_seen(seen, iface):
    """Return True if interface already is seen.
    """
    for seen_iface in seen:
        if seen_iface.extends(iface):
            return True
    return False

def most_specialized_interfaces(context):
    """Get interfaces for an object without any duplicates.

    Interfaces in a declaration for an object may already have been seen
    because it is also inherited by another interface.
    """
    declaration = zope.interface.providedBy(context)
    seen = []
    for iface in declaration.flattened():
        if interface_seen(seen, iface):
            continue
        seen.append(iface)
    return seen

def marshall_fieldname_to_troposphere_value(obj, props, troposphere_name, field_name):
    """
    Return a value that can be used in a troposphere Properties dict.

    If field_name is a tuple, the first item is the field_name in the schema and the
    second item is the attribute (typically a @property) to return the modified value.
    """

    if type(field_name) == type(tuple()):
        mapping_field_name = field_name[0]
        mapping_attr_name = field_name[1]
    else:
        mapping_field_name = field_name
        mapping_attr_name = field_name

    for interface in most_specialized_interfaces(obj):
        fields = zope.schema.getFields(interface)
        if mapping_field_name in fields:
            # Field provides type information to help convert to Troposphere type
            field = fields[mapping_field_name]
            value = getattr(obj, mapping_attr_name)
            if zope.schema.interfaces.IBool.providedBy(field) and props[troposphere_name][0] == type(str()):
                if value:
                    return 'true'
                else:
                    return 'false'
            if isinstance(field, zope.schema.Text) and props[troposphere_name][0] == type(dict()):
                try:
                    return json.loads(value)
                except TypeError:
                    return None
            if value == {} or value == []:
                return None
            else:
                return value
        elif hasattr(obj, mapping_field_name):
            # supplied as a base property or attribute - these should return
            # types that troposphere expects
            value = getattr(obj, mapping_field_name)
            if value == {} or value == []:
                return None
            else: return value
        else:
            # Shouldn't get here unless the cfn_mapping is incorrect
            raise InvalidCFNMapping

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

class CFNExport():
    @property
    def cfn_export_dict(self):
        "CloudFormation export dictionary suitable for use in troposphere templates"
        result = {}
        for key, value in self.cfn_mapping.items():
            value = marshall_fieldname_to_troposphere_value(
                self,
                self.troposphere_props,
                key,
                value
            )
            if value != None:
                result[key] = value
        return result

@implementer(schemas.INamed)
class Named(CFNExport):
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

    @property
    def aim_ref_parts(self):
        "Bare aim.ref string to the object"
        obj = self
        parts = []

        # special case for global buckets
        if get_parent_by_interface(obj, schemas.IGlobalResources) and schemas.IS3Bucket.providedBy(obj):
            account = obj.account.split('.')[-1:][0]
            parts = ['resource','s3','buckets', account, obj.region, obj.name]
            return '.'.join(parts)

        parent = obj.__parent__
        while parent != None:
            parts.append(obj.name)
            obj = parent
            parent = obj.__parent__
        parts.reverse()
        return '.'.join(parts)

    @property
    def aim_ref(self):
        "aim.ref string to the object"
        return 'aim.ref ' + self.aim_ref_parts


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
            context = getattr(context, '__parent__', None)

        # walked right to the top and enabled is still true
        return True

@implementer(schemas.INameValuePair)
class NameValuePair():
    name = FieldProperty(schemas.INameValuePair['name'])
    value = FieldProperty(schemas.INameValuePair['value'])

class Regionalized():
    "Mix-in to allow objects to identify which account and region they are deployed in"

    @property
    def account_name(self):
        account_cont = get_parent_by_interface(self, schemas.IAccountContainer)
        if account_cont != None:
            return account_cont.name
        env_region = get_parent_by_interface(self, schemas.IEnvironmentRegion)
        project = get_parent_by_interface(self)
        if env_region != None:
            return get_model_obj_from_ref(env_region.network.aws_account, project).name
        raise AttributeError('Could not determine account for {}'.format(self.name))

    @property
    def region_name(self):
        # region the resource is deployed in
        region = get_parent_by_interface(self, schemas.IRegionContainer)
        if region != None:
            return region.name
        # Global buckets have a region field
        if schemas.IS3Bucket.providedBy(self):
            return self.region
        raise AttributeError('Could not determine region for {}'.format(self.name))

    @property
    def region_full_name(self):
        return vocabulary.aws_regions[self.region_name]['full_name']

    @property
    def region_short_name(self):
        return vocabulary.aws_regions[self.region_name]['short_name']

@implementer(schemas.IDNSEnablable)
class DNSEnablable():
    dns_enabled = FieldProperty(schemas.IDNSEnablable['dns_enabled'])

    def is_dns_enabled(self):
        """
        Returns True in a deployed state, otherwise False.
        Will walk up the tree, and if anything is set to "enabled: false"
        this will return False.
        """
        state = self.dns_enabled
        # if current resource is already "enabled: false" simlpy return that
        if not state: return False

        context = self
        while context is not None:
            override = getattr(context, 'dns_enabled', True)
            # once we encounter something higher in the tree with "enabled: false"
            # the lower resource is always False and we return that
            if not override: return False
            context = getattr(context, '__parent__', None)

        # walked right to the top and enabled is still true
        return True

@implementer(schemas.IResource)
class Resource(Named, Deployable, Regionalized, DNSEnablable):
    "Resource"
    type = FieldProperty(schemas.IResource['type'])
    resource_name = FieldProperty(schemas.IResource['resource_name'])
    resource_fullname = FieldProperty(schemas.IResource['resource_fullname'])
    order = FieldProperty(schemas.IResource['order'])
    change_protected = FieldProperty(schemas.IResource['change_protected'])

    def get_account(self):
        """
        Return the Account object that this resource is provisioned to
        """
        env_reg = get_parent_by_interface(self, schemas.IEnvironmentRegion)
        project = get_parent_by_interface(self, schemas.IProject)
        return get_model_obj_from_ref(env_reg.network.aws_account, project)

@implementer(schemas.IAccountRef)
class AccountRef():
    account = FieldProperty(schemas.IAccountRef['account'])


@implementer(schemas.IAccountContainer)
class AccountContainer(Named, Regionalized, dict):
    pass

@implementer(schemas.IRegionContainer)
class RegionContainer(Named, Regionalized, dict):
    pass
