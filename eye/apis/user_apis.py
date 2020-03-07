import datetime
import json
import traceback
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from eye.apis.helper import dictfetchall
from eye.check_image import ImageValidator
from eye.models import SiteUser


@api_view(['POST'])
def user_login(request):
    email = request.data["email"]
    password = request.data["password"]
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
            select u.id,u.password,count(*) as role from  user u join user_role r
            on u.id=r.user_id where lower(u.email)=lower('{email}') 
            group by u.id
            '''
        )
        items = dictfetchall(cursor)[0]
        if items["password"] == password:
            return Response({
                'code': 200,
                'success': "login successful",
                'userid': items["id"],
                'userrole': items["role"]
            })
        else:
            return Response({
                'code': 400,
                'failed': "error occurred"
            })


@api_view(['GET'])
def userprofile(request):
    user_id = request.GET['id']
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
           Select email, name, lastname, DATE_FORMAT(date_of_birth, "%d %M %Y") AS date_of_birth, 
           phone, description, photo_link, is_verified, is_validated,
           (select count(*) from user_role where user_id = {user_id} and role_id = 2) as isSeller, 
           (select count(*) from user_role where user_id = {user_id} and role_id = 3) as isAdmin,
           CAST(is_seller_requested AS SIGNED INTEGER) AS is_seller_requested
           from user where id={user_id}
        '''
        )
        try:
            items = dictfetchall(cursor)
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['GET'])
def transactions(request):
    user_id = request.GET['id']
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
           SELECT p.name as product_name, price, u.name as seller_name, 
           DATE_FORMAT(sold_date, "%d %M %Y") AS sold_date
           FROM product p join user u on u.id = p.seller_id 
           where buyer_id={user_id}
        '''
        )
        try:
            items = dictfetchall(cursor)
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['GET'])
def getproductofuser(request):
    user_id = request.GET['id']
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            select p.*,u.name as seller_name, c.name as category_name 
            from product p join user u on p.seller_id = u.id 
            join category c on c.id = p.category_id where seller_id={user_id}
            """
        )
        try:
            records = dictfetchall(cursor)
            for item in records:
                for key, value in item.items():
                    if isinstance(value, datetime.datetime):
                        item[key] = item[key].strftime("%m/%d/%Y")
            data = json.loads(json.dumps(records))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['POST'])
def updateprofilepic(request):
    id = request.data['id']
    try:
        file = request.FILES['files']
        validator = ImageValidator(file)
        resized = validator.resize()
        file_path = f'photos/{id}_profile.{file.name.split(".")[-1]}'
        absolute_path = default_storage.save(file_path, ContentFile(resized))
        user = SiteUser.objects.get(id=id)
        user.photo_link = request.build_absolute_uri("/images/" + absolute_path)
        user.save()
        return Response(
            {
                'code': 200,
                'success': "Image Uploaded Successfully."
            }
        )
    except KeyError:
        raise ParseError('Request has no resource file attached')


@api_view(['POST'])
def updateprofile(request):
    id = request.data['id']
    name = request.data['name'] if request.data['name'] != "undefined" else ""
    lastname = request.data['lastname'] if request.data['lastname'] != "undefined" else ""
    phone = request.data['phone'] if request.data['phone'] != "undefined" else ""
    description = request.data['description'] if request.data['description'] != "undefined" else ""
    email = request.data['email']
    password = request.data['password']
    photo_link = request.data['photo_link']
    date_of_birth = request.data['date_of_birth']
    if password == "undefined" or password == "null":
        query = f"""
        UPDATE user SET name='{name}', lastname='{lastname}', phone='{phone}',
        photo_link='{photo_link}', email='{email}',
        description='{description}', date_of_birth='{date_of_birth}' WHERE id={id}
        """
    else:
        query = f"""
        UPDATE user SET name='{name}', lastname='{lastname}', phone='{phone}',
        photo_link='{photo_link}', email='{email}',
        description='{description}', date_of_birth='{date_of_birth}', password='{password}' WHERE id={id}
        """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return Response(
                {
                    'code': 200,
                    'success': "Details modified successfully"
                }
            )
    except:
        traceback.print_exc()


@api_view(['POST'])
def getusercart(request):
    user_id = request.data["user_id"]
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT product.id,product.name,product.price,product.added_date,
            product.buyer_id,product.sold_date,product.description,product.category_id,
            product.is_validated,product.external_link,product.seller_id,product.picture_link
            FROM product JOIN cart_product ON product.id=cart_product.product_id 
            JOIN cart on cart.id=cart_product.cart_id WHERE cart.buyer_id={user_id}
            """
        )
        records = dictfetchall(cursor)
        for item in records:
            for key, value in item.items():
                if isinstance(value, datetime.datetime):
                    item[key] = item[key].strftime("%m/%d/%Y")
        data = json.loads(json.dumps(records))
        return Response(data, status=200)
