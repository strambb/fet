class UserRegistrationError(Exception):
    """Base exception for user registration failures"""

    pass


class InsecurePassword(UserRegistrationError):
    pass


class InvalidEmail(UserRegistrationError):
    pass


class DuplicateEmail(UserRegistrationError):
    pass
