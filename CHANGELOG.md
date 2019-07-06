Changelog for aim.models
=================

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
