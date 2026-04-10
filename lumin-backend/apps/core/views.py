"""
Core views for Lumin SaaS.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from functools import wraps


def onboarding_required(view_func):
    """
    Decorator that checks if user completed onboarding.
    If not, redirects to phone verification (first step).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.onboarding_completed:
            # Redirect to onboarding flow
            return redirect('phone_verification')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    """
    Home page with links to important resources.
    """
    context = {
        'project_name': 'Lumin - מערכת ניהול עסקית',
        'version': '1.0.0',
        'endpoints': {
            'Admin Panel': '/admin/',
            'API Documentation': '/api/',
            'Authentication': '/api/auth/',
            'Users API': '/api/users/',
            'Products API': '/api/products/',
            'Orders API': '/api/orders/',
            'Customers API': '/api/customers/',
            'Analytics API': '/api/analytics/',
        }
    }
    return render(request, 'home.html', context)


def api_root(request):
    """
    API root endpoint showing available endpoints.
    """
    return JsonResponse({
        'message': 'Welcome to Lumin API',
        'version': '1.0.0',
        'endpoints': {
            'accounts': '/api/accounts/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'customers': '/api/customers/',
            'analytics': '/api/analytics/',
            'integrations': '/api/integrations/',
        },
        'documentation': '/admin/',
    })


@login_required
@onboarding_required
def splash_screen(request):
    """
    Splash screen shown after login before dashboard.
    """
    return render(request, 'splash.html')


@login_required
@onboarding_required
def dashboard(request):
    """
    Main dashboard view for logged-in users.
    """
    user = request.user
    tenant = user.tenant
    
    # Fetch recent activity
    from apps.customers.models import Treatment, Customer
    from apps.sales.models import Order
    from itertools import chain
    from operator import attrgetter

    # Recent treatments
    recent_treatments = Treatment.objects.filter(tenant=tenant).select_related('customer', 'treatment_type').order_by('-created_at')[:5]
    
    # Recent orders
    recent_orders = Order.objects.filter(tenant=tenant).select_related('customer').order_by('-created_at')[:5]
    
    # New customers
    new_customers = Customer.objects.filter(tenant=tenant).order_by('-created_at')[:5]

    # Combine and sort, taking the 10 most recent
    activity_stream = sorted(
        chain(recent_treatments, recent_orders, new_customers),
        key=attrgetter('created_at'),
        reverse=True
    )[:10]

    # Tag items with type for template rendering
    for item in activity_stream:
        if isinstance(item, Treatment):
            item.activity_type = 'treatment'
        elif isinstance(item, Order):
            item.activity_type = 'order'
        elif isinstance(item, Customer):
            item.activity_type = 'customer'

    # Calculate KPIs
    from django.db.models import Sum, Count
    from django.utils import timezone
    from apps.inventory.models import Product

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Sales & Orders (This Month)
    sales_data = Order.objects.filter(
        tenant=tenant, 
        created_at__gte=month_start
    ).aggregate(
        total_sales=Sum('total_amount'),
        total_orders=Count('id')
    )
    kpi_sales_month = sales_data['total_sales'] or 0
    kpi_orders_month = sales_data['total_orders'] or 0

    # Customers
    kpi_customers_total = Customer.objects.filter(tenant=tenant).count()
    kpi_customers_new = Customer.objects.filter(
        tenant=tenant, 
        created_at__gte=month_start
    ).count()

    # Products
    kpi_products_total = Product.objects.filter(tenant=tenant).count()
    kpi_products_new = Product.objects.filter(
        tenant=tenant, 
        created_at__gte=month_start
    ).count()

    context = {
        'user': user,
        'tenant': tenant,
        'business_name': tenant.business_name if tenant else 'העסק שלי',
        'activities': activity_stream,
        
        # KPIs
        'kpi_sales_month': kpi_sales_month,
        'kpi_orders_month': kpi_orders_month,
        'kpi_customers_total': kpi_customers_total,
        'kpi_customers_new': kpi_customers_new,
        'kpi_products_total': kpi_products_total,
        'kpi_products_new': kpi_products_new,
    }

    return render(request, 'dashboard.html', context)


# Onboarding Views (4-step flow)
@login_required
def phone_verification(request):
    """
    Step 1/4: Phone verification (25%).
    """
    return render(request, 'onboarding/phone_verification.html')


@login_required
def verify_code(request):
    """
    Step 1.5: Verify OTP code (for phone verification).
    """
    return render(request, 'onboarding/verify_code.html')


@login_required
def business_basics(request):
    """
    Step 2/4: Business basics - name and category (50%).
    """
    return render(request, 'onboarding/business_basics.html')


@login_required
def business_details(request):
    """
    Step 3/4: Business details - size, revenue, goal (75%).
    """
    return render(request, 'onboarding/business_details_step3.html')


@login_required
def business_branding(request):
    """
    Step 4/4: Business branding - logo and description (100%).
    """
    return render(request, 'onboarding/business_branding.html')


@login_required
def onboarding_complete(request):
    """
    Final step: Onboarding complete - celebrate!
    """
    # Mark onboarding as complete
    if request.method == 'POST':
        request.user.onboarding_completed = True
        request.user.save()
        return redirect('splash')

    return render(request, 'onboarding/complete.html')
@login_required
@onboarding_required
def settings(request):
    """
    Settings page - user profile, business details, account settings.
    """
    return render(request, 'settings.html')
