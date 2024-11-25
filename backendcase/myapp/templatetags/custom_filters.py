from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def time_diff(check_out, check_in):
    if check_out and check_in:
        diff = check_out - check_in
        hours = diff.seconds // 3600
        minutes = (diff.seconds // 60) % 60
        return f"{hours} saat, {minutes} dakika"
    return "Veri eksik"
