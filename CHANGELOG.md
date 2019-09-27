Changelog for aim.models
=================

6.0.0 (2019-09-27)
------------------

### Added

- ICloudWatchAlarms have `enable_ok_actions` and `enable_insufficient_data_actions` booleans
  that will send to the notification groups when the alarm enters the OK or INSUFFICIENT_DATA states.

- `references.get_model_obj_ref` will resolve an aim.ref to a model object
  and won't attempt to do Stack output lookups.

- Service plug-ins are loaded according to an `initilization_order` integer
  that each plug-in can supply. If no integer is supplied, loading for unordered
  plug-ins count up from 1000.

- Minimal API Gateway models for Methods, Resources, Models and Stages.

- S3Bucket NotificationConfiguration for Lambdas.

- S3Bucket has `get_bucket_name()` to return the full computed bucket name.

- IGlobalResources for project['resource'] to contain config from the ./Resources/ directory.
  Resources such as S3 and EC2 now implement INamed and are loaded into project['resource'].

- ISNSTopic has `cross_account_access` which grants `sns:Publish` to all accounts in the AIM Project.

- IAccountContainer and IRegionContainer are lightweight containers for account and region information.
  They can be used by Services that want to set-up Resources in a multi-account, multi-region manner.

### Changed

- CloudTrail defines CloudWatchLogGroup as a sub-object rather than an aim.ref.

- Alarms have `get_alarm_actions_aim_refs` renamed from `get_alarm_actions` as alarms can only provide
  aim.refs and need to get the ARNs from the stacks.

- NotificationGroups are now Resources. Now they have regular working aim.ref's.

5.0.0 (2019-08-26)
------------------

### Added

- New field `aim.models.reference.FileReference` which resolves the path and replaces
  the original value with the value of the file indicated by the path.
  IApiGatewayRestApi.body_file_location uses this new field.

- ApiGatewayRestApi and CloudWatchAlarm have a `cfn_export_dict` property that
  returns a new dict that can be used to created Troposphere resources.

- Added external_resource support to the ACM

- Added ReadOnly support to the Administrator IAMUserPermission

### Changed

 - Multi-Dimension Alarms now need to specify an `aim.ref` as the Value.

- Added IAMUser schemas and loading for IAM users.

- Added a CommaList() schema type for loading comma separated lists into schema.List()

- Moved aim reference generation into the Model. Model objects now have .aim_ref and
  .aim_ref_parts properties which contain their aim.ref reference.

### Fixed

- Invariants were not being check for resources. Invariants need to be checked by the
  loader if they are not contained in a `zope.schema.Object` field, which will run the
  check behind the scenes.

### Changed

- Renamed project['ne'] to project['netenv']

- Modified NatGateway segments to aim references

4.0.0 (2019-08-21)
------------------

### Added

 - IVPCPeering and IVPCPeeringRoute have been added to the model for VPC Peering support.

 - Added a CloudTrail schema configured in `Resources/CloudTrail.yaml`.

 - IS3BucketPolicy now has `principal` and `condition` fields.
   `principal` can be either a Key-Value dictionary, where the key is either 'AWS', 'Service', etc.
   and the value can be either a String or a List. It is an alternate to the `aws` field, which will
   remain for setting simpler AWS-only principals.
   The `condition` field is a Key-Value dictionary of Key-Value filters.

 - Alarm now has 'get_alarm_actions' and 'get_alarm_description' to help construct alarms.

 - CloudTrail has a 'get_accounts' which will resolve the CloudTrail.accounts field to a list
   of Account objects in the model.

 - IAlarm has `description` and `runbook_url` fields.

 - CodePipeBuildDeploy.resolve_ref() function covers wider scope of ref lookups

 - Added VPCPeering to the model.

 - Added IElastiCache and IElastiCacheRedis to the model.

### Changed

 - `MonitorConfig/LogSets.yaml` has been renamed to `MonitorConfig/Logging.yaml`. CloudWatch
   logging is under the top level `cw_logging` key. The schema has been completely reworked
   so that LogGroups and LogSets are properly modelled.

 - IAccount.region, IEC2KeyPair.region and ICredentials.aws_default_region no longer have
   `us-west-2` as a default. The region needs to be explicity set.

### Fixed

 - IAlarm.classification is now a required field.


3.1.0 (2019-08-08)
------------------

### Added

- aim-project-version.txt file in the root directory can now contain the AIM Project YAML
  version. IProject now has an aim_project_version field to store this value.

- ICloudWatchAlarm gets a namespace field. Can be used to override the default
  Resource namespace, for example, use 'CWAgent' for the CloudWatch agent metrics.

- IResource now has a resource_fullname field. The fullname is the name needed to
  specify for a metric in a CloudWatch Alarm.

- ICloudWatchAlarm now has a dimensions field, which is a List of Dimension objects.

- ITargetGroup now inherits from IResource. It loads resource_name from outputs.


3.0.0 (2019-08-06)
------------------

### Added

- New `MonitorConfig/NotificationGroups.yaml` that contains subscription groups for notifications.

- sdb_cache field for Lambda.

- Lambda can have alarms.

- ISNSTopic and ISNSTopicSubscription to model SNS.

### Changed

- All references have been renamed to start with ``aim.ref`` for consistency.

- AlarmSets, AlarmSet and Alarm all now implement INamed and
  are locatable in the model

- Service plugins can load their outputs


2.0.0 (2019-07-23)
------------------

### Added

- Schema for Notifications for subscribing to Alarms

- Added S3Resource for Resources/S3.yml configuration

- Added Lambda resolve_ref support

### Changed

- Services are loaded as entry_point plugins named `aim.services`

- Refactored the models applications, resources, and services.

- Renamed IRoute53 to IRoute53Resource.

### Fixed

 - CloudWatchAlarms now validate a classification field value of
   'performance', 'health' or 'security' is supplied.


1.1.0 (2019-07-06)
------------------

### Added

- Added function.ref to be able to look-up latest AMI IDs

- Added more constraints to the schemas.

- Added default to IS3Bucket.policy

- Added Route53 to schema and model

- Added redirect to Listner rules in the ALB

### Changed

- Description attribute for Fields is now used to describe constraints.

- Ported CodeCommit to schema and model

- Refactored S3 to use Application StackGroup

- CPBD artifacts s3 bucket now uses S3 Resource in NetEnv yaml instead

- Converted the ALB's listener and listener rules to dicts from lists

### Removed

- Removed unused yaml config from aimdemo under fixtures.


1.0.1 (2019-06-19)
------------------

- Improvements to Python packaging metadata.


1.0.0 (2019-06-19)
------------------

- First open source release
