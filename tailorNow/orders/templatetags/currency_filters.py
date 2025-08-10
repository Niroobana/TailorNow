from django import template

register = template.Library()


@register.filter(name='currency_cents')
def currency_cents(value, code='LKR'):
    try:
        cents = int(value or 0)
    except Exception:
        cents = 0
    amount = cents / 100.0
    symbol = 'රු'
    if code.upper() == 'LKR':
        return f"{symbol} {amount:,.2f}"
    return f"{amount:,.2f} {code}"



