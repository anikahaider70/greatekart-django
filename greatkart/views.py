from django.shortcuts import render
from store.models import Product  # ✅ Capitalized model name

def home(request):
    products = Product.objects.filter(is_available=True)  # ✅ also no need for `.all()`
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)


