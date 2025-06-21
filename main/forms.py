from django import forms
from .models import QuotationRequest

class QuotationRequestForm(forms.ModelForm):
    class Meta:
        model = QuotationRequest
        fields = ['full_name', 'email', 'phone', 'company_name', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Phone Number (Optional)'}),
            'company_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Company Name (Optional)'}),
            'message': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'rows': 4, 'placeholder': 'Any specific requirements or message...'}),
        }

