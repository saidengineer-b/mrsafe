from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import  StoreItem
from django import forms
from django.contrib.auth.forms import PasswordResetForm

# ✅ Get the Custom User Model
CustomUser = get_user_model()

# ✅ User Registration Form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter a password"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm your password"}),
        }

# ✅ Login Form (Email + Password)
class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

# ✅ Profile Editing Form
class EditProfileForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_photo', 'password']
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter first name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email"}),
            "password": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password (optional)"}),
        }
from django import forms
from .models import CustomUser
class EditUserForm(forms.ModelForm):
    """
    ✅ Form for editing user details including username, email, profile photo, coin balance, and admin privileges.
    """
    coin_balance = forms.IntegerField(
        min_value=0,
        required=False,
        label="Coin Balance",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Coin Balance"}),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_photo", "is_premium", "is_active", "is_staff"]

    def __init__(self, *args, **kwargs):
        """ ✅ Initialize form with user balance data """
        user = kwargs.pop("user", None)  # Get user object
        super().__init__(*args, **kwargs)

        if user:
            user_balance = UserCoinBalance.objects.filter(user=user).first()
            if user_balance:
                self.fields["coin_balance"].initial = user_balance.balance  # ✅ FIX: Ensure correct balance

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Enter Username"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Enter Email"})
        self.fields["profile_photo"].widget.attrs.update({"class": "form-control"})
        self.fields["is_premium"].widget.attrs.update({"class": "form-check-input"})
        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})
        self.fields["is_staff"].widget.attrs.update({"class": "form-check-input"})

        

# ✅ Quiz Form__________________________________________________________________________






from django import forms
from .models import StoreItem

class StoreItemForm(forms.ModelForm):
    ITEM_TYPE_CHOICES = [
        ('coins', 'Coins'),
        ('membership', 'Membership'),
        ('book', 'Book'),
        ('other', 'Other'),
    ]

    item_type = forms.ChoiceField(choices=ITEM_TYPE_CHOICES, required=True)

    class Meta:
        model = StoreItem
        fields = ['name', 'description', 'price', 'item_type', 'coins_amount', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'coins_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



from django import forms
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
            'required': True
        })
    )

    # ✅ Custom clean method to validate email existence
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.get_users(email):
            raise forms.ValidationError("No account is associated with this email address.")
        return email



##############################################################################################

#############################################################################################

#############################################################################################

from django import forms
from .models import PremiumPlan

class PremiumPlanForm(forms.ModelForm):
    class Meta:
        model = PremiumPlan
        fields = ['name', 'duration_days', 'coin_bonus', 'price', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].choices = PremiumPlan.PLAN_CHOICES
    
  # mrsafe_app/forms.py
from django import forms

class HazardForm(forms.Form):
    title = forms.CharField(max_length=200)
    severity = forms.ChoiceField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')])
    description = forms.CharField(widget=forms.Textarea)
    oshas = forms.CharField(widget=forms.Textarea, required=False)

class RecommendationForm(forms.Form):
    title = forms.CharField(max_length=200)
    action = forms.CharField(widget=forms.Textarea)
    ppe = forms.CharField(required=False)
    training = forms.CharField(required=False)
    timeline = forms.CharField(required=False)

from django import forms

class HazardRecommendationForm(forms.Form):
    # Hazard Fields
    hazard_title = forms.CharField(label="Hazard Title", max_length=200)
    severity = forms.ChoiceField(label="Severity", choices=[
        ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')
    ])
    description = forms.CharField(label="Description", widget=forms.Textarea)
    osha_reference = forms.CharField(label="OSHA Reference", widget=forms.Textarea, required=False)

    # Recommendation Fields
    recommendation_action = forms.CharField(label="Recommended Action", widget=forms.Textarea)
    ppe = forms.CharField(label="PPE", required=False)
    training = forms.CharField(label="Training", required=False)
    engineering_control = forms.CharField(label="Engineering Control", required=False)
    timeline = forms.CharField(label="Timeline", required=False)

from django import forms
from .models import SiteInspection
class SiteInspectionForm(forms.ModelForm):
    class Meta:
        model = SiteInspection
        fields = ['title', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django.contrib.auth.decorators import login_required

@login_required
def inspection_create(request):
    if request.method == 'POST':
        form = SiteInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.inspector = request.user
            inspection.save()
            return redirect('mrsafe_app:inspection_detail', inspection_id=inspection.id)
    else:
        form = SiteInspectionForm()
    
    return render(request, 'mrsafe/inspection/create.html', {'form': form})
