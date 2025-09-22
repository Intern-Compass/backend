from collections import namedtuple
from enum import StrEnum, Enum


class DepartmentEnum(Enum):
    CHIEF_EXECUTIVE_OFFICER_OFFICE = 1
    CHIEF_OPERATING_OFFICER_OFFICE_NG = 2
    COMPANY_SECRETARIAT = 3
    CORPORATE_SERVICES_AND_SUSTAINABILITY = 4
    CUSTOMER_RELATIONS_AND_EXPERIENCE = 5
    DIGITAL_SERVICES_NG = 6
    ENTERPRISE_BUSINESS = 7
    FINANCE = 8
    FIXED_BROADBAND = 9
    HUMAN_RESOURCES = 10
    INFORMATION_TECHNOLOGY = 11
    INTERNAL_AUDIT_AND_FORENSIC_SERVICES = 12
    MARKETING = 13
    NETWORK = 14
    RISK_AND_COMPLIANCE = 15
    SALES_AND_DISTRIBUTION = 16
    STRATEGY_AND_INNOVATION = 17


class UserType(StrEnum):
    SUPERVISOR = "supervisor"
    INTERN = "intern"
    ADMIN = "admin"

InternMatchDetail = namedtuple("InternMatchDetail", ["intern_id", "similarity"])

