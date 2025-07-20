from django.contrib import admin
from .models import (
    Category, Product, CategoryParameter, ProductParameterValue, 
    ProductImage, Document, QuotationRequest, QuotationItem,
    CustomerLogo # Import the new model
)

# Inline for CategoryParameter
class CategoryParameterInline(admin.TabularInline):
    model = CategoryParameter
    extra = 1
    fields = ('name', 'order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [CategoryParameterInline]

# Inline for ProductParameterValue
class ProductParameterValueInline(admin.TabularInline):
    model = ProductParameterValue
    extra = 1
    fields = ('parameter', 'value')

# Inline for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_file', 'is_main')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_main_image_thumbnail')
    list_filter = ('category',)
    search_fields = ('name', 'details')
    inlines = [ProductImageInline, ProductParameterValueInline]

    def get_main_image_thumbnail(self, obj):
        if obj.main_image:
            return admin.display(description="Main Image")(lambda _: f'<img src="{obj.main_image.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />')
        return "No Image"
    get_main_image_thumbnail.allow_tags = True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        main_images = obj.images.filter(is_main=True)
        if main_images.count() > 1:
            last_main = main_images.latest('id')
            for img in main_images.exclude(id=last_main.id):
                img.is_main = False
                img.save()
        elif main_images.count() == 0 and obj.images.exists():
            first_img = obj.images.first()
            if first_img:
                first_img.is_main = True
                first_img.save()

# Register Document model
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    search_fields = ('title', 'description')
    list_filter = ('uploaded_at',)

# NEW: Inline for QuotationItem - define it as a class
class QuotationItemInline(admin.TabularInline): # Corrected: Define a class for the inline
    model = QuotationItem # Corrected: 'model' is an attribute of the class, not an arg to constructor
    extra = 0
    fields = ['product', 'quantity']

@admin.register(QuotationRequest)
class QuotationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company_name', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('full_name', 'email', 'company_name', 'message')
    inlines = [QuotationItemInline] # Corrected: Use the class name here
    readonly_fields = ('submitted_at',)

# Register CustomerLogo model
@admin.register(CustomerLogo)
class CustomerLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_image', 'website_url', 'order')
    list_editable = ('order',)
    search_fields = ('name',)

