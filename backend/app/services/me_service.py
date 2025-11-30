from app.utils.jwt_utils import get_user_id
from app.models.member import Member

def get_profile_service(token):
    user_id = get_user_id(token)
    if not user_id:
        return False, "Invalid token"
    
    member = Member.query.get(user_id)
    if not member:
        return False, "User not found"
        
    return True, {
        "id": member.m_id,
        "name": member.u_name,
        "email": member.u_mail
    }

def get_my_items(token):
    return True, []

def get_my_reservations(token):
    return True, []

def get_reservation_detail(token, r_id):
    return True, {}
