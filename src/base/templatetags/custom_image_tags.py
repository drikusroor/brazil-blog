from django import template
from wagtail.images.models import Image

register = template.Library()

@register.filter(name='advanced_image')
def advanced_image(image, args=''):
    if not isinstance(image, Image):
        return ""

    # Set default values
    defaults = {
        'fill': '512x512',
        'bgcolor': 'transparent',  # Default to black or any other color
        'format': 'webp',  # Default format
        'quality': '10'  # Default quality
    }

    # Parse the arguments string
    options = {arg.split('-')[0]: arg.split('-')[1] for arg in args.split(',') if '-' in arg}

    # Apply default values where necessary
    fill = options.get('fill', defaults['fill'])
    bgcolor = options.get('bgcolor', defaults['bgcolor'])
    format = options.get('format', defaults['format'])
    quality = options.get('quality', defaults['quality'])

    # Construct the rendition string
    rendition_string = f'fill-{fill}|jpegquality-{quality}|format-{format}'

    if bgcolor != 'transparent':
        rendition_string += f'|bgcolor-{bgcolor}'

    return image.get_rendition(rendition_string).url
