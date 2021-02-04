Changelog for paco.models
=========================

7.7.6 (2021-02-03)
------------------

- Add `external_resource` to `ICloudWatchLogGroup`.


7.7.5 (2021-01-29)
------------------

- Add `script_manager` to `IASG` for ECR Deployments.


7.7.4 (2021-01-13)
------------------

### Changed

- EC2 `launch_options.codedeploy_agent` was defaulting to True. It is now False by default.

### Fixed

- Fixed DynamoDB Table resolve_ref.

7.7.3 (2021-01-05)
------------------

### Added

- ECS ASG Capacity Provider has a `managed_instance_protection` field.

7.7.2 (2021-01-05)
------------------

### Added

- ECS Service has a `capacity_providers` field for ECS Capacity Providers.

- ECS Cluster has a `capacity_providers` field that is the default if no `launch_type` is specified.

7.7.1 (2020-12-31)
------------------

### Added

- ReleasePhases for DeploymentPipeline CodeBuild actions.

7.7.0 (2020-12-23)
------------------

### Changed

- Add support for Network Load Balaners. New `IloadBalancer` base class and `IApplicationLoadBalancer` and `INetworkLoadBalancer` classes.
  The `LBApplication` class has been renamed to `ApplicationLoadBalancer`.

### Added

- AlarmDescription metadata now includes a 'ref' field, which is the paco.ref parts to the Alarm resource.

- Constraint for `IS3BucketPolicy` and `IStatement` for the `condition` field to check for valid AWS Constraint.

- `IBackupPlan` has new `copy_actions` field.

- Initial schemas for DynamoDB.

### Fixed

- AdminIAMUsers for `IAccount` is now a container with a `name`.

- ListenerRules for `IListener` for load balancers is now a container with a `name`.

- CloudFrontOrigins for `ICloudFront` is now a container with a `name`.

- CloudFrontFactories for `ICloudFront` is now a container with a `name`.


7.6.1 (2020-11-12)
------------------

### Added

- Added `codedeploy_agent` to field to `EC2LaunchOptions`.


7.6.0 (2020-11-07)
------------------

### Fixed

 - Cross-account netenv refs are properly detected and don't get munged.

 - `add_stack_hooks` can be called before or **after** template initialization and be registred.

 - IoTPolicy now works with Services.

### Added

- Add `add_paco_suffix` field to `S3Bucket` resource.

- Lambda Triggers for CognitoUserPool

- Path fields that go to a local path can now use `~/` to expand to the home directory path.

- `IECSServices` has `setting_groups` field.

- `IApiGatewayResource` has `child_resources` and `enable_cors` fields.

- New method `Project.get_all_resources_by_type()` which depends upon a Project resource registry which
  contains a dict of all application resources grouped by type. Easily query across applications!

- loader has a `validate_local_paths` to allow loading the model from a CI/CD or other environments
  that may not have local paths available.

- New `IBinaryFileReference` to load binary files.

- CloudFront LambdaFunctionAssociation support and Lambda@Edge initial support.

- Initial Cognito support with resource types for `ICognitoUserPool` and `ICognitoIdentityPool`.

- TargetGroup has a `target_type` field.

- ECSServices has Fargate support.

- ECSService has a `target_tracking_scaling_policies` for service scaling.

- Helpful errors for misconfigured AlarmSets.

- Added `monitoring` to `ECSServices` and `ECSCluster`.

- Added `ecr_repositories` to `IDeploymentPipelineBuildCodeBuild` to simplify declaring
  ECR Repository permissions.

- Added a `add_stack_hooks` to `paco.models.base.Resource`.

### Changed

- YAML file loading now accounts for case-sensitive filesystems, but allowing for directory names and
  filenames to either be lower-case or capitalized.

- Renamed `IApiGatewayMethod` for ApiGatewayRestApi from `resource_id` to `resource_name`
  to better reflect the name matches the resources of the gatewway.

- Renamed `IAWSCertificateManager` to `IACM` so that it matches it's Resource Type name.

- ApiGatewayRestApi doesn't supply a name in it's CloudFormation export


7.5.0 (2020-09-17)
------------------

### Added

- Added `paco.models.registry` as a place to contain configuration that extends or changes Paco.

- Added `IIAMUserResource` as an application-level IAMUser resource.

- Minimal `IPinpointApplication` schema for AWS Pinpoint support.

- AlarmSets and CWLogging are loaded into `project.monitor`. These are used by `paco describe` feature.

- Added `extend_base_schema` hook to the loader to allows Services to extend schemas before the loader loads.

- Container loader can load empty objects (objects with no fields, only a name)

### Changed

- `paco.modes.services.list_service_plugins` changed to `list_enabled_services`. Returns ony enabed services
  in a dict format.

- `IIAMUserProgrammaticAccess` changed to `IEnablable` and now defaults to True.

- The `ICloudFrontCustomErrorResponse` field `error_caching_min_ttl` has a default of 300.

- PyLance detected fixes: re-arrange `IRDS` schema so it no longer provides `IResource`.
  https://github.com/microsoft/pylance-release


7.4.0 (2020-07-14)
------------------

### Added

- DeploymentPipeline now has an `ECR.Source` action.

- Added `IEnablable` that is the same as `IDeployable` except it defaults to true.

- Added `IRDSMysqlAurora` and `IRDSPostgresqlAurora` for Aurora support.

- Added users and groups to `resource/ec2.yaml` and `ssh_access` to IASG.

- ECSSerivce additional fields for deployment_maximum_percent, deployment_minimum_healthy_percent and
  health_check_grace_period_seconds.

- ISecretManagerSecret now has an `account` field to specify it belongs to a specific account.

### Changed

- `IDeploymentPipelineStageAction` uses IEnablable so that deployment actions are enabled by default.

- `ISNSTopic` uses IEnablable so that topics are enabled by default.

7.3.0 (2020-06-22)
------------------

### Added

- ICodeCommitUser has a permissions field that can be ReadWrite or ReadOnly.

- IDeploymentPipelineBuildCodeBuild has a `buildspec` field.

- New `paco.models.gen_vocabulary` of vocabularies dynamically generated from AWS API calls. Added vocabulary for
  AWS AMI Ids.

- `paco.ref function` now supports a `:` synatx to pass extra context to a function

- New `paco.aws` package with `paco.ref function` calls. First call is `paco.aws.ami_id:latest.amazon-linux-2-ecs`

- ECS Cluster with initial EC2 AutoScalingGroup support.

- New `resource/sns.yaml` fiel with SNS global resource to allow SNS Topics and Subscriptions to be provisioned
  across any combination of accounts/regions.

- AWS Config support added in ``resource/config.yaml``.

- ICloudTrail now has a ``kms_users`` field which is a list of IAM Users granted access to encrypted CloudTrail logs.

### Changed

- ISNSTopics has a locations field. This only applies for `resource/sns.yaml`

- The IASG `instance_iam_role` field is no longer a required field.

- The home / config_folder is now a pathlib.Path object.


7.2.0 (2020-05-09)
------------------

### Added

- Added ``IASG.launch_options.ssm_agent`` to indicate if SSM Agent should be installed.

- Added ``IRDSPostgresql`` with RDS for Postgresql support. Added complete list of RDS EngineVerions for
  Mysql and Postgresql to vocabulary.

### Changed

- Vocabulary for instance_ami_type expanded to include OS major release or other significant attributes.

- Added ``poll_for_source_changes`` to IDeploymentPipelineSourceGitHub.

- ``Lambda:code:zipfile`` can now be a path to a local directory.

7.1.0 (2020-04-04)
------------------

### Migration

- ASG field's ``update_policy_max_batch_size`` and ``update_policy_min_instances_in_service`` are removed.
  Instead use the ASG field ``rolling_update_policy`` and set ``max_batch_size`` and ``min_instances_in_service``.

### Added

- New ``managed_policies`` for IIAMUserPermissionCustomPolicy to allow easily adding AWS Managed Policies.

- IIoTAnalyticsPipeline, IIoTTopicRule and IIoTPolicy schemas and implementation to support core IoT
  ingestion and analysis.

- IListener has an ``ssl_policy`` for setting the SslPolicy for a SSL Listener.

7.0.2 (2020-03-14)
------------------

### Fixed

- Restore cfn-init wget command.


7.0.1 (2020-03-14)
------------------

### Added

- IDeploymentPipelineDeployS3 has input_artifacts field for Stages/Actions.

7.0.0 (2020-03-06)
------------------

### Migration

- NotifcationGroups was renamed to SNSTopics.
  Migration: git mv resource/NotificationGroups.yaml resource/snstopics.yaml

- IEventsRule now has an IEventTarget instead of just a paco.ref to the target. This
  allows you to specify the input_json for the target.

### Added

- IManagedPolicy has a policy_name field which can be used to specify the name of IAM Policy in AWS.

- IDeploymentPipelineSourceGitHub to model GitHub.Source actions for CodePipeline.

- IDeploymentPipeline has a stages field which can be used to create more flexible Stages and Actions
  than the pre-baked source/build/deploy fields.

### Changed

- IS3Resource now has an IS3Buckets instead of a dict and references for global buckets
  has been cleaned up.

### Fixed

- All IVPC schemas with dicts have been replaced by INamed objects so that they can provide a paco_ref.

6.4.1 (2020-02-19)
------------------

### Added

- New IVersionControl schema for a IProject configuration.


6.4.0 (2020-02-17)
------------------

### Added

- IElasticsearchDomain schema.

- ASG has instance_ami_ignore_changes field to indicate the AMI Id is being updated
  externally.

- paco.ref function can now call any arbitrary Python function.

- Add enabled_state for IEventRule.

- Added log_group_names and expire_events_after_days to ILambda to allow it to
  manage Log Groups and set a Retention period.

### Changed

- Superflous ICodeCommitRepositoryGroups was removed and ICodeCommit is the container
  now for an ICodeCommitRepositoryGroup.

### Fixed

- Fix errors thrown by loader when loading environments with empty config.

6.3.7 (2020-02-05)
------------------

### Added

- Full set of fields for `generate_secret_string` for Secrets.

### Fixed

- Lambda.add_environment_variable was not passing the parent.


6.3.6 (2020-01-29)
------------------

### Added

- Error message when cfn-init files with !Sub and !Join can't be parsed.


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
