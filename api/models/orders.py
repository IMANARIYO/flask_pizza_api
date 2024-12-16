from ..utils import db
from datetime import datetime,timezone
from enum import Enum
class Sizes(str,Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'
class  Orderstatus(str,Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'

class Order(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True)
    size=db.Column(db.Enum(Sizes), default=Sizes.SMALL)
    order_status=db.Column(db.Enum(Orderstatus), default=Orderstatus.PENDING)
    flavour=db.Column(db.String(50),nullable=False)
    date_ordered=db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    quantity=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    user=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    def __repr__(self):
        return f'<Order {self.id}>'
    def save(self):
       db.session.add(self)
       db.session.commit()
    @classmethod
    def get_all(cls):
        return cls.query.all()
    @classmethod
    def get_by_id(cls,id):
        return cls.query.get_or_404(id)
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def update(self):
        db.session.commit()
        
