class UserRegistrationError(Exception):
    """Base exception for user registration failures"""

    pass


class InsecurePassword(UserRegistrationError):
    pass


class InvalidEmail(UserRegistrationError):
    pass


class DuplicateEmail(UserRegistrationError):
    pass


class UserAuthenticationError(Exception):
    """Base exception for user authentication failures"""

    pass


class InvalidPassword(UserAuthenticationError):
    pass


class UnknownEmail(UserAuthenticationError):
    pass

class BrokenUserRecord(UserAuthenticationError):
    pass