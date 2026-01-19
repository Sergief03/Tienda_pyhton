class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    finished = db.Column(db.Boolean, default=False)


    order_lines = db.relationship(
        "OrderLine",
        backref="order",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __init__(self, user_id):
        self.user_id = user_id

    def get_ID(self):
        return self.id

    def get_user_id(self):
        return self.user_id
    
    def get_created_at(self):
        return self.created_at

    def get_finished(self):
        return self.finished

    def set_finished(self, finished):
        self.finished = finished

    def get_order_lines(self):
        return self.order_lines
