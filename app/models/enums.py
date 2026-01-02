from enum import Enum

class ViolationTypeEnum(str, Enum):
    UNAUTHORIZED_QR_SCAN = "unauthorized_qr_scan"
    FACE_VERIFICATION_MISMATCH = "face_verification_mismatch"
    MULTIPLE_FAIL_ATTEMPT = "multiple_fail_attempt"
    EXPIRED_VISITOR_QR_CODE = "expired_visitor_qr_code"

class SubjectTypeEnum(str, Enum):
    STUDENT = "student"
    STAFF = "staff"
    VISITOR = "visitor"

class UserRoleEnum(str, Enum):
    SECURITY_OFFICER = "security_officer"
    SECURITY_SUPERVISOR = "security_supervisor"
    ADMIN = "admin"

class EnrollmentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"

class EmploymentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

class GateStatusEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class VehicleTypeEnum(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    VAN = "van"
    BUS = "bus"
    OTHER = "other"

class VehicleEntryStatusEnum(str, Enum):
    ENTERED = "entered"
    EXITED = "exited"
    FLAGGED = "flagged"

class VehicleAlertTypeEnum(str, Enum):
    UNKNOWN_VEHICLE = "unknown_vehicle"
    VEHICLE_MISMATCH = "vehicle_mismatch"

class OwnerTypeEnum(str, Enum):
    STUDENT = "student"
    STAFF = "staff"
    VISITOR = "visitor"
