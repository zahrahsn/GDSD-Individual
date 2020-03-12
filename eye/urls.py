from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static
from eye.views import index
import eye.apis.user_apis as user
import eye.apis.product_apis as product
import eye.apis.purchase_apis as purchase

urlpatterns = [
                  url(r'^api/post/login$', user.user_login),
                  url(r'^api/get/allproducts/$', product.allproducts),
                  url(r'^api/post/addtocart$', purchase.addtocart),
                  url(r'^api/post/deleteitemincart$', purchase.deleteitemincart),
                  url(r'^api/post/buy_item$', purchase.buy_item),
                  url(r'^api/post/updateprofile$', user.updateprofile),
                  url(r'^api/post/updateprofilepic$', user.updateprofilepic),
                  url(r'^api/post/uploadpic$', product.uploadproductepic),
                  url(r'^api/post/editproduct$', product.editproduct),
                  url(r'^api/post/addproduct$', product.addproduct),
                  url(r'^api/get/productlist/$', product.productlist),
                  url(r'^api/get/productlistbyid/$', product.productdetail),
                  url(r'^api/get/profile$', user.userprofile),
                  url(r'^api/get/getTransactions$', user.transactions),
                  url(r'^api/get/userCartItems$', user.getusercart),
                  url(r'^api/get/categories$', product.getcategories),
                  url(r'^api/get/productofuser$', user.getproductofuser),
                  path('', index),
                  path('cart/', index),
                  path('login/', index),
                  path('about/', index),
                  path('privacyPolicy/', index),
                  path('user/', index),
                  path('detail/', index)
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)
