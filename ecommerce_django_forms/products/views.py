from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.forms import ProductForm
from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB
    products = Product.objects.all()

    # Get up to 4 featured products from the DB
    featured_products = Product.objects.filter(featured=True)

    # This is done for you. The request.session is a dictionary that contains
    # data that will be stored as long as the user is authenticated.
    # We are just initializing an empty list for the products_in_cart, that will
    # be use later on.
    request.session.setdefault('products_in_cart', [])
    request.session.save()

    # Render 'products.html' template sending products and featured products
    # as context
    context = {
        'products':products,
        'featured_products':featured_products,
    }
    
    return render(request, 'products.html',context)


def create_product(request):
    if request.method == 'GET':
        # Create an empty instance of ProductFrom() and render "create_product.html"
        # sending the form as context under "product_form" key
        product_form = ProductForm()
        return render(request, 'create_product.html', context={
            'product_form':product_form
        })
    
    elif request.method == 'POST':
        # Create an instance of ProductFrom initializing it with the product
        # data that come in request.POST
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product = product_form.save()
            
            images = []
            for i in range(3):
                image = product_form.cleaned_data['image_{}'.format(i + 1)]
                if image:
                    images.append(image)
            
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    url=image
                )
            
            
            # Redirect to products view
            return redirect('products')

        # If form is not valid, re-render the 'create_product.html' sending the
        # product_form as context, which will have all the error messages included
        return render(request, 'create_product.html', context={
            'product_form':product_form
        })


def edit_product(request, product_id):
    # Get the product with given product_id from the DB
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        # Create an instance of ProductForm sending the product in the "instance"
        # parameter. This will initialize all the fields in the form with the
        # data from our product.
        product_form = ProductForm(instance=product)

        # Render the 'edit_product.html' template sending the product and the
        # product_form as context
        
        return render(request, 'edit_product.html', context={
            'product_form':product_form,
            'product': product,
        })
    
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        product_form = ProductForm(instance=product)
        return render(
            request,
            'edit_product.html',
            context={
                'product': product,
                'product_form': product_form
            }
        )
    
    elif request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product = product_form.save()

            # Create new images that came in payload, and delete the ones that
            # didn't came in payload but are already created in the DB
            new_images = []
            for i in range(3):
                image = product_form.cleaned_data['image_{}'.format(i + 1)]
                if image:
                    new_images.append(image)

            old_images = [image.url for image in product.productimage_set.all()]

            images_to_delete = []
            for image in old_images:
                if image not in new_images:
                    images_to_delete.append(image)
            ProductImage.objects.filter(url__in=images_to_delete).delete()

            for image in new_images:
                if image not in old_images:
                    ProductImage.objects.create(
                        product=product,
                        url=image
                    )
            return redirect('products')

        return render(
            request,
            'edit_product.html',
            context={
                'product': product,
                'product_form': product_form
            }
        )

def delete_product(request, product_id):
    # Get the product with given product_id from the DB
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        # Render the 'delete_product.html' template sending the product as context
        return render(request, 'delete_product.html',context={
            'product':product
        })
    elif request.method == "POST":
        # Delete the product and redirect to 'products' view
        # YOUR CODE HERE
        product = Product.objects.get(id=product_id)
        product.delete()
        
        return redirect('products')


def toggle_featured(request, product_id):
    # Get the product with given product_id from the DB
    product = Product.objects.get(id=product_id)

    # Toggle the boolean product.featured and save the product
    if product.featured is True:
        product.featured = False
    else:
        product.featured = True
    
    product.save()

    # Redirect to 'products' view
    return redirect('products')


def cart(request):
    # Get all the products ids from the products that have been added to the cart.
    # You can find this ids in the request.session dictionary, under the
    # 'products_in_cart' key. This was explained and initialized in the 'products' view
    products_ids = request.session.get('products_in_cart', [])

    # Get all the products from the DB with the ids above
    products_in_cart = Product.objects.filter(id__in=products_ids)
    

    # Render the 'cart.html' template sending the products_in_cart as context
    return render(request, 'cart.html', context={
        'products_in_cart':products_in_cart,
    })


def add_to_cart(request):
    # Get the product_id that come in request.POST and add it to the
    # list under 'products_in_cart' key of request.session dictionary.
    # Do a .save() to the request.session. This is the way that Django recognizes
    # that something changes in the session.
    product_id = request.POST.get('product_id')
    # YOUR CODE HERE
    request.session['products_in_cart'].append(product_id)
    request.session.save()
    # Redirect to 'products' view
    return redirect('products')


def remove_from_cart(request):
    # Get the product_id that come in request.POST and remove it from the list
    # under 'products_in_cart' of request.session dictionary.
    # Do a .save() to the request.session.
    product_id = request.POST.get('product_id')
    request.session['products_in_cart'].remove(product_id)
    request.session.save()
    # YOUR CODE HERE

    # Redirect to 'cart' view
    return redirect('cart')
