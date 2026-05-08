from django import template

register = template.Library()


@register.filter
def intcomma(value):
    """Convert a number to a string with commas."""
    if value is None:
        return "0"
    try:
        value = int(value)
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value
