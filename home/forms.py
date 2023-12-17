from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Category, Product, Review
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']
        labels = {'name': 'Name','parent': 'Parent'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)

class DeleteCategoryForm(forms.Form):
    category_ids = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'description', 'base_price', 'number_in_stock']
        labels = {'number_in_stock': 'Num in stock'}
    
    def clean_number_in_stock(self):
        number_in_stock = self.cleaned_data.get('number_in_stock')
        if number_in_stock is not None and number_in_stock <= 0:
            raise forms.ValidationError(_('The number in stock must be a positive integer.'))
        return number_in_stock

    def clean_base_price(self):
        base_price = self.cleaned_data.get('base_price')
        if base_price is not None and base_price <= 0:
            raise forms.ValidationError(_('The base price must be a positive integer.'))
        return base_price

class DeleteProductForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

class ADCustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

class DeleteCustomUserForm(forms.Form):
    user_ids = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

class CustomUserDetailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address', 'is_staff']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
