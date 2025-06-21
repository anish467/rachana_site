from django.contrib import admin
from .models import Category, Product, CategoryParameter, ProductParameterValue, ProductImage, Document # Import Document

# Inline for CategoryParameter: Allows managing parameters directly when editing a Category
class CategoryParameterInline(admin.TabularInline):
    model = CategoryParameter
    extra = 1
    fields = ('name', 'order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [CategoryParameterInline]

# Inline for ProductParameterValue: Allows managing parameter values directly when editing a Product
class ProductParameterValueInline(admin.TabularInline):
    model = ProductParameterValue
    extra = 1
    fields = ('parameter', 'value')

# Inline for ProductImage: Allows managing multiple images directly when editing a Product
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_file', 'is_main')
    # max_num = 5 # Uncomment to limit number of images

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

# NEW: Register the Document model
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    search_fields = ('title', 'description')
    list_filter = ('uploaded_at',)

