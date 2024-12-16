from flask_restx import Resource,Namespace,fields
from ..models.orders import Order
from ..models.orders import Sizes
from ..models.orders import Sizes

from ..models.users import User
from flask import jsonify
from http import HTTPStatus
from enum import Enum
from flask_jwt_extended import jwt_required,get_jwt_identity
from ..utils import db 
from ..utils.decorators import staff_required


class Sizes(str, Enum):
    SMALL = 'SMALL'
    MEDIUM = 'MEDIUM'
    LARGE = 'LARGE'
    EXTRA_LARGE = 'EXTRA_LARGE'

class OrderStatus(str, Enum):
    PENDING = 'PENDING'
    IN_TRANSIT = 'IN_TRANSIT'
    DELIVERED = 'DELIVERED'
order_namespace = Namespace('orders',description='Namespace for Operations related to orders')
order_status_model=order_namespace.model(
    'OrderStus',{
         'order_status': fields.String(
            description='The status of the order',
            default='pending',
            required=True,
            enum=['pending', 'completed', 'cancelled', 'in_transit', 'delivered']
        ),
    }
)
order_model=order_namespace.model(
'Order',{
    'id':fields.Integer(description='The order id'),
    'size':fields.String(description='The size of the pizza',required=True, enum=[size.value for size in Sizes]),
    'order_status': fields.String(
            description='The status of the order',
            default='pending',
            required=True,
            enum=['pending', 'completed', 'cancelled', 'in_transit', 'delivered']
        ),
    'flavour':fields.String(description='The flavour of the pizza',required=True),
    

}
)
order_response = order_namespace.model('OrderResponse', {
    'message': fields.String(description='Response message'),
    'data': fields.Nested(order_namespace.model('Order', {
        'id': fields.Integer(description='The order id'),
        'size': fields.String(description='Size of the pizza', required=True, 
                             enum=[size.value for size in Sizes]),
        'flavour': fields.String(description='Flavour of the pizza', required=True),
        'quantity': fields.Integer(description='Quantity ordered'),
        'price': fields.Float(description='Price of the order'),
        'order_status': fields.String(
            description='The status of the order',
            default='pending',
            required=True,
            enum=['pending', 'completed', 'cancelled', 'in_transit', 'delivered']
        ),
    }))
})
@order_namespace.route('/orders')
class OrderResource(Resource):
    @order_namespace.marshal_with(order_model)
    # @jwt_required()
    def get(self):
        """
        get all orders
        """
        orders=Order.query.all()
        return orders,HTTPStatus.OK
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @jwt_required()

    def post(self):
        """
        place orders
        """ 
        username=get_jwt_identity()
        current_user=User.query.filter_by(username=username).first()
        data=order_namespace.payload
        # order=Order(**data)
        new_order=Order(
           size=data['size'],
           quantity=data['quantity'],
           flavour=data['flavour'], 
           price=data['price'],

        )
        new_order.customer=current_user
        if not current_user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        new_order.save()
        # return data,HTTPStatus.CREATED
        return new_order,HTTPStatus.CREATED
@order_namespace.route('/order/<int:id>')
class GetUpdateDelete(Resource):
    @order_namespace.marshal_with(order_response)
    def get(self,id):
        """retrieve an order by id"""
        order=Order.get_by_id(id)
        if not order:
            return {"message": "Order not found"}, HTTPStatus.NOT_FOUND
        return{
                'message': 'succesful retrieved the  following order details',
                'data': order
            },HTTPStatus.OK
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    def put(self,id): 
        "update an order by with id" 
        order_to_update=Order.get_by_id(id)
        data=order_namespace.payload
        order_to_update.quantity=data['quantity']
        order_to_update.size=data['size']
        order_to_update.flavour=data['flavour']
        db.session.commit()
        return order_to_update,HTTPStatus.OK
    @order_namespace.marshal_with(order_model )
    def delete(self,id):
        "delete an order by order_id"
        order_to_delete=Order.get_by_id(id)
        order_to_delete.delete()

@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')  
class GetSpecificOrderByUser(Resource):
    @order_namespace.marshal_with(order_response)
    @jwt_required()
    def get(self,user_id,order_id):
        """retrieve an order by user"""
        user=User.get_by_id(user_id)
        order = Order.query.filter_by(id=order_id, user=user_id).first()
        if not order:
            return {
                'message': 'Order not found',
                'data': None
            }, HTTPStatus.NOT_FOUND
        return {
            'message': 'Order retrieved successfully',
            'data': order
        }, HTTPStatus.OK
       
@order_namespace.route('/user/<int:user_id>/orders')
class GetOrdersByUser(Resource):
    @order_namespace.marshal_list_with(order_model)
    def get(self,user_id):
        """retrieve all  orders by user"""
        user=User.get_by_id(user_id)
        orders=user.orders
        return orders,HTTPStatus.OK

@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):
    @order_namespace.expect(order_status_model)
    @order_namespace.marshal_with(order_model )
    def patch(self,order_id):
        """update order status"""
        data=order_namespace.payload 
        print(f"Received payload: {data}")

        order_to_update=Order.get_by_id(order_id)
        if not order_to_update:
           return {"message": "Order not found"}, HTTPStatus.NOT_FOUND
        order_to_update.order_status=data['order_status']
        db.session.commit()

        return order_to_update,HTTPStatus.OK 
@order_namespace.route('/orders/delete_all')
class DeleteAllOrders(Resource):
    @order_namespace.marshal_with(order_model)
    @jwt_required() 
    # ensuring the use  is loggred i n first
    @staff_required
    def delete(self):
        """delete all orders"""
        # idont need to load the data in me mery as long as i have the QLAlchemy ORM event listeners like before_delete or after_delete defined,
        
        Order.query.delete()
        db.session.commit()
        return {"message": "All orders deleted successfully2"}, HTTPStatus.OK
    
    
        
