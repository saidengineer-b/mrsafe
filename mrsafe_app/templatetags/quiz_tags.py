# quiz_app/templatetags/quiz_tags.py
from django import template

register = template.Library()

@register.filter
def get_correct_choice_label(choices):
    labels = ['A', 'B', 'C', 'D']
    for index, choice in enumerate(choices):
        if choice.is_correct:
            return labels[index]
    return ''

@register.filter
def pair_with_labels(choices):
    labels = ['A', 'B', 'C', 'D']
    return zip(choices, labels)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
