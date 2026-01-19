from db import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.JSON, nullable=False, default=list)

    def __init__(self, username, password, roles=None):
        self.username = username
        self.password = password
        self.roles = roles or []

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "roles": self.roles
        }
