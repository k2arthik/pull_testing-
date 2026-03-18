from django import template

register = template.Library()

@register.filter(name='split_lines')
def split_lines(value):
    """
    Splits a string by newlines and returns a list of non-empty lines.
    """
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]
