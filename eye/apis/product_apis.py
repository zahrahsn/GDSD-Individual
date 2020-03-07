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
import Individual.settings as settings


@api_view(['GET'])
def getcategories(request):
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
            SELECT * FROM category
            '''
        )
        try:
            items = dictfetchall(cursor)
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['POST'])
def uploadproductepic(request):
    try:
        file = request.FILES['files']
        file_path = f'photos/product_{file.name}'
        validator = ImageValidator(file)
        resized = validator.resize(max_height=500)
        default_storage.save(file_path, ContentFile(resized))
        photo_link = request.build_absolute_uri("/images/" + file_path)
        res = validator.check(f"{settings.MEDIA_ROOT}/{file_path}")
        if res is not None:
            default_storage.delete(file_path)
            return Response(
                {
                    'code': 501,
                    'error': res
                }
            )
        return Response(
            {
                'code': 200,
                'image': photo_link
            }
        )
    except KeyError:
        raise ParseError('Request has no resource file attached')


@api_view(['POST'])
def addproduct(request):
    description = request.data['description']
    name = request.data['name']
    picture_link = request.data['picture_link']
    price = request.data['price']
    seller_id = request.data['seller_id']
    category_id = request.data['category_id']
    query = f"""
            INSERT INTO product (added_date,description,name, picture_link,price,seller_id, category_id, is_validated) 
            VALUES (CURRENT_TIMESTAMP, '{description}','{name}','{picture_link}',{price},{seller_id},{category_id},1)
            """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return Response(
                {
                    'code': 200,
                    'success': "Product Added."
                }
            )
    except:
        traceback.print_exc()


@api_view(['POST'])
def editproduct(request):
    id = request.data['id']
    description = request.data['description']
    name = request.data['name']
    picture_link = request.data['picture_link']
    price = request.data['price']
    catid = request.data['catid']
    query = f"""
            UPDATE product SET description='{description}',name='{name}', picture_link='{picture_link}',price={price},
            category_id={catid} WHERE id={id}
            """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return Response(
                {
                    'code': 200,
                    'success': "Product Information Updated."
                }
            )
    except:
        traceback.print_exc()


@api_view(['GET'])
def allproducts(request):
    type = request.GET["type"]
    term = request.GET["term"]
    if type == '':
        type = "Name"
    with connection.cursor() as cursor:
        if type == "Name":
            cursor.execute(
                f'''
                SELECT p.*,u.name as seller_name, c.name as category_name
                from product p join user u on p.seller_id = u.id
                join category c on c.id = p.category_id
                WHERE p.buyer_id is null and p.is_validated= 1
                and LOWER(p.name) LIKE LOWER('%{term}%')
            '''
            )

        elif type == "Category":
            cursor.execute(
                f'''
                SELECT p.*,u.name as seller_name, c.name as category_name
                from product p join user u on p.seller_id = u.id
                join category c on c.id = p.category_id
                WHERE LOWER(c.name) LIKE LOWER('%{term}%') and p.buyer_id is null and
                p.is_validated = 1
            '''
            )
        else:
            cursor.execute(
                f'''
                SELECT p.*,u.name as seller_name, c.name as category_name 
                from product p join user u on p.seller_id = u.id 
                join category c on c.id = p.category_id
                WHERE LOWER(u.name) LIKE LOWER('%{term}%') and p.buyer_id is null and 
                p.is_validated=1
            '''
            )
        try:
            items = dictfetchall(cursor)
            for item in items:
                item["added_date"] = item["added_date"].strftime("%m/%d/%Y")
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['GET'])
def productlist(request):
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
            SELECT p.*,u.name as seller_name, c.name as category_name
            from product p join user u on p.seller_id = u.id
            join category c on c.id = p.category_id
            WHERE p.buyer_id is null
        '''
        )
        try:
            items = dictfetchall(cursor)
            for item in items:
                item["added_date"] = item["added_date"].strftime("%m/%d/%Y")
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()


@api_view(['GET'])
def productdetail(request):
    product_id = request.GET['product_id']
    with connection.cursor() as cursor:
        cursor.execute(
            f'''
            SELECT p.*,u.name as seller_name, c.name as category_name
            from product p join user u on p.seller_id = u.id
            join category c on c.id = p.category_id
            WHERE p.id={product_id}
        '''
        )
        try:
            items = dictfetchall(cursor)
            for item in items:
                item["added_date"] = item["added_date"].strftime("%m/%d/%Y")
            data = json.loads(json.dumps(items))
            return Response(data, status=200)
        except:
            traceback.print_exc()
