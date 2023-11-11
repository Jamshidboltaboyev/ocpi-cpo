import sys

from rest_framework.exceptions import ValidationError

from utils.redis import RedisClient


class AuthService:
    """
    types options:
    1. `forget_pass_verification`
    2. `registration_sms_verification`
    3. `login_sms_verification`
    4. `update_phone_verification`
    5. `change_password`
    6. `delete_profile`
    """

    redis_client = RedisClient()

    @classmethod
    def check_login_attempts(cls, phone, type):
        # 1 second for testing, ttl in  production should be changed to one day
        ttl = 1 if "test" in sys.argv else 900
        key = f"login_attempts:{phone}:{type}"
        attempts = cls.redis_client.get(key)
        if attempts is not None and int(attempts) >= 3:
            # Block user
            cls.redis_client.set(f"blocked_user:{phone}:{type}", "blocked", ttl=ttl)  # Block for 15 minutes
            cls.redis_client.delete(key)  # Reset login attempts
            raise ValidationError("User is blocked", code="blocked_user")  # use only in serializer
        else:
            if attempts is None:
                cls.redis_client.set(key, 1, ttl)
            else:
                attempts = int(attempts)
                if attempts < 3:
                    attempts += 1
                    cls.redis_client.set(key, attempts)

    @classmethod
    def is_user_blocked(cls, phone, type):
        return cls.redis_client.get(f"blocked_user:{phone}:{type}") is not None

    @classmethod
    def unblock_user(cls, phone, type):
        cls.redis_client.delete(f"login_attempts:{phone}:{type}")
        cls.redis_client.delete(f"blocked_user:{phone}:{type}")

    @classmethod
    def block_user(cls, phone, type, ttl: int = 24 * 60 * 60):
        cls.redis_client.set(f"blocked_user:{phone}:{type}", "blocked", ttl=ttl)

    @classmethod
    def reset_login_attempts(cls, phone, type):
        cls.redis_client.delete(f"blocked_user:{phone}:{type}")
        cls.redis_client.delete(f"login_attempts:{phone}:{type}")
