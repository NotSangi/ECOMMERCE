from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'state', 'city', 'country', 'order_note']
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args,**kwargs)
        if user and user.is_authenticated:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone_number
        
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Enter Address'
        self.fields['address_line_2'].widget.attrs['placeholder'] = 'Enter Address Detail'
        self.fields['state'].widget.attrs['placeholder'] = 'Enter State'
        self.fields['city'].widget.attrs['placeholder'] = 'Enter City'
        self.fields['country'].widget.attrs['placeholder'] = 'Enter Country'
        self.fields['order_note'].widget.attrs['placeholder'] = 'Enter an Order Note'

        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'