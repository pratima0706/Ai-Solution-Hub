from django import forms
from django.core.validators import RegexValidator
from .models import Contact, NewsletterSubscriber

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
            'placeholder': '+44 191 234 5678',
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
    
    country = forms.ChoiceField(
        choices=[
            ('', 'Select your country'),
            ('GB', 'United Kingdom'),
            ('US', 'United States'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('NL', 'Netherlands'),
            ('IE', 'Ireland'),
            ('ES', 'Spain'),
            ('IT', 'Italy'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('CH', 'Switzerland'),
            ('AT', 'Austria'),
            ('BE', 'Belgium'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('JP', 'Japan'),
            ('IN', 'India'),
            ('BR', 'Brazil'),
            ('MX', 'Mexico'),
            ('PT', 'Portugal'),
            ('GR', 'Greece'),
            ('PL', 'Poland'),
            ('CZ', 'Czech Republic'),
            ('HU', 'Hungary'),
            ('RO', 'Romania'),
            ('BG', 'Bulgaria'),
            ('HR', 'Croatia'),
            ('SI', 'Slovenia'),
            ('SK', 'Slovakia'),
            ('LT', 'Lithuania'),
            ('LV', 'Latvia'),
            ('EE', 'Estonia'),
            ('LU', 'Luxembourg'),
            ('MT', 'Malta'),
            ('CY', 'Cyprus'),
            ('OTHER', 'Other (Please specify)'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'required': True
        })
    )
    
    # Additional field for "Other" country
    other_country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter your country name'
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
        fields = ['name', 'email', 'phone', 'company', 'country', 'job_title', 'job_details', 'form_type']
        widgets = {
            'form_type': forms.HiddenInput(),
        }
    
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
        
        # Validate country selection
        country = cleaned_data.get('country')
        other_country = cleaned_data.get('other_country')
        
        if country == 'OTHER' and not other_country:
            raise forms.ValidationError("Please specify your country when selecting 'Other'.")
        
        # If "Other" is selected, use the other_country value
        if country == 'OTHER' and other_country:
            cleaned_data['country'] = other_country
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add error styling
        for field_name, field in self.fields.items():
            if field_name != 'website':  # Skip honeypot field
                field.widget.attrs.update({
                    'class': field.widget.attrs.get('class', '') + ' error:border-red-500 error:focus:ring-red-500'
                })


class DemoRequestForm(forms.ModelForm):
    """Demo request form with enhanced validation and styling"""
    
    # Enhanced validation
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
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
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+44 191 234 5678'
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
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Company Name'
        })
    )
    
    country = forms.ChoiceField(
        choices=[
            ('', 'Select your country'),
            ('GB', 'United Kingdom'),
            ('US', 'United States'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('NL', 'Netherlands'),
            ('IE', 'Ireland'),
            ('ES', 'Spain'),
            ('IT', 'Italy'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('CH', 'Switzerland'),
            ('AT', 'Austria'),
            ('BE', 'Belgium'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('JP', 'Japan'),
            ('IN', 'India'),
            ('BR', 'Brazil'),
            ('MX', 'Mexico'),
            ('PT', 'Portugal'),
            ('GR', 'Greece'),
            ('PL', 'Poland'),
            ('CZ', 'Czech Republic'),
            ('HU', 'Hungary'),
            ('RO', 'Romania'),
            ('BG', 'Bulgaria'),
            ('HR', 'Croatia'),
            ('SI', 'Slovenia'),
            ('SK', 'Slovakia'),
            ('LT', 'Lithuania'),
            ('LV', 'Latvia'),
            ('EE', 'Estonia'),
            ('LU', 'Luxembourg'),
            ('MT', 'Malta'),
            ('CY', 'Cyprus'),
            ('OTHER', 'Other (Please specify)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    # Additional field for "Other" country
    other_country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your country name'
        })
    )
    
    interest = forms.ChoiceField(
        choices=[
            ('', 'Select your interest'),
            ('ai_virtual_assistant', 'AI-Powered Virtual Assistant'),
            ('prototyping_solutions', 'AI-Based Prototyping Solutions'),
            ('personalized_demo', 'Personalized Solution Demo'),
            ('promotional_events', 'Join Our Events'),
            ('general_inquiry', 'General Inquiry'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about your specific needs, challenges, or questions...',
            'rows': 4
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
        fields = ['name', 'email', 'phone', 'company', 'country', 'interest', 'message', 'form_type']
        widgets = {
            'form_type': forms.HiddenInput(),
        }
    
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
        
        # Validate country selection
        country = cleaned_data.get('country')
        other_country = cleaned_data.get('other_country')
        
        if country == 'OTHER' and not other_country:
            raise forms.ValidationError("Please specify your country when selecting 'Other'.")
        
        # If "Other" is selected, use the other_country value
        if country == 'OTHER' and other_country:
            cleaned_data['country'] = other_country
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add error styling
        for field_name, field in self.fields.items():
            if field_name != 'website':  # Skip honeypot field
                field.widget.attrs.update({
                    'class': field.widget.attrs.get('class', '') + ' error:border-red-500 error:focus:ring-red-500'
                })


class EventRegistrationForm(forms.ModelForm):
    """Event registration form with enhanced validation and styling"""
    
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
            'placeholder': '+44 191 234 5678',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^[\+]?[1-9][\d]{0,15}$',
                message='Enter a valid phone number'
            )
        ]
    )
    
    country = forms.ChoiceField(
        choices=[
            ('', 'Select your country'),
            ('GB', 'United Kingdom'),
            ('US', 'United States'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('NL', 'Netherlands'),
            ('IE', 'Ireland'),
            ('ES', 'Spain'),
            ('IT', 'Italy'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('CH', 'Switzerland'),
            ('AT', 'Austria'),
            ('BE', 'Belgium'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('JP', 'Japan'),
            ('IN', 'India'),
            ('BR', 'Brazil'),
            ('MX', 'Mexico'),
            ('PT', 'Portugal'),
            ('GR', 'Greece'),
            ('PL', 'Poland'),
            ('CZ', 'Czech Republic'),
            ('HU', 'Hungary'),
            ('RO', 'Romania'),
            ('BG', 'Bulgaria'),
            ('HR', 'Croatia'),
            ('SI', 'Slovenia'),
            ('SK', 'Slovakia'),
            ('LT', 'Lithuania'),
            ('LV', 'Latvia'),
            ('EE', 'Estonia'),
            ('LU', 'Luxembourg'),
            ('MT', 'Malta'),
            ('CY', 'Cyprus'),
            ('OTHER', 'Other (Please specify)'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'required': True
        })
    )
    
    # Additional field for "Other" country
    other_country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
            'placeholder': 'Enter your country name'
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
        fields = ['name', 'email', 'phone', 'country', 'form_type']
        widgets = {
            'form_type': forms.HiddenInput(),
        }
    
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
        
        # Validate country selection
        country = cleaned_data.get('country')
        other_country = cleaned_data.get('other_country')
        
        if country == 'OTHER' and not other_country:
            raise forms.ValidationError("Please specify your country when selecting 'Other'.")
        
        # If "Other" is selected, use the other_country value
        if country == 'OTHER' and other_country:
            cleaned_data['country'] = other_country
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add error styling
        for field_name, field in self.fields.items():
            if field_name != 'website':  # Skip honeypot field
                field.widget.attrs.update({
                    'class': field.widget.attrs.get('class', '') + ' error:border-red-500 error:focus:ring-red-500'
                })


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'flex-1 px-6 py-4 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200',
            'placeholder': 'Enter your email address',
            'required': True
        })
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
    
    def clean_email(self):
        """Validate email and check for existing subscription"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists and is active
            existing = NewsletterSubscriber.objects.filter(email=email, is_active=True).exists()
            if existing:
                raise forms.ValidationError("This email is already subscribed to our newsletter.")
        return email
    
    def save(self, request=None, commit=True):
        """Save with additional metadata"""
        instance = super().save(commit=False)
        
        if request:
            instance.ip_address = self.get_client_ip(request)
            instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
            instance.source = 'website'
        
        if commit:
            instance.save()
        return instance
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
