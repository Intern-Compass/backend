from enum import StrEnum


class Department(StrEnum):
    CHIEF_EXECUTIVE_OFFICER_OFFICE = "chief_executive_officer_office"
    CHIEF_OPERATING_OFFICER_OFFICE_NG = "chief_operating_officer_office_ng"
    COMPANY_SECRETARIAT = "company_secretariat"
    CORPORATE_SERVICES_AND_SUSTAINABILITY = "corporate_services_and_sustainability"
    CUSTOMER_RELATIONS_AND_EXPERIENCE = "customer_relations_and_experience"
    DIGITAL_SERVICES_NG = "digital_services_ng"
    ENTERPRISE_BUSINESS = "enterprise_business"
    FINANCE = "finance"
    FIXED_BROADBAND = "fixed_broadband"
    HUMAN_RESOURCES = "human_resources"
    INFORMATION_TECHNOLOGY = "information_technology"
    INTERNAL_AUDIT_AND_FORENSIC_SERVICES = "internal_audit_and_forensic_services"
    MARKETING = "marketing"
    NETWORK = "network"
    RISK_AND_COMPLIANCE = "risk_and_compliance"
    SALES_AND_DISTRIBUTION = "sales_and_distribution"
    STRATEGY_AND_INNOVATION = "strategy_and_innovation"


class UserType(StrEnum):
    SUPERVISOR = "supervisor"
    INTERN = "intern"
    ADMIN = "admin"
