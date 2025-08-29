from django import forms
from django.core.validators import RegexValidator
from .models import Contact

class ContactForm(forms.ModelForm):
    """Contact form with enhanced validation and styling"""
    
    # Enhanced validation
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Your Full Name',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$',
                message='Name can only contain letters and spaces'
            )
        ]
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'your.email@example.com',
            'required': True
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': '+1 (555) 123-4567',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^[\+]?[1-9][\d]{0,15}$',
                message='Enter a valid phone number'
            )
        ]
    )
    
    company = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Your Company Name',
            'required': True
        })
    )
    
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Your Country',
            'required': True
        })
    )
    
    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Your Job Title',
            'required': True
        })
    )
    
    job_details = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none',
            'placeholder': 'Tell us about your project requirements, challenges, and goals...',
            'rows': 5,
            'required': True
        })
    )
    
    # Honeypot field for spam protection
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'company', 'country', 'job_title', 'job_details']
    
    def clean_website(self):
        """Honeypot validation - if filled, it's likely spam"""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError("Form submission failed. Please try again.")
        return website
    
    def clean(self):
        """Additional validation logic"""
        cleaned_data = super().clean()
        
        # Check if email contains suspicious patterns
        email = cleaned_data.get('email')
        if email:
            suspicious_patterns = ['test@', 'example@', 'spam@']
            if any(pattern in email.lower() for pattern in suspicious_patterns):
                raise forms.ValidationError("Please provide a valid business email address.")
        
        # Check if job details are too short
        job_details = cleaned_data.get('job_details')
        if job_details and len(job_details.strip()) < 20:
            raise forms.ValidationError("Please provide more details about your project requirements.")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add error styling
        for field_name, field in self.fields.items():
            if field_name != 'website':  # Skip honeypot field
                field.widget.attrs.update({
                    'class': field.widget.attrs.get('class', '') + ' error:border-red-500 error:focus:ring-red-500'
                })
