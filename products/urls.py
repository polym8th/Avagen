from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.list_digital_products, name="products"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path(
        "delete/<int:product_id>/", views.delete_product, name="delete_product"
    ),
]

# Serve media files during development

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
