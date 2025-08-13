# In main/urls.py (or your app's urls.py)
from django.urls import path
from . import views
from django.conf import settings # new
from  django.conf.urls.static import static #new
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import ProductSitemap, StaticViewSitemap

sitemaps = {
    "products": ProductSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('about/', views.about, name='about'),
    path('products/', views.product_list, name='products'),
    path('products/<int:category_id>/', views.product_list, name='category_products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
    path('download-catalog/', views.download_catalog_pdf, name='download_catalog_pdf'),
    path('downloads/', views.downloads_view, name='downloads'),
    path('api/search-suggestions/', views.search_suggestions_api, name='search_suggestions_api'),
    # NEW URLs for Quotation System
    path('quote/add-remove/', views.add_remove_from_quote, name='add_remove_from_quote'), # AJAX endpoint
    path('quote/', views.view_quote_cart, name='view_quote_cart'), # View quote cart
    path('quote/submit/', views.submit_quotation_request, name='submit_quotation_request'), # Submit quote
    path('quote/success/', views.quote_success, name='quote_success'), # Success page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)