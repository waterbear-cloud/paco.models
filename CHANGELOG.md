Changelog for paco.models
=========================

6.3.5 (2020-01-23)
------------------

### Fixed

- Ubuntu awscli install had extra whitespace which could stop up UserData.


6.3.4 (2020-01-16)
------------------

### Added

- Added external_resource field for ICodeCommit.


6.3.3 (2020-01-09)
------------------

### Added

- The TextReference class was renamed PacoRefernce and can now be passed `schema_constraint` with the
  name or Schema that it must be a reference to.

- Support for `users` and `groups` in cfn-init. Invariant to prevent user name duplicating group name.

### Changed

- Temporarily disable chmod 400 check on .credentials to support filesystems that don't have permissions.

- CodeCommit contains CodeCommitRepositoryGroups and CodeCommitRepostory group objects instead of a two-level dict.
  Fixes docs and simplifies loader.

### Fixed

- `Lambad.add_environment_variable` passes parent.

6.3.2 (2020-01-06)
------------------

### Changed

- Schema clean-up, removed IMapping for all schemas that do not actually use it.

- Removed unused managed_udpates field for IApplication.


6.3.1 (2020-01-03)
------------------

### Added

- IRoute53HealthCheck has ip_address field.

- resource/snstopics.yaml is an alias for resource/notificationgroups.yaml

- raise_invalid_reference method to display helpful message when a ref look-up fails.

### Fixed

- cfn-init package sets were only loading for item, now loads all package types.

- ICloudWatchLogSource log_stream_name is a required field, if it's empty the agent won't launch.


6.3.0 (2019-12-03)
------------------

### Added

- ICloudWatchDashboard for CloudWatch Dashboard resources.

- Route53 Health Checks have domain_name and enable_sni fields.

### Changed

- Invariant errors in schema checks have non-confusing error message.


6.2.1 (2019-11-29)
------------------

- Fixes for the AIM to paco rename.


6.2.0 (2019-11-28)
------------------

### Changed

- Package rename: `paco.models` is now `paco.models`, consistent with the tool being
  renamed to `paco`.

- Top-level directories have been renamed to be consistent with their names in the model:
    NetworkEnvironments --> netenv
    Resources --> resource
    Services --> service
    Accounts --> account
    MonitorConfig --> monitor
  The loader will look for `NetworkEnvironments` and if it exists use the legacy names.

### Added

- Added support for AWS Backup Vault. There can now be global backup_vaults field in NetworkEnvironment YAML files.
  These can be overrode in EnvironmentDefault and EnvironmentRegion configuration sections.

- Added support for block_device_mappings for IASG.

6.1.0 (2019-11-06)
------------------

### Added

- Applications can be provisioned in the same environment more than once with a new
  "app{suffix}" syntax for an environments application keys.

- INotificationGroups has a regions field, if it is the default of ['ALL'] it will apply to
  all of a project's active regions. Otherwise is will just provision in the selected region(s).

- ICloudFormationInit for modelling AWS::CloudFormation::Init, which can be applied to
  the IASG.cfn_init field.

- ICloudWatchLogAlarm schema. ICloudWatchAlarm now has "type: Alarm" and if it is "type: LogAlarm"
  an ICloudWatchLogAlarm will be created which can be used to connect an alarm to a MetricFilter
  of a LogGroup.

- IDBParameterGrouups resource.

- IElastiCache has `description` and `cache_clusters` fields, while IElastiCacheRedis has `snapshot_retention_limit_days`
  and `snapshot_window` fields.

- IRDS has new `license_model`, `cloudwatch_logs_export` and `deletion_protection` fields.

- `global_role_name` field for IAM Role can be set to True and the RoleName
  will not be hashed. Can only be used for global Roles, otherwise if these
  Roles overlap per-environment, things will break!

- `monitoring.health_checks` which can contain HealthCheck Resources.
  IRoute53HealthCheck resource for Route53 health checks.

- `region_name` property can be overrode if a `overrode_region_name` attribute is set.

- Added a CodeBuild IAM Permission for IAM Users

- Added `resolve_ref` method to DeploymentPipelineConfiguration

- Added the EIP Application Resource and a support 'eip' field to the ASG resource for associating an EIP with a single instance ASG.

- Added AWS Cli install commands to vocabulary.

- Added `dns` to EIP Application Resource

- Added `cftemplate_iam_user_delegates_2019_10_02` legacy flag to make user delegate role stack names consistent with others.

- Added `route53_hosted_zone_2019_10_12` legacy flag for Route53 CFTemplate refactor.

- Added `route53_record_set_2019_10_16` legacy flag for the Route53 RecordSet refactor.

- Added `availability_zone` for locking in an ASG to a single Availability Zone.

- Added `parameter_group` to IElastiCache Application Resource

- Added `vpc_associations` to IPrivateHosted.

- Added `vpc_config` to the ILambda Application Resources

- Added `secrets_manager` to IIEnvironmentDefault.

- Added `ttl` to IDNS

- Added caching to instance AMI ID function.ref lookups.

- Added the EBS Application Resources.
  Added `ebs_volume_mounts` to IASG to mount volumes to single instance groups.

- Added `launch_options` to IASG as an IEC2LaunchOptions object. The initial option is update_packages which will update the linux distributions packages on launch.

- Added resolve_ref() to Resource in base.py as a catch all.

### Changed

- ISecurityGroupRule `source_security_group` was moved to IIngressRule and IEgressRule (finally!)
  has a `destination_security_group` field.

- `load_resources` was removed and you can now simply apply_attributes to
  an Application and it will recurse through app.groups.<groupname>.resources.<resourcename>
  without any external fiddling.

- Moved deepdiff CLI functions into `aim` project.

- IApplication is now IMonitorable. Alarms at the Application level must
  specify their Namespace and Dimensions.

- Changed RDS `primary_domain_name` and `primary_hosted_zone` to an IDNS object

### Fixed

- Alarm overrides are now cast to the schema of the field. Fixes "threshold: 10" loading as in int()
  when the schema expects a float().

6.0.0 (2019-09-27)
------------------

### Added

- ICloudWatchAlarms have `enable_ok_actions` and `enable_insufficient_data_actions` booleans
  that will send to the notification groups when the alarm enters the OK or INSUFFICIENT_DATA states.

- `references.get_model_obj_ref` will resolve an paco.ref to a model object
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

- CloudTrail defines CloudWatchLogGroup as a sub-object rather than an paco.ref.

- Alarms have `get_alarm_actions_paco_refs` renamed from `get_alarm_actions` as alarms can only provide
  paco.refs and need to get the ARNs from the stacks.

- NotificationGroups are now Resources. Now they have regular working paco.ref's.

5.0.0 (2019-08-26)
------------------

### Added

- New field `paco.models.reference.FileReference` which resolves the path and replaces
  the original value with the value of the file indicated by the path.
  IApiGatewayRestApi.body_file_location uses this new field.

- ApiGatewayRestApi and CloudWatchAlarm have a `cfn_export_dict` property that
  returns a new dict that can be used to created Troposphere resources.

- Added external_resource support to the ACM

- Added ReadOnly support to the Administrator IAMUserPermission

### Changed

 - Multi-Dimension Alarms now need to specify an `paco.ref` as the Value.

- Added IAMUser schemas and loading for IAM users.

- Added a CommaList() schema type for loading comma separated lists into schema.List()

- Moved aim reference generation into the Model. Model objects now have .paco_ref and
  .paco_ref_parts properties which contain their paco.ref reference.

- Renamed project['ne'] to project['netenv']

- Modified NatGateway segments to aim references

### Fixed

- Invariants were not being check for resources. Invariants need to be checked by the
  loader if they are not contained in a `zope.schema.Object` field, which will run the
  check behind the scenes.


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
  version. IProject now has an paco_project_version field to store this value.

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

- All references have been renamed to start with ``paco.ref`` for consistency.

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

- Services are loaded as entry_point plugins named `paco.services`

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

- Removed unused yaml config from pacodemo under fixtures.


1.0.1 (2019-06-19)
------------------

- Improvements to Python packaging metadata.


1.0.0 (2019-06-19)
------------------

- First open source release
