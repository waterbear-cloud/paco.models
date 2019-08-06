import pkg_resources

def list_service_plugins():
    """Return a dict of Service plugins"""
    return {
        entry_point.name: entry_point.load()
        for entry_point
        in pkg_resources.iter_entry_points('aim.services')
    }