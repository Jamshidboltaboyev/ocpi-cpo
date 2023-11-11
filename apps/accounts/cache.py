from enum import Enum


class OTPTypes(Enum):
    LOGIN_SMS_VERIFICATION = "login_sms_verification"
    PANEL_ADMIN_LOGIN = "panel_admin_login"
    REGISTRATION_SMS_VERIFICATION = "registration_sms_verification"
    FORGET_PASS_VERIFICATION = "forget_pass_verification"
    UPDATE_PHONE_VERIFICATION = "update_phone_verification"
    CHANGE_PASSWORD = "change_password"
    DELETE_PROFILE = "delete_profile"
    SOCIAL_LOGIN = "social_login"
    DELETE_ACCOUNT = "delete_account"


def generate_cache_key(cache_type: str, *args):
    return f"{cache_type}{''.join(args)}"


types = [_.value for _ in OTPTypes]
