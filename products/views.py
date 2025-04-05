from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReviewForm
from django.db.models import Avg
from .models import Review
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Product, Category

# This function checks if user is admin
def is_admin(user):
    return user.is_superuser

def home(request):
    """Home page view with featured products"""
    context = {
        'products': Product.objects.all()[:6],  # Show only 6 products on home page
        'categories': Category.objects.all(),
        'title': 'Home'
    }
    return render(request, 'products/home.html', context)

class ProductListView(ListView):
    """View all products with pagination"""
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'products'
    ordering = ['-date_posted']
    paginate_by = 8
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Products'
        context['categories'] = Category.objects.all()
        return context

class UserProductListView(ListView):
    model = Product
    template_name = 'products/user_products.html'
    context_object_name = 'products'
    paginate_by = 8
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return Product.objects.filter(seller=user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        context['title'] = f"{username}'s Products"
        context['seller'] = user
        return context

# class ProductDetailView(DetailView):
    """View product details"""
    model = Product
    template_name = 'products/product_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context

def product_detail(request, pk):
    """View product details with reviews"""
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all()
    
    # Initialize variables
    review_form = None
    has_reviewed = False
    
    if request.user.is_authenticated:
        # Check if user already reviewed this product
        has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        
        # Form handling
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                existing_review = Review.objects.filter(product=product, user=request.user).first()
                
                if existing_review:
                    # Update existing review
                    existing_review.rating = review_form.cleaned_data['rating']
                    existing_review.comment = review_form.cleaned_data['comment']
                    existing_review.save()
                    messages.success(request, "Your review has been updated!")
                else:
                    # Create new review
                    new_review = review_form.save(commit=False)
                    new_review.product = product
                    new_review.user = request.user
                    new_review.save()
                    messages.success(request, "Your review has been added!")
                    
                return redirect('product-detail', pk=pk)
        else:
            # Pre-populate form if user has already reviewed
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                review_form = ReviewForm(instance=existing_review)
            else:
                review_form = ReviewForm()
    else:
        review_form = ReviewForm()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'avg_rating': avg_rating,
        'has_reviewed': has_reviewed,  # Add this variable
        'title': product.name
    }
    return render(request, 'products/product_detail.html', context)

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create new product (admin only)"""
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'description', 'price', 'category', 'sustainability_score', 'materials', 'image', 'in_stock']
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Product'
        context['button_text'] = 'Add Product'
        return context

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update existing product (admin only)"""
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'description', 'price', 'category', 'sustainability_score', 'materials', 'image', 'in_stock']
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Product'
        context['button_text'] = 'Update Product'
        return context

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete product (admin only)"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = '/'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Product'
        return context

def category_products(request, category_id):
    """View products by category"""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by('-date_posted')
    
    context = {
        'category': category,
        'products': products,
        'title': f'{category.name} Products'
    }
    return render(request, 'products/category_products.html', context)