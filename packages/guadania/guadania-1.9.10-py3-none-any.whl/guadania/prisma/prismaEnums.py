import enum

class TimeUnit(enum.Enum):
    """TimeUnit.MINUTE, TimeUnit.HOUR, TimeUnit.DAY, TimeUnit.WEEK, TimeUnit.MONTH y TimeUnit.YEAR"""
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


# No se van a usar de momento
# class AlertFields(enum.Enum):
#    """AlertFields.ALERT_ID, AlertFields.ALERT_STATUS, AlertFields.ALERT_TIME, AlertFields.CLOUD_ACCOUNT_ID, 
#    AlertFields.CLOUD_ACCOUNT, AlertFields.CLOUD_REGION, AlertFields.RESOURCE_ID, AlertFields.RESOURCE_NAME, 
#    AlertFields.POLICY_NAME, AlertFields.POLICY_TYPE y AlertFields.POLICY_SEVERITY"""
#    ALERT_ID = 'alert.id'
#    ALERT_STATUS = 'alert.status'
#    ALERT_TIME = 'alert.time'
#    CLOUD_ACCOUNT_ID = 'cloud.accountId'
#    CLOUD_ACCOUNT = 'cloud.account'
#    CLOUD_REGION = 'cloud.region'
#    RESOURCE_ID = 'resource.id'
#    RESOURCE_NAME = 'resource.name'
#    POLICY_NAME = 'policy.name'
#    POLICY_TYPE = 'policy.type'
#    POLICY_SEVERITY = 'policy.severity'


class PolicySeverity(enum.Enum):
    """PolicySeverity.INFORMATIONAL, PolicySeverity.LOW, PolicySeverity.MEDIUM, PolicySeverity.HIGH, PolicySeverity.CRITICAL"""
    INFORMATIONAL = 'informational'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class PolicyType(enum.Enum):
    """PolicyType.IAM, PolicyType.CONFIG, PolicyType.NETWORK y PolicyType.AUDIT_EVENT"""
    CONFIG = 'config'
    NETWORK = 'network'
    AUDIT_EVENT = 'audit_event'
    IAM = 'iam'


class AlertStatus(enum.Enum):
    """AlertStatus.OPEN, AlertStatus.DISMISSED, AlertStatus.SNOOZED y AlertStatus.RESOLVED"""
    OPEN = 'open'
    DISMISSED = 'dismissed'
    SNOOZED = 'snoozed'
    RESOLVED = 'resolved'

class ScanStatus(enum.Enum):
    """ScanStatus.ALL, ScanStatus.PASSED y ScanStatus.FAILED"""
    ALL = 'all'
    PASSED = 'passed'
    FAILED = 'failed'

class GroupBy(enum.Enum):
    """GroupBy.CLOUD_TYPE, GroupBy.CLOUD_ACCOUNT, GroupBy.CLOUD_REGION, GroupBy.CLOUD_SERVICE Y GroupBy.RESOURCE_TYPE"""

    CLOUD_TYPE = 'cloud.type'
    CLOUD_ACCOUNT = 'cloud.account'
    CLOUD_REGION = 'cloud.region'
    CLOUD_SERVICE = 'cloud.service'
    RESOURCE_TYPE = 'resource.type'

class CloudType(enum.Enum):
    """CloudType.AZURE, CloudType.AWS, CloudType.GCP, CloudType.OCI Y CloudType.ALIBABA"""

    AZURE = 'Azure'
    AWS = 'AWS'
    GCP = 'GCP'
    OCI = 'OCI'
    ALIBABA = 'Alibaba Cloud'