from django import template
from django.utils.html import format_html
from datetime import datetime
import pytz

register = template.Library()

@register.simple_tag
def display_brazil_time():
    # Define the timezone for São Paulo, Brazil
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    
    # Get the current time in UTC and convert it to São Paulo time
    sao_paulo_time = datetime.now(pytz.utc).astimezone(sao_paulo_tz)
    
    # Format the time as a string
    formatted_time = sao_paulo_time.strftime('%Y-%m-%d %H:%M')
    
    # Determine if it's day or night
    hour = sao_paulo_time.hour
    if 6 <= hour < 18:
        emoji = '☀️'  # Sun emoji for day time
    else:
        emoji = '🌙'  # Moon emoji for night time
    
    # Return the formatted time with the appropriate emoji
    return format_html(f"{formatted_time} {emoji}")