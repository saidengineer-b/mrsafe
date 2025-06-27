# mrsafe_app/templatetags/markdown_filters.py
import markdown
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def markdown_to_html(value):
    extensions = ['fenced_code', 'tables']
    return mark_safe(markdown.markdown(value, extensions=extensions))

@register.filter
def get_section_title(value):
    """Extract the first line as section title"""
    return value.split('\n')[0].strip('#').strip()

@register.filter
def get_section_content(value):
    """Get all content after the first line"""
    lines = value.split('\n')
    return '\n'.join(lines[1:]).strip()

@register.filter
def process_hazards(value):
    """Convert hazard items to structured HTML"""
    items = re.split(r'\n\s*-\s*', value)
    if not items or len(items) < 2:
        return value
        
    html = '<div class="hazard-items">'
    for item in items[1:]:
        if not item.strip():
            continue
            
        severity_class = 'hazard-medium'
        if 'Severity: Critical' in item:
            severity_class = 'hazard-critical'
        elif 'Severity: High' in item:
            severity_class = 'hazard-high'
        elif 'Severity: Low' in item:
            severity_class = 'hazard-low'
            
        html += f'<div class="hazard-item {severity_class}">'
        html += markdown.markdown(f"- {item}")
        html += '</div>'
    
    html += '</div>'
    return mark_safe(html)