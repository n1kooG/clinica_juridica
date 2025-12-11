from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un item de un diccionario por su key.
    Uso: {{ diccionario|get_item:clave }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)