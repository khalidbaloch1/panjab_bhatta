from django import template

register = template.Library()


@register.assignment_tag
def stock_purchased_amount(stock, season=None):
    amount = stock.purchased_stock_amount(season=season)
    return amount


@register.assignment_tag
def total_stock(stock, season=None):
    total_stock = stock.total_stock(season=season)
    return total_stock


@register.assignment_tag
def available_stock(stock, season=None):
    total_stock = stock.available_stock(season=season)
    return total_stock


@register.assignment_tag
def purchased_stock(stock, season=None):
    total_stock = stock.purchased_stock(season=season)
    return total_stock


@register.simple_tag
def update_variable(value):
    data = value
    return data


@register.filter(is_safe=False)
def subtract(value, arg):
    """Adds the arg to the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ''
