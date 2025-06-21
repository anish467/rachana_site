from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    # Add other fields as needed for Category (e.g., description, image)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    details = models.TextField()
    # price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    # Helper method to get the main image
    @property
    def main_image(self):
        # Tries to get the image marked as main, otherwise returns the first available image
        main_img = self.images.filter(is_main=True).first()
        if main_img:
            return main_img.image_file
        # Fallback: if no main image, return the first image uploaded
        first_img = self.images.first()
        if first_img:
            return first_img.image_file
        return None # No image available

    # Helper method to get other images
    @property
    def other_images(self):
        # Returns all images that are not marked as main
        return self.images.filter(is_main=False)


# New Model: Defines a parameter (e.g., "Tolerance Limit", "Material") for a specific Category
class CategoryParameter(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=255, help_text="e.g., 'Model', 'Tolerance Limit', 'Material of Construction'")
    order = models.IntegerField(default=0, help_text="Order in which this parameter appears in the table")

    class Meta:
        # Ensures that a parameter name is unique within a category
        unique_together = ('category', 'name')
        ordering = ['order', 'name']
        verbose_name = "Category Parameter"
        verbose_name_plural = "Category Parameters" # Corrected from verbose_plural

    def __str__(self):
        return f"{self.name} ({self.category.name})"

# New Model: Stores the actual value for a product for a given CategoryParameter
class ProductParameterValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameter_values')
    parameter = models.ForeignKey(CategoryParameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=500, help_text="Value for this parameter (e.g., 'NC-5K-E1-ASS', '± 2.5 mg')")

    class Meta:
        # Ensures a product has only one value for a given parameter
        unique_together = ('product', 'parameter')
        verbose_name = "Product Parameter Value"
        verbose_name_plural = "Product Parameter Values" # Corrected from verbose_plural

    def __str__(self):
        return f"{self.product.name} - {self.parameter.name}: {self.value}"

# NEW Model: For handling multiple images per product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='product_gallery/')
    is_main = models.BooleanField(default=False, help_text="Check if this is the main image for the product.")
    
    class Meta:
        ordering = ['-is_main', 'id'] # Main image first, then by upload order
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images" # Corrected from verbose_plural

    def __str__(self):
        return f"{self.product.name} - Image {self.id} {'(Main)' if self.is_main else ''}"

# NEW MODEL: For downloadable documents
class Document(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the document (e.g., 'Product Manual', 'Certificate of Calibration')")
    description = models.TextField(blank=True, null=True, help_text="Brief description of the document.")
    file = models.FileField(upload_to='documents/', help_text="Upload the document file (PDF, DOCX, etc.)")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at', 'title'] # Order by most recently uploaded
        verbose_name = "Document"
        verbose_name_plural = "Documents" # Corrected from verbose_plural

    def __str__(self):
        return self.title


# NEW MODELS FOR QUOTATION SYSTEM

class QuotationRequest(models.Model):
    """Represents a submitted quotation request."""
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True, help_text="Any additional message or specific requirements.")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Quotation Request"
        verbose_name_plural = "Quotation Requests" # Corrected from verbose_plural

    def __str__(self):
        return f"Quote from {self.full_name} ({self.email}) - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

class QuotationItem(models.Model):
    """Represents a product included in a quotation request."""
    quotation_request = models.ForeignKey(QuotationRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # You could add more fields here if needed, like 'requested_features', 'custom_notes' for this specific item

    class Meta:
        verbose_name = "Quotation Item"
        verbose_name_plural = "Quotation Items" # Corrected from verbose_plural
        # Ensures a product is not added multiple times to the same request (unless quantities are distinct)
        unique_together = ('quotation_request', 'product') 

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

