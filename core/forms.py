from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import PriestProfile, DevoteeProfile, SEOMetadata, validate_hyderabad

class SEOMetadataForm(forms.ModelForm):
    class Meta:
        model = SEOMetadata
        fields = ['path', 'title_tag', 'meta_description', 'keywords']
        widgets = {
            'path': forms.TextInput(attrs={'placeholder': 'e.g., /services/', 'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'placeholder': 'Meta Title Tag', 'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Meta Description', 'class': 'form-control'}),
            'keywords': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Keywords (comma separated)', 'class': 'form-control'}),
        }
from django.utils.safestring import mark_safe
from .models import Puja

class PujaForm(forms.ModelForm):
    class Meta:
        model = Puja
        fields = [
            'title', 'category', 'short_description', 'full_description', 'page_description',
            'benefits', 'inclusions', 'image', 'duration', 'price', 
            'pandits', 'location', 'deity', 'required_purohits', 
            'is_active', 'is_featured', 'display_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'full_description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'page_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'benefits': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'inclusions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 hours'}),
            'pandits': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'deity': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'required_purohits': forms.NumberInput(attrs={'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PriestRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True)
    photo = forms.ImageField(required=True)  # Required at registration
    language = forms.CharField(required=True, help_text="Enter languages separated by commas (e.g., Telugu, Hindi, English)")
    
    class Meta:
        model = PriestProfile
        fields = [
            'fullname', 'mobile', 'experience', 'language',
            'gothram', 'qualification', 'qualification_place',
            'formal_vedic_training', 'knows_smaardham', 'organize_scientifically',
            'can_perform_rituals', 'location', 'specialization',
            'photo', 'certificate', 'id_proof'
        ]
        widgets = {
            'gothram': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your Gothram'}),
            'qualification': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Highest Educational Qualification'}),
            'qualification_place': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Gurukulam / Vedic Institution'}),
            'formal_vedic_training': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'knows_smaardham': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'organize_scientifically': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'can_perform_rituals': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }
        labels = {
            'qualification': 'Highest Educational Qualification',
            'qualification_place': 'Gurukulam / Vedic Institution',
            'formal_vedic_training': 'Have you formally undergone Vedic training?',
            'knows_smaardham': 'Have you know of the Veda called Smaardham?',
            'organize_scientifically': 'Can you organize the program scientifically?',
            'can_perform_rituals': 'Can perform as per scriptures?',
        }
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            mobile = str(mobile).strip()
            if not mobile.isdigit():
                raise forms.ValidationError("Mobile number must contain only digits.")
            if len(mobile) != 10:
                raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            try:
                validate_hyderabad(location)
            except ValidationError as e:
                raise forms.ValidationError(e.message)
        return location

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered. Please use another email.")
        return email

    def clean_language(self):
        language = self.cleaned_data.get('language')
        if isinstance(language, str):
            # Split by comma if it's a string from CharField or test data
            return [s.strip() for s in language.split(',') if s.strip()]
        return [language] if language else []
    
    

class PriestEditForm(forms.ModelForm):
    language = forms.CharField(required=True, help_text="Enter languages separated by commas (e.g., Telugu, Hindi, English)")

    class Meta:
        model = PriestProfile
        fields = [
            'fullname', 'mobile', 'experience', 'language',
            'gothram', 'qualification', 'qualification_place',
            'formal_vedic_training', 'knows_smaardham', 'organize_scientifically',
            'can_perform_rituals', 'location', 'specialization',
            'photo', 'certificate', 'id_proof'
        ]
        widgets = {
            'gothram': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your Gothram'}),
            'qualification': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your Divine Qualifications'}),
            'qualification_place': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter place of qualification'}),
            'formal_vedic_training': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'knows_smaardham': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'organize_scientifically': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'can_perform_rituals': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }
        labels = {
            'qualification': 'Highest Educational Qualification',
            'qualification_place': 'Gurukulam / Vedic Institution',
            'formal_vedic_training': 'Have you formally undergone Vedic training?',
            'knows_smaardham': 'Have you know of the Veda called Smaardham?',
            'organize_scientifically': 'Can you organize the program scientifically?',
            'can_perform_rituals': 'Can perform as per scriptures?',
        }
    
    def clean_language(self):
        language = self.cleaned_data.get('language')
        if isinstance(language, str):
            return [s.strip() for s in language.split(',') if s.strip()]
        return [language] if language else []

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            mobile = str(mobile).strip()
            if not mobile.isdigit():
                raise forms.ValidationError("Mobile number must contain only digits.")
            if len(mobile) != 10:
                raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            try:
                validate_hyderabad(location)
            except ValidationError as e:
                raise forms.ValidationError(e.message)
        return location

class DevoteeRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = DevoteeProfile
        fields = ['fullname', 'mobile', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your address in Hyderabad', 'required': True}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            mobile = str(mobile).strip()
            if not mobile.isdigit():
                raise forms.ValidationError("Mobile number must contain only digits.")
            if len(mobile) != 10:
                raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            try:
                validate_hyderabad(address)
            except ValidationError as e:
                raise forms.ValidationError(e.message)
        return address

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered. Please use another email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class PriestLoginForm(forms.Form):
    login_id = forms.CharField(label="Mobile Number or Email", help_text="Enter your 10-digit mobile number or registered email")
    password = forms.CharField(widget=forms.PasswordInput())

class PurohitResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create new password'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            error_message = mark_safe('<span style="color: red; font-weight: bold;">Passwords do not match.</span>')
            raise forms.ValidationError(error_message)
        
        return cleaned_data
class AdminDevoteeEditForm(forms.ModelForm):
    class Meta:
        model = DevoteeProfile
        fields = ['fullname', 'mobile', 'address']
        css_class = 'sacred-input'
        widgets = {
            'fullname': forms.TextInput(attrs={'class': css_class}),
            'mobile': forms.TextInput(attrs={'class': css_class}),
            'address': forms.Textarea(attrs={'class': css_class, 'rows': 3}),
        }

class AdminPurohitEditForm(forms.ModelForm):
    class Meta:
        model = PriestProfile
        fields = ['fullname', 'mobile', 'location', 'experience', 'qualification', 'qualification_place']
        css_class = 'sacred-input'
        widgets = {
            'fullname': forms.TextInput(attrs={'class': css_class}),
            'mobile': forms.TextInput(attrs={'class': css_class}),
            'location': forms.Textarea(attrs={'class': css_class, 'rows': 2}),
            'experience': forms.NumberInput(attrs={'class': css_class}),
            'qualification': forms.TextInput(attrs={'class': css_class}),
            'qualification_place': forms.TextInput(attrs={'class': css_class}),
        }
