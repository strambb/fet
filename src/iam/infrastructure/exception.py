class UserRepositoryException(Exception):
    pass

class UserNotFound(UserRepositoryException):
    pass

class UserTranslationError(UserRepositoryException):
    pass
