Changelog for aim.models
=================

3.2.0 (unreleased)
------------------

### Added

- CloudWatch Log Group objects are loaded in `MonitorConfig/AlarmSets.yaml` in a `log_groups`
  section. These are for configuring CloudWatch Log Group expiration dates.

### Changed

 - LogSets, LogSet, LogCategory and LogSource are now all locatable INamed objects.

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
