def render_template(template: str, **kwargs) -> str:
    return template.format(**kwargs)
