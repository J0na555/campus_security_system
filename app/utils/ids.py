import uuid

def generate_violation_id() -> str:
    """Generate a unique violation ID"""
    return f"vio_{uuid.uuid4().hex[:10]}"

def generate_pass_id() -> str:
    """Generate a unique visitor pass ID"""
    return f"vis_pass_{uuid.uuid4().hex[:8]}"
