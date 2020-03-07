import json
import traceback
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from eye.apis.helper import dictfetchall
from django.db.models.functions import datetime


@api_view(['POST'])
def addtocart(request):
    buyer_id = request.data["id"]
    product_id = request.data["product_id"]
    if buyer_id:
        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                select * from cart join cart_product on cart_product.cart_id = cart.id
                where buyer_id={buyer_id} and product_id={product_id}
                '''
            )
            items = dictfetchall(cursor)
            if len(items) > 0:
                return Response(status=404, data="this item is already added to cart!")

            cursor.execute(
                f'''
                select * from cart where buyer_id={buyer_id}
                '''
            )
            items = dictfetchall(cursor)
            if len(items) == 0:
                cursor.execute(
                    f'''
                    insert into cart (buyer_id) values ({buyer_id})
                    '''
                )
                cursor.execute(
                    f'''
                    select id from cart order by id desc limit 1
                    '''
                )
                cart_id = cursor.fetchone()[0]
            else:
                cart_id = items[0]["id"]

            cursor.execute(
                f'''
                insert into cart_product (quantity,cart_id,product_id) 
                values (1,{cart_id},{product_id})
                '''
            )
            return Response(
                {
                    'code': 200,
                    'success': "product added to cart"
                }
            )
    else:
        return Response(status=404, data="user has not logged in!")

@api_view(['POST'])
def deleteitemincart(request):
    buyer_id = request.data["user_id"]
    product_id = request.data["product_id"]
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
                delete from cart_product where cart_id=(
                select id from cart where buyer_id={buyer_id})
                and product_id={product_id}
                '''
        )

        if cursor.rowcount > 0:
            return Response(
                {
                    'code': 200,
                    'success': "product deleted from cart"
                }
            )
        else:
            return Response(
                {
                    'code': 401,
                    'error': "There is no such product in your cart"
                }
            )



@api_view(['POST'])
def buy_item(request):
    buyer_id = request.data['userID']
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
            select cp.id as cp_id,pp.sold_date,ct.buyer_id,cp.product_id from cart_product cp 
            join cart ct on cp.cart_id=ct.id join product pp on pp.id=cp.product_id
            where ct.buyer_id={buyer_id}
            '''
        )
        items = dictfetchall(cursor)
        for item in items:
            if item['sold_date'] is not None:
                return Response(
                    {
                        'code': 404,
                        'error': f"product {item['name']} has been sold!"
                    }
                )
        for item in items:
            product_id = item['product_id']
            cursor.execute(
                f'''
                update product set buyer_id={buyer_id},sold_date={datetime.Now()} where id={product_id}
                '''
            )
        for item in items:
            cursor.execute(
                f'''
                delete from cart_product where id={item['cp_id']}
                '''
            )

        cursor.execute(
            f'''
            delete from cart where buyer_id={buyer_id}
            '''
        )

        return Response(
            {
                'code': 200,
                'success': "purchase is done"
            }
        )