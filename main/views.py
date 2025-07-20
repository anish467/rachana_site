from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Prefetch
from django.views.decorators.http import require_POST, require_GET

from weasyprint import HTML, CSS

from .forms import QuotationRequestForm
from .models import (
    Category, Product, CategoryParameter, ProductParameterValue, 
    ProductImage, Document, QuotationRequest, QuotationItem,
    CustomerLogo # Import the new model
)


def home(request):
    categories = Category.objects.all().prefetch_related('products')
    
    categories_for_template = []
    for cat in categories:
        categories_for_template.append({
            'id': cat.id,
            'name': cat.name,
            'products': list(cat.products.all())
        })
    
    # NEW: Fetch customer logos
    customer_logos = list(CustomerLogo.objects.all()) # Fetch all logos and convert to list
    
    context = {
        'categories': categories_for_template,
        'customer_logos': customer_logos, # Pass logos to the template
    }
    return render(request, 'main/home.html', context)

def about(request):
    return render(request, 'main/about.html')

def catalog_view(request):
    categories = Category.objects.all().prefetch_related('products')
    
    categories_for_template = []
    for cat in categories:
        categories_for_template.append({
            'id': cat.id,
            'name': cat.name,
            'products': list(cat.products.all())
        })
    
    return render(request, 'main/catalog.html', {'categories': categories_for_template})

def download_catalog_pdf(request):
    all_products = Product.objects.select_related('category').prefetch_related(
        Prefetch(
            'parameter_values',
            queryset=ProductParameterValue.objects.select_related('parameter').order_by('parameter__order')
        )
    ).order_by('category__name', 'name')

    product_pages = []
    current_page_products = []
    for product in all_products:
        current_page_products.append(product)
        if len(current_page_products) == 2:
            product_pages.append(current_page_products)
            current_page_products = []
    
    if current_page_products:
        product_pages.append(current_page_products)

    html_string = render_to_string('main/pdf_catalog.html', {'product_pages': product_pages})

    pdf_stylesheets = [
        CSS(string='''
            /* Basic Page Settings */
            @page {
                size: A4;
                margin: 1cm;
                @top-center { content: "Rachana Corporation Product Catalog"; font-size: 10pt; color: #555; }
                @bottom-center { content: counter(page); font-size: 10pt; color: #555; }
            }
            body { 
                font-family: 'Arial', sans-serif; 
                margin: 0; 
                padding: 0; 
                font-size: 12pt; 
                line-height: 1.6;
                color: #333;
            }

            .page-break { page-break-before: always; }

            .product-card {
                box-sizing: border-box; 
                width: 100%;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-bottom: 30px;
                padding: 20px;
                background-color: white;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                overflow: hidden;
            }
            .product-card:last-child { margin-bottom: 0; }

            .product-image-container {
                width: 100%;
                height: 250px;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #f8fafc;
                border-radius: 6px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            .product-image-container img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
            }

            .product-info { padding: 0; text-align: left; }
            .product-name { 
                font-size: 26px; 
                font-weight: bold; 
                color: #1a202c; 
                margin-bottom: 5px; 
                word-wrap: break-word;
            }
            .product-category { 
                font-size: 14px; 
                color: #718096; 
                margin-bottom: 15px; 
                font-style: italic;
            }
            .product-details { 
                font-size: 15px; 
                color: #4a5568; 
                margin-bottom: 25px; 
            }

            .spec-table-container { margin-top: 20px; }
            .spec-table-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 1px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden;
            }
            .spec-table-grid-cell {
                padding: 10px 15px;
                font-size: 14px;
                line-height: 1.4;
            }
            .spec-table-grid-header {
                background-color: #3182ce;
                color: white;
                font-weight: bold;
                text-align: left;
            }
            .spec-table-grid-value {
                background-color: #fff9c4;
                color: #2d3748;
                text-align: left;
            }
            .spec-table-grid-row:nth-child(even) .spec-table-grid-value {
                background-color: #fffde7;
            }
            .spec-table-grid-row:nth-child(even) .spec-table-grid-header {
                background-color: #2b6cb0;
            }
        ''')
    ]
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    
    pdf_file = html.write_pdf(stylesheets=pdf_stylesheets)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Rachana_Corporation_Catalog.pdf"'
    return response


def product_list(request, category_id=None):
    products = Product.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(details__icontains=query))
        
    if category_id:
        products = products.filter(category_id=category_id)
        current_category = get_object_or_404(Category, id=category_id)
    else:
        current_category = None

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'query': query,
    }
    return render(request, 'main/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch(
                'parameter_values',
                queryset=ProductParameterValue.objects.select_related('parameter').order_by('parameter__order')
            )
        ),
        pk=pk
    )
    is_in_quote_cart = str(product.id) in request.session.get('quote_cart', {})
    
    context = {
        'product': product,
        'is_in_quote_cart': is_in_quote_cart,
    }
    return render(request, 'main/product_detail.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            email_message = EmailMessage(
                subject="New Contact Form Submission from Rachana Corporation Website",
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else "your_email@gmail.com",
                to=["anishagrawal467@gmail.com"],
                reply_to=[email],
            )
            email_message.send()
            success_message = "Your message has been sent successfully!"
            return render(request, 'main/contact.html', {'success_message': success_message})
        except Exception as e:
            error_message = f"There was an error sending your message: {e}"
            print(f"Error sending contact email: {e}") 
            return render(request, 'main/contact.html', {'error_message': error_message, 'name': name, 'email': email, 'message': message})

    return render(request, 'main/contact.html')

def downloads_view(request):
    documents = Document.objects.all()
    return render(request, 'main/downloads.html', {'documents': documents})

def search_suggestions_api(request):
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse({'products': []})

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(details__icontains=query)
    ).values('id', 'name')[:10]

    product_data = list(products)
    return JsonResponse({'products': product_data})


@require_POST
def add_remove_from_quote(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    if not product_id:
        return JsonResponse({'success': False, 'error': 'Product ID is required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    quote_cart = request.session.get('quote_cart', {})
    product_id_str = str(product_id)

    if product_id_str in quote_cart:
        del quote_cart[product_id_str]
        action = 'removed'
    else:
        quote_cart[product_id_str] = {'quantity': quantity, 'name': product.name}
        action = 'added'
    
    request.session['quote_cart'] = quote_cart
    request.session.modified = True

    return JsonResponse({'success': True, 'action': action, 'cart_count': len(quote_cart)})

@require_GET
def view_quote_cart(request):
    quote_cart = request.session.get('quote_cart', {})
    
    product_ids = quote_cart.keys()
    products_in_cart = Product.objects.filter(id__in=product_ids).prefetch_related('images')
    
    quote_items = []
    for product in products_in_cart:
        item_quantity = quote_cart.get(str(product.id), {}).get('quantity', 1)
        quote_items.append({
            'product': product,
            'quantity': item_quantity,
        })
    
    form = QuotationRequestForm()

    context = {
        'quote_items': quote_items,
        'form': form,
        'cart_count': len(quote_cart)
    }
    return render(request, 'main/quote_cart.html', context)

@require_POST
def submit_quotation_request(request):
    quote_cart = request.session.get('quote_cart', {})
    if not quote_cart:
        return redirect('view_quote_cart') 

    form = QuotationRequestForm(request.POST)
    if form.is_valid():
        quotation_request = form.save()

        product_ids = quote_cart.keys()
        products_for_email = Product.objects.filter(id__in=product_ids).prefetch_related(
            Prefetch('parameter_values', queryset=ProductParameterValue.objects.select_related('parameter').order_by('parameter__order')),
            'images'
        )
        
        for product in products_for_email: # Iterate over prefetched products
            item_quantity = quote_cart.get(str(product.id), {}).get('quantity', 1)
            QuotationItem.objects.create(
                quotation_request=quotation_request,
                product=product,
                quantity=item_quantity
            )
        
        quote_details_html = render_to_string('main/email/quotation_email.html', {
            'quotation_request': quotation_request,
            'quote_items': products_for_email, # Pass the prefetched products to email template
            'request': request # Pass request object for absolute URLs in email
        })

        try:
            email_message = EmailMessage(
                subject=f"New Quotation Request from {quotation_request.full_name}",
                body=quote_details_html,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else "your_email@gmail.com",
                to=["anishagrawal467@gmail.com"],
                reply_to=[quotation_request.email],
            )
            email_message.content_subtype = "html"
            email_message.send()
        except Exception as e:
            print(f"Error sending quotation email: {e}")

        del request.session['quote_cart']
        request.session.modified = True

        return redirect('quote_success')
    else:
        product_ids = quote_cart.keys()
        products_in_cart = Product.objects.filter(id__in=product_ids).prefetch_related('images')
        
        quote_items = []
        for product in products_in_cart:
            item_quantity = quote_cart.get(str(product.id), {}).get('quantity', 1)
            quote_items.append({
                'product': product,
                'quantity': item_quantity,
            })
            
        context = {
            'quote_items': quote_items,
            'form': form,
            'cart_count': len(quote_cart)
        }
        return render(request, 'main/quote_cart.html', context)

def quote_success(request):
    return render(request, 'main/quote_success.html')

