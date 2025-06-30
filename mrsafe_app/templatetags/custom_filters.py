from django import template

register = template.Library()

# FILTERS
@register.filter(name='get_item')
def get_item(dictionary, key):
    """Fetches the value from the dictionary using the key."""
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(field, css_class):
    """Adds a CSS class to a form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='multiply')
def multiply(value, factor):
    """Multiplies the given value by the specified factor."""
    try:
        return int(value) * int(factor)
    except (ValueError, TypeError):
        return 0

# TAGS
@register.simple_tag
def get_question_field(form, index):
    return form[f'question_{index}']

@register.simple_tag
def get_option_field(form, index, option):
    return form[f'option_{index}_{option}']

@register.simple_tag
def get_correct_answer_field(form, index):
    return form[f'correct_answer_{index}']

@register.simple_tag
def get_difficulty_field(form, index):
    return form[f'difficulty_{index}']



@register.filter
def in_list(value, list_str):
    return value in list_str.split(',')


@register.filter
def filter_by_tool_type(tools, tool_type):
    return [tool for tool in tools if tool.tool_type == tool_type]

# quiz_app/templatetags/custom_filters.py


@register.filter
def split_paragraphs(value):
    """Split text into paragraphs based on double line breaks."""
    if not value:
        return []
    return [p.strip() for p in value.split('\n\n') if p.strip()]


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''



@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except:
        return ''


@register.filter
def strip(value):
    try:
        return value.strip()
    except AttributeError:
        return value



@register.filter
def abs(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    

@register.filter
def map_attr(iterable, attr_name):
    return [getattr(obj, attr_name, None) for obj in iterable]


@register.filter
def to_list(value):
    return list(value)