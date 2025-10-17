"""
Core views for Lumin SaaS.
"""
from django.shortcuts import render
from django.http import JsonResponse


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
            'auth': '/api/auth/',
            'users': '/api/users/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'customers': '/api/customers/',
            'analytics': '/api/analytics/',
        },
        'documentation': '/admin/',  # For now, admin serves as docs
    })
