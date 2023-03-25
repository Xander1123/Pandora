from django.shortcuts import render
from store.models import Product,Category


def home(request):
    products=Product.objects.all().filter(is_aviable=True)

    context={
        'products':products,
    }
    return render(request,'home.html',context)