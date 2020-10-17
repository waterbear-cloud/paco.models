import zope.schema
import zope.interface

class InvalidPacoReferenceString(zope.schema.ValidationError):
    __doc__ = 'PacoReference must be of type (string)'

class InvalidPacoReferenceStartsWith(zope.schema.ValidationError):
    __doc__ = "PacoReference must begin with 'paco.ref'"

class InvalidPacoReferenceRefType(zope.schema.ValidationError):
    __doc__ = "PacoReference 'paco.ref must begin with: netenv | resource | accounts | function | service"

class FileReference():
    pass

class StringFileReference(FileReference, zope.schema.Text):
    """Path to a string file on the filesystem"""

    def constraint(self, value):
        """
        Validate that the path resolves to a file on the filesystem
        """
        return True
        # ToDo: how to get the PACO_HOME and change to that directory from here?
        #path = pathlib.Path(value)
        #return path.exists()

class BinaryFileReference(FileReference, zope.schema.Bytes):
    """Path to a binary file on the filesystem"""

    def constraint(self, value):
        """
        Validate that the path resolves to a file on the filesystem
        """
        return True

class YAMLFileReference(FileReference, zope.schema.Object):
    """Path to a YAML file"""

    def __init__(self, **kw):
        self.schema = zope.interface.Interface
        self.validate_invariants = kw.pop('validate_invariants', True)
        super(zope.schema.Object, self).__init__(**kw)

def is_ref(paco_ref, raise_enabled=False):
    """Determines if the string value is a Paco reference"""
    if type(paco_ref) != type(str()):
        if raise_enabled: raise InvalidPacoReferenceString
        return False
    if paco_ref.startswith('paco.ref ') == False:
        if raise_enabled: raise InvalidPacoReferenceStartsWith
        return False
    ref_types = ["netenv", "resource", "accounts", "function", "service"]
    for ref_type in ref_types:
        if paco_ref.startswith('paco.ref %s.' % ref_type):
            return True
    if raise_enabled: raise InvalidPacoReferenceRefType
    return False

class PacoReference(zope.schema.Text):

    def __init__(self, *args, **kwargs):
        self.str_ok = False
        self.schema_constraint = ''
        if 'str_ok' in kwargs.keys():
            self.str_ok = kwargs['str_ok']
            del kwargs['str_ok']
        # schema_constraint is a string name of an ISchema
        # if a Schema is passed, it is converted to a string
        if 'schema_constraint' in kwargs.keys():
            self.schema_constraint = kwargs['schema_constraint']
            if hasattr(self.schema_constraint, '__name__'):
                self.schema_constraint = self.schema_constraint.__name__
            del kwargs['schema_constraint']
        super().__init__(*args, **kwargs)

    def constraint(self, value):
        """
        Limit text to the format 'word.ref chars_here.more-chars.finalchars100'
        """
        if self.str_ok and is_ref(value) == False:
            if isinstance(value, str) == False:
                raise InvalidPacoReferenceString
                #return False
            return True

        return is_ref(value, raise_enabled=True)
