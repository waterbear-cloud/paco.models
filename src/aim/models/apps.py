"""
All things Application Engine.
"""
from aim.models.base import Named, Deployable, Regionalized
from aim.models.metrics import Monitorable
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models import loader
from aim.models.vocabulary import application_group_types
from aim.models.locations import get_parent_by_interface


@implementer(schemas.IApplicationEngines)
class ApplicationEngines(Named, dict):
    pass

@implementer(schemas.IApplicationEngine)
class ApplicationEngine(Named, Deployable, Regionalized, dict):
    managed_updates = FieldProperty(schemas.IApplicationEngine['managed_updates'])
    groups = FieldProperty(schemas.IApplicationEngine['groups'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.groups = ResourceGroups('groups', self)

    # Returns a list of groups sorted by 'order'
    def groups_ordered(self):
        group_config_list = []
        for item_group_id, item_group_config in self.groups.items():
            new_group_config = [item_group_id, item_group_config]
            insert_idx = 0
            for group_config in group_config_list:
                if item_group_config.order < group_config[1].order:
                    group_config_list.insert(insert_idx, new_group_config)
                    break
                insert_idx += 1
            else:
                group_config_list.append(new_group_config)

        return group_config_list

@implementer(schemas.IApplication)
class Application(ApplicationEngine, Regionalized):

    def get_resource_by_name(self, resource_name):
        """
        Iterate through resource groups and find resource
        of the given name.
        """
        resource = None
        for group in self.groups.values():
            if resource_name in group.resources.keys():
                return group.resources[resource_name]
        return resource

    def get_all_group_types(self):
        """
        Iterate through all groups and return a list of all types in use.
        Results are always sorted in a fixed order.
        """
        types = {}
        results = []
        for group in self.groups.values():
            if group.type not in types:
                types[group.type] = True
        for sorted_type in application_group_types:
            if sorted_type in types:
                results.append(sorted_type)
        return results

    def list_alarm_info(self, group_name=None):
        """
        Return a list of dicts of Alarms for the Application. The dict contains
        the group and resource that the Alarm belongs to for context:

            {
                'alarm': CloudWatchAlarm,
                'group': ResourceGroup,
                'resource': Resource
            }

        The `group_name` will limit results to a specifc ResourceGroup.
        """
        alarm_info = []
        for group in self.groups.values():
            if group_name and group.__name__ != group_name:
                continue
            for resource in group.resources.values():
                if hasattr(resource, 'monitoring'):
                    if hasattr(resource.monitoring, 'alarm_sets'):
                        for alarm_set in resource.monitoring.alarm_sets.values():
                            for alarm in alarm_set.values():
                                alarm_info.append({
                                    'alarm': alarm,
                                    'resource': resource,
                                    'group': group
                                })
        return alarm_info

    def resolve_ref(self, ref):
        pass

@implementer(schemas.IResourceGroups)
class ResourceGroups(Named, dict):
    "ResourceGroups"

    def all_groups_by_type(self, group_type):
        "Return all ResourceGroups contained of a specific type"
        results = []
        for group in self.values():
            if group.type == group_type:
                results.append(group)
        return results


@implementer(schemas.IResourceGroup)
class ResourceGroup(Named, dict):

    def resources_ordered(self):
        "Returns a list of a group's resources sorted by 'order'"
        res_config_list = []
        for item_res_id, item_res_config in self.resources.items():
            new_res_config = [item_res_id, item_res_config]
            insert_idx = 0
            for res_config in res_config_list:
                if item_res_config.order < res_config[1].order:
                    res_config_list.insert(insert_idx, new_res_config)
                    break
                insert_idx+=1
            else:
                res_config_list.append(new_res_config)

        return res_config_list

    def list_alarm_info(self):
        app = get_parent_by_interface(self, schemas.IApplication)
        return app.list_alarm_info(group_name=self.__name__)
