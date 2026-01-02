"""
SQLModel database models for Campus Security System
Based on API Contract v1.1.0
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


# ============================================================================
# ENUMS
# ============================================================================

class ViolationTypeEnum(str, Enum):
    """Violation types as per API contract section 6"""
    UNAUTHORIZED_QR_SCAN = "unauthorized_qr_scan"
    FACE_VERIFICATION_MISMATCH = "face_verification_mismatch"
    MULTIPLE_FAIL_ATTEMPT = "multiple_fail_attempt"
    EXPIRED_VISITOR_QR_CODE = "expired_visitor_qr_code"


class SubjectTypeEnum(str, Enum):
    """Subject types as per API contract section 6"""
    STUDENT = "student"
    STAFF = "staff"
    VISITOR = "visitor"


class UserRoleEnum(str, Enum):
    """User roles for security staff as per API contract section 6"""
    SECURITY_OFFICER = "security_officer"
    SECURITY_SUPERVISOR = "security_supervisor"
    ADMIN = "admin"


class EnrollmentStatusEnum(str, Enum):
    """Student enrollment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"


class EmploymentStatusEnum(str, Enum):
    """Staff employment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class GateStatusEnum(str, Enum):
    """Gate operational status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class VehicleTypeEnum(str, Enum):
    """Vehicle type classification"""
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    VAN = "van"
    BUS = "bus"
    OTHER = "other"


class VehicleEntryStatusEnum(str, Enum):
    """Vehicle entry status"""
    ENTERED = "entered"
    EXITED = "exited"
    FLAGGED = "flagged"


class VehicleAlertTypeEnum(str, Enum):
    """Vehicle alert types"""
    UNKNOWN_VEHICLE = "unknown_vehicle"
    VEHICLE_MISMATCH = "vehicle_mismatch"


class OwnerTypeEnum(str, Enum):
    """Vehicle owner type"""
    STUDENT = "student"
    STAFF = "staff"
    VISITOR = "visitor"


# ============================================================================
# LOOKUP TABLES
# ============================================================================

class Gate(SQLModel, table=True):
    """Gate/entry point lookup table"""
    __tablename__ = "gates"
    
    id: str = Field(primary_key=True, description="Gate identifier (e.g., 'gate_main_entrance')")
    name: str = Field(index=True, description="Human-readable gate name")
    location: str = Field(description="Physical location description")
    status: GateStatusEnum = Field(default=GateStatusEnum.ONLINE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    violations: list["Violation"] = Relationship(back_populates="gate")
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="gate")


class Department(SQLModel, table=True):
    """Department lookup table"""
    __tablename__ = "departments"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    students: list["Student"] = Relationship(back_populates="department")
    staff_members: list["StaffMember"] = Relationship(back_populates="department")


# ============================================================================
# SUBJECT TABLES (Student, Staff, Visitor)
# ============================================================================

class Student(SQLModel, table=True):
    """Student records"""
    __tablename__ = "students"
    
    id: str = Field(primary_key=True, description="Student ID (e.g., 'stu_789xyz')")
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    photo_url: Optional[str] = None
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    enrollment_status: EnrollmentStatusEnum = Field(default=EnrollmentStatusEnum.ACTIVE)
    qr_code: str = Field(unique=True, index=True, description="Student's QR code content")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    department: Optional[Department] = Relationship(back_populates="students")
    violations: list["Violation"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "Violation.student_id"}
    )
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="student")


class StaffMember(SQLModel, table=True):
    """Staff/Faculty member records"""
    __tablename__ = "staff_members"
    
    id: str = Field(primary_key=True, description="Staff ID (e.g., 'stf_456abc')")
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    photo_url: Optional[str] = None
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    position: Optional[str] = None
    employment_status: EmploymentStatusEnum = Field(default=EmploymentStatusEnum.ACTIVE)
    qr_code: str = Field(unique=True, index=True, description="Staff's QR code content")
    hired_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    department: Optional[Department] = Relationship(back_populates="staff_members")
    violations: list["Violation"] = Relationship(
        back_populates="staff_member",
        sa_relationship_kwargs={"foreign_keys": "Violation.staff_id"}
    )
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="staff_member")
    hosted_visitors: list["Visitor"] = Relationship(back_populates="host")


class Visitor(SQLModel, table=True):
    """Visitor pass records"""
    __tablename__ = "visitors"
    
    id: str = Field(primary_key=True, description="Visitor pass ID (e.g., 'vis_pass_456')")
    name: str = Field(index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    purpose: str
    host_staff_id: str = Field(foreign_key="staff_members.id")
    qr_code: str = Field(unique=True, index=True, description="Visitor pass QR code content")
    qr_code_image_url: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    allowed_gates: Optional[str] = Field(default=None, description="JSON array of allowed gate IDs")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_staff_id: str = Field(foreign_key="security_staff.id")
    
    # Relationships
    host: StaffMember = Relationship(back_populates="hosted_visitors")
    created_by: "SecurityStaff" = Relationship(back_populates="created_visitors")
    violations: list["Violation"] = Relationship(
        back_populates="visitor",
        sa_relationship_kwargs={"foreign_keys": "Violation.visitor_id"}
    )
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="visitor")


# ============================================================================
# SECURITY STAFF (Dashboard Users)
# ============================================================================

class SecurityStaff(SQLModel, table=True):
    """Security staff who can log into the dashboard"""
    __tablename__ = "security_staff"
    
    id: str = Field(primary_key=True, description="User ID (e.g., 'usr_abc123')")
    employee_id: str = Field(unique=True, index=True, description="Employee ID (e.g., 'EMP-2024-001')")
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str = Field(description="Hashed password")
    role: UserRoleEnum = Field(default=UserRoleEnum.SECURITY_OFFICER)
    department: str = Field(default="Campus Security")
    is_active: bool = Field(default=True)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    created_visitors: list[Visitor] = Relationship(back_populates="created_by")
    resolved_violations: list["Violation"] = Relationship(back_populates="resolved_by")


# ============================================================================
# VIOLATION TRACKING
# ============================================================================

class Violation(SQLModel, table=True):
    """Security violation records"""
    __tablename__ = "violations"
    
    id: str = Field(primary_key=True, description="Violation ID (e.g., 'vio_abc123')")
    type: ViolationTypeEnum = Field(index=True)
    
    # Subject information (nullable for unauthorized_qr_scan violations)
    subject_type: Optional[SubjectTypeEnum] = Field(default=None, index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id")
    staff_id: Optional[str] = Field(default=None, foreign_key="staff_members.id")
    visitor_id: Optional[str] = Field(default=None, foreign_key="visitors.id")
    
    # Gate and timing information
    gate_id: str = Field(foreign_key="gates.id", index=True)
    occurred_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Violation details (JSON field for flexibility)
    details: Optional[str] = Field(default=None, description="JSON object with violation-specific details")
    
    # For unauthorized_qr_scan: raw scanned QR data
    scanned_qr_code: Optional[str] = None
    qr_hash: Optional[str] = Field(default=None, description="SHA256 hash of raw QR data for unknowns")
    
    # For face verification violations: captured image info
    captured_image_url: Optional[str] = None
    captured_image_path: Optional[str] = Field(default=None, description="Local file path to captured image")
    confidence_score: Optional[float] = None
    
    # Resolution tracking
    resolved: bool = Field(default=False, index=True)
    resolved_at: Optional[datetime] = None
    resolved_by_staff_id: Optional[str] = Field(default=None, foreign_key="security_staff.id")
    resolution_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    gate: Gate = Relationship(back_populates="violations")
    student: Optional[Student] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.student_id"}
    )
    staff_member: Optional[StaffMember] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.staff_id"}
    )
    visitor: Optional[Visitor] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.visitor_id"}
    )
    resolved_by: Optional[SecurityStaff] = Relationship(back_populates="resolved_violations")
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="violation")


class FailAttempt(SQLModel, table=True):
    """Failed verification attempt tracking for multiple_fail_attempt violations"""
    __tablename__ = "fail_attempts"
    
    id: int = Field(default=None, primary_key=True)
    
    # Subject information
    subject_type: SubjectTypeEnum = Field(index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id")
    staff_id: Optional[str] = Field(default=None, foreign_key="staff_members.id")
    visitor_id: Optional[str] = Field(default=None, foreign_key="visitors.id")
    
    # Attempt details
    gate_id: str = Field(foreign_key="gates.id", index=True)
    attempted_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    captured_image_url: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Link to violation if this attempt triggered one
    violation_id: Optional[str] = Field(default=None, foreign_key="violations.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    gate: Gate = Relationship(back_populates="fail_attempts")
    student: Optional[Student] = Relationship(back_populates="fail_attempts")
    staff_member: Optional[StaffMember] = Relationship(back_populates="fail_attempts")
    visitor: Optional[Visitor] = Relationship(back_populates="fail_attempts")
    violation: Optional[Violation] = Relationship(back_populates="fail_attempts")


# ============================================================================
# ACCESS LOG (Optional - for successful scans)
# ============================================================================

class AccessLog(SQLModel, table=True):
    """Log of successful access grants (optional, for analytics)"""
    __tablename__ = "access_logs"
    
    id: int = Field(default=None, primary_key=True)
    
    # Subject information
    subject_type: SubjectTypeEnum = Field(index=True)
    subject_id: str = Field(index=True, description="ID of student/staff/visitor")
    
    # Access details
    gate_id: str = Field(index=True)
    accessed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    qr_code_used: str
    face_verified: bool = Field(default=False)
    face_confidence: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# VEHICLE TRACKING TABLES
# ============================================================================

class Vehicle(SQLModel, table=True):
    """Registered vehicle records"""
    __tablename__ = "vehicles"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(unique=True, index=True, description="Vehicle license plate number")
    owner_type: OwnerTypeEnum = Field(index=True)
    owner_id: Optional[str] = Field(default=None, description="ID of student/staff/visitor owner")
    owner_name: str = Field(description="Name of vehicle owner")
    vehicle_type: VehicleTypeEnum = Field(default=VehicleTypeEnum.CAR)
    color: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    vehicle_entries: list["VehicleEntry"] = Relationship(back_populates="vehicle")


class VehicleEntry(SQLModel, table=True):
    """Vehicle entry/exit log - ALL entries are logged"""
    __tablename__ = "vehicle_entries"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(index=True, description="License plate scanned")
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicles.id", description="FK to Vehicle if registered")
    entry_time: datetime = Field(default_factory=datetime.utcnow, index=True)
    exit_time: Optional[datetime] = Field(default=None, index=True)
    entry_image_path: Optional[str] = Field(default=None, description="Path to entry camera image")
    exit_image_path: Optional[str] = Field(default=None, description="Path to exit camera image")
    status: VehicleEntryStatusEnum = Field(default=VehicleEntryStatusEnum.ENTERED, index=True)
    gate_id: Optional[str] = Field(default=None, description="Gate where entry occurred")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    vehicle: Optional[Vehicle] = Relationship(back_populates="vehicle_entries")


class VehicleAlert(SQLModel, table=True):
    """Vehicle security alerts for unknown or mismatched vehicles"""
    __tablename__ = "vehicle_alerts"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(index=True, description="License plate that triggered alert")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    alert_type: VehicleAlertTypeEnum = Field(index=True)
    captured_image_path: Optional[str] = Field(default=None, description="Path to captured image")
    details: Optional[str] = Field(default=None, description="JSON object with alert details")
    resolved: bool = Field(default=False, index=True)
    resolved_at: Optional[datetime] = None
    resolved_by_staff_id: Optional[str] = Field(default=None, foreign_key="security_staff.id")
    resolution_notes: Optional[str] = None
    gate_id: Optional[str] = Field(default=None, description="Gate where alert occurred")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    resolved_by: Optional["SecurityStaff"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "VehicleAlert.resolved_by_staff_id"}
    )
