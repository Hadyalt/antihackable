class Users:
    ROLES = ("system_admin", "super_admin", "service_engineer")

    def __init__(self, username: str, password: str, role: str, is_active: bool = True):
        if role not in self.ROLES:
            raise ValueError(f"Invalid role: {role}")
        self.username = username
        self.password = password
        self.role = role
        self.is_active = is_active

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role}, is_active={self.is_active})>"
