from enum import IntEnum
from enum import auto

class Actions(IntEnum):
    login_success = auto()
    login_failed = auto()
    logout = auto()
    account_locked = auto()
    password_changed = auto()
    password_reset = auto()
    email_changed = auto()
    new_profile = auto()
    profile_deactivation = auto()
    profile_activation = auto()
    account_deactivation = auto()
    account_activation = auto()
    profile_deletion = auto()
    account_deletion = auto()