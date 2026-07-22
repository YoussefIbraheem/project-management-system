from accounts.models import User, UserVerification
import random
from utils.generate_unique_number import generate_verification_code

def generate_user_otp_code(user:User):
    otp = generate_verification_code()
    latest_user_verification = UserVerification.objects.filter(user=user).last()
    if latest_user_verification:
        latest_user_verification.delete()
    UserVerification.objects.create(user=user,code=otp)
    user.save()
    return otp
    