from django import forms
from .models import CartItem, Variation
class CartItemForm(forms.ModelForm):
    color = forms.ModelChoiceField(
        queryset=Variation.objects.filter(variation_category='color'),
        required=False
    )
    size = forms.ModelChoiceField(
        queryset=Variation.objects.filter(variation_category='size'),
        required=False
    )

    class Meta:
        model = CartItem
        fields = ['product', 'cart', 'quantity', 'is_active', 'color', 'size']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if self.cleaned_data.get('color'):
                instance.variations.add(self.cleaned_data['color'])
            if self.cleaned_data.get('size'):
                instance.variations.add(self.cleaned_data['size'])
        return instance