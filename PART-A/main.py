import re
from datetime import date

# ==========================================
# Dummy Database Schema
# ==========================================

admin_detail = [
    {"user_name": "admin_root", "name": "Principal Root", "password": "AdminPassword123@"}
]

educator = [
    {"edu_id": 1, "user_name": "mr_smith", "name": "John Smith", "password": "Password123@"}
]

applicant = [
    {"id": 1, "aid": "A001", "name": "James Potter", "email": "james@example.com", "dob": "2005-01-01", "status": "new"},
    {"id": 2, "aid": "A002", "name": "Lily Evans", "email": "lily@example.com", "dob": "2005-01-30", "status": "accepted"},
    {"id": 3, "aid": "A003", "name": "Severus Snape", "email": "severus@example.com", "dob": "2005-01-09", "status": "rejected"}
]

marks = [
    {"applicant_id": 1, "math": 90, "science": 85}
]

attendance_log = [
    # {id, educator_id, start_date, ongoing}
]

marked_attendance = [
    # {attendance_id, student_id}
]

# Helper increment IDs
next_edu_id = 2
next_applicant_id = 4
next_attendance_id = 1


# ==========================================
# Admin Management
# ==========================================

def validate_admin(user_name, password):
    admin = next((a for a in admin_detail if a["user_name"] == user_name), None)
    if not admin: return 1
    if admin["password"] != password: return 2
    return 0

def get_admin_name(user_name):
    admin = next((a for a in admin_detail if a["user_name"] == user_name), None)
    if admin: return admin["name"]
    return 1


# ==========================================
# Educator Management
# ==========================================

def validate_educator_details(user_name, name, password):
    if not (4 <= len(user_name) <= 20) or not re.match(r'^\w+$', user_name): return 1
    if len(name) > 100 or not re.match(r'^[A-Z][a-zA-Z]*(?: [A-Z][a-zA-Z]*){0,2}$', name): return 2
    if not (8 <= len(password) <= 20): return 3
    if not re.search(r'[A-Z]', password): return 3
    if not re.search(r'[a-z]', password): return 3
    if not re.search(r'[0-9]', password): return 3
    if not re.search(r'[@#$%&]', password): return 3
    return 0

def add_educator_details(user_name, name, password):
    global next_edu_id
    val = validate_educator_details(user_name, name, password)
    if val != 0: return val
    if any(e["user_name"] == user_name for e in educator): return 4
    educator.append({"edu_id": next_edu_id, "user_name": user_name, "name": name, "password": password})
    next_edu_id += 1
    return 0

def update_educator_details(edu_id, user_name, name, password):
    val = validate_educator_details(user_name, name, password)
    if val != 0: return val
    if any(e["user_name"] == user_name and e["edu_id"] != edu_id for e in educator): return 4
    edu = next((e for e in educator if e["edu_id"] == edu_id), None)
    if not edu: return 5
    edu["user_name"] = user_name
    edu["name"] = name
    edu["password"] = password
    return 0


# ==========================================
# Admission Management
# ==========================================

def get_students_on_status(status):
    status_lower = status.lower()
    if status_lower not in ["new", "accepted", "rejected"]: return []
    result = []
    for app in applicant:
        if app["status"] == status_lower:
            result.append({
                "id": app["id"], "name": app["name"], "email": app["email"], "dob": app["dob"]
            })
    return result

def update_application(application_id, action):
    app = next((a for a in applicant if a["id"] == application_id), None)
    if not app: return 1
    if app["status"] != "new": return 1
    action_lower = action.lower()
    if action_lower not in ["accept", "reject"]: return 2
    app["status"] = "accepted" if action_lower == "accept" else "rejected"
    return 0

# --- NEW: withdraw_application ---
def withdraw_application(email):
    app = next((a for a in applicant if a["email"] == email), None)
    if not app:
        return 1
    app_id = app["id"]
    # delete from marks table
    global marks, applicant
    marks = [m for m in marks if m["applicant_id"] != app_id]
    # delete from applicant table
    applicant = [a for a in applicant if a["id"] != app_id]
    return 0


# ==========================================
# Attendance Management
# ==========================================

def user_login(role, user_name, password):
    if role == "educator":
        if not password: return 1
        edu = next((e for e in educator if e["user_name"] == user_name), None)
        if not edu: return 2
        if edu["password"] != password: return 3
        # In order to supply the educator ID later, we will return the entire object or a tuple, 
        # But instructions say "return the name of the educator".
        # We will strictly return the name, but our mock routes.py might find them by name.
        return edu["name"]
        
    elif role == "student":
        app = next((a for a in applicant if a["email"] == user_name), None)
        if not app: return 4
        if app["status"] != "accepted": return 5
        return app["name"]
    else:
        return 6


# --- NEW: Attendance specific logic ---

def check_attendance():
    """Returns True if any attendance collection is currently ongoing, else False."""
    for log in attendance_log:
        if log["ongoing"] is True:
            return True
    return False

def start_attendance(educator_id):
    """
    1. if check_attendance() is True -> return 1
    2. if educator had started another collection on the same day -> return 2
    3. start attendance collection, set ongoing=true -> return 0
    """
    global next_attendance_id
    if check_attendance() is True:
        return 1
    
    current_date = date.today().strftime("%Y-%m-%d")
    for log in attendance_log:
        if log["educator_id"] == educator_id and log["start_date"] == current_date:
            return 2
            
    attendance_log.append({
        "id": next_attendance_id,
        "educator_id": educator_id,
        "start_date": current_date,
        "ongoing": True
    })
    next_attendance_id += 1
    return 0

def stop_attendance():
    if check_attendance() is False:
        return 1
    
    for log in attendance_log:
        if log["ongoing"] is True:
            log["ongoing"] = False
    return 0

def mark_attendance(student_id):
    """
    - using check_attendance(), if no ongoing -> return 1
    - check if student is already marked -> return 2
    - insert in marked_attendance -> return 0
    """
    if not check_attendance():
        return 1
        
    active_log = next((log for log in attendance_log if log["ongoing"] is True), None)
    if not active_log:
        return 1
        
    a_id = active_log["id"]
    for m in marked_attendance:
        if m["attendance_id"] == a_id and m["student_id"] == student_id:
            return 2
            
    marked_attendance.append({
        "attendance_id": a_id,
        "student_id": student_id
    })
    return 0

def get_attendance_list():
    """
    Fetch stopped attendances.
    Return list of dicts: {'attendance_id', 'educator_name', 'start_date'}
    """
    res = []
    for log in attendance_log:
        if log["ongoing"] is False:
            edu = next((e for e in educator if e["edu_id"] == log["educator_id"]), None)
            res.append({
                "attendance_id": log["id"],
                "educator_name": edu["name"] if edu else "Unknown",
                "start_date": log["start_date"]
            })
    return res

def get_students_attendance(attendance_id):
    """
    Check if stopped, if ongoing return 1.
    For each ACCEPTED student, fetch aid, name, present.
    Return list of dicts: {'aid', 'name', 'present'}
    """
    log = next((l for l in attendance_log if l["id"] == attendance_id), None)
    if not log or log["ongoing"] is True:
        return 1
        
    res = []
    for app in applicant:
        if app["status"] == "accepted":
            present = any(m["attendance_id"] == attendance_id and m["student_id"] == app["id"] 
                          for m in marked_attendance)
            res.append({
                "aid": app.get("aid", f"A00{app['id']}"),
                "name": app["name"],
                "present": 1 if present else 0
            })
    return res


# Helper to submit an application 
def apply_application(data):
    global next_applicant_id
    app_id = next_applicant_id
    
    applicant.append({
        "id": app_id,
        "aid": f"A00{app_id}",
        "name": data["name"],
        "email": data["email"],
        "dob": data.get("dob"), # string format generally passed back from forms
        "guardian_name": data.get("guardian_name"),
        "contact": data.get("guardian_contact"),
        "status": "new"
    })
    
    marks.append({
        "applicant_id": app_id,
        "language1": data.get("language1"),
        "language2": data.get("language2"),
        "math": data.get("math"),
        "science": data.get("science"),
        "history": data.get("history"),
        "geography": data.get("geography")
    })
    
    next_applicant_id += 1
    return True