from sqlmodel import Session
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.visitor import Visitor

def get_subject_name(session: Session, subject_id: str, subject_type: str):
    if subject_type == "student":
        sub = session.get(Student, subject_id)
        return sub.name if sub else None
    if subject_type == "staff":
        sub = session.get(StaffMember, subject_id)
        return sub.name if sub else None
    if subject_type == "visitor":
        sub = session.get(Visitor, subject_id)
        return sub.name if sub else None
    return None

def link_subject(obj, subject_id: str, subject_type: str):
    if subject_type == "student": obj.student_id = subject_id
    elif subject_type == "staff": obj.staff_id = subject_id
    elif subject_type == "visitor": obj.visitor_id = subject_id
