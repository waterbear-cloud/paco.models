from aim.models.locations import get_parent_by_interface
from aim.models import schemas

def get_formatted_model_context(obj):
    """Return a formatted string describing a model object in it's context
    """
    # ToDo: should work for all NetEnv objects, will need expanding to
    # handle Services and other objects
    netenv = get_parent_by_interface(obj, schemas.INetworkEnvironment)
    env = get_parent_by_interface(obj, schemas.IEnvironment)
    envreg = get_parent_by_interface(obj, schemas.IEnvironmentRegion)
    app = get_parent_by_interface(obj, schemas.IApplication)
    group = get_parent_by_interface(obj, schemas.IResourceGroup)
    out = ""
    if netenv != None:
        if netenv.title:
            out += "Network Environment: {} ({})\n".format(netenv.title, netenv.name)
        else:
            out += "Network Environment: " + netenv.name + "\n"
    if env != None:
        if env.title:
            out += "Environment: {} ({})\n".format(env.title, env.name)
        else:
            out += "Environment: " + env.name + "\n"
    if envreg != None:
        out += "Account: " + envreg.network.aws_account + "\n"
        if envreg.title:
            out += "Region: {} ({})\n".format(envreg.title, envreg.name)
        else:
            out += "Region: " + envreg.name + "\n"
    if app != None:
        if app.title:
            out += "Application: {} ({})\n".format(app.title, app.name)
        else:
            out += "Application: " + app.name + "\n"
    if group != None:
        if group.title:
            out += "Resrouce Group: {} ({})\n".format(group.title, group.name)
        else:
            out += "Resource Group: " + group.name + "\n"
    return out
