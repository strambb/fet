class IAMDomainException(Exception):
    """Base exception for user registration failures"""

    pass


class InsecurePassword(IAMDomainException):
    pass
