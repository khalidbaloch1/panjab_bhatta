"""nawab_bricks_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,  include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('common.urls', namespace='common')),
    url(r'^customer/', include('batta_customers.urls', namespace='customer')),
    url(r'^stock/', include('batta_stock.urls', namespace='stock')),
    url(r'^sales/', include('batta_sales.urls', namespace='sales')),
    url(r'^expense/', include('batta_expense.urls', namespace='expense')),
    url(r'^staff/', include('batta_staff.urls', namespace='staff')),
    url(r'^koyla/', include('batta_koylas.urls', namespace='koyla')),
    url(r'^other/expense/', include('other_expense.urls', namespace='other_expense')),
    url(r'^account/', include('batta_account.urls', namespace='account')),

]
