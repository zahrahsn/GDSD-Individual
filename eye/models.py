from django.db import models


class BuyProducts(models.Model):
    product_id = models.IntegerField()
    buyer_id = models.IntegerField()
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'buy_products'


class Cart(models.Model):
    buyer = models.OneToOneField('SiteUser', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'cart'


class CartProduct(models.Model):
    product = models.ForeignKey('Product', models.DO_NOTHING)
    cart = models.ForeignKey(Cart, models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cart_product'


class Category(models.Model):
    name = models.CharField(unique=True, max_length=45)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'category'


class Product(models.Model):
    name = models.CharField(max_length=256)
    price = models.FloatField()
    added_date = models.DateTimeField()
    buyer = models.ForeignKey('SiteUser', models.DO_NOTHING, blank=True, null=True, related_name='product_buyer')
    sold_date = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey('Category', models.DO_NOTHING)
    is_validated = models.BooleanField(blank=True, null=True)
    external_link = models.CharField(max_length=255, blank=True, null=True)
    picture_link = models.CharField(max_length=255, blank=True, null=True)
    seller = models.ForeignKey('SiteUser', models.DO_NOTHING, related_name='product_seller')
    is_rejected = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'product'


class Review(models.Model):
    seller_id = models.BigIntegerField()
    byuer_id = models.BigIntegerField()
    text = models.CharField(max_length=4000)
    date = models.DateTimeField()
    rate = models.FloatField()

    class Meta:
        managed = True
        db_table = 'review'


class Role(models.Model):
    name = models.CharField(unique=True, max_length=45)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'role'


class SiteUser(models.Model):
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    photo_link = models.FileField(blank=True, null=True)
    is_verified = models.BooleanField(blank=True, null=True)
    is_validated = models.BooleanField(blank=True, null=True)
    is_seller_requested = models.BooleanField(blank=True, null=True)
    is_banned = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.name, self.lastname)

    class Meta:
        managed = True
        db_table = 'user'


class UserRole(models.Model):
    user = models.ForeignKey(SiteUser, models.DO_NOTHING)
    role = models.ForeignKey(Role, models.DO_NOTHING)

    def __str__(self):
        return f'{self.user.name} {self.user.lastname} => {self.role.name}'

    class Meta:
        managed = True
        db_table = 'user_role'
