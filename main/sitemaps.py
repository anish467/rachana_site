from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product  # Use your actual Product model

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Replace with your actual datetime field

    # This is important — sitemap will use this to generate the URL
    def location(self, obj):
        return reverse("product_detail", args=[obj.pk])


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        # Match the names you used in urls.py
        return ["home", "about", "products", "contact", "downloads"]

    def location(self, item):
        return reverse(item)
