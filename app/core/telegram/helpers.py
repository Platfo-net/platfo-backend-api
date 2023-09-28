from jinja2 import Environment, FileSystemLoader


def load_message(lang, template_name, **kwargs) -> str:
    file_path = f'app/templates/telegram/{lang}'
    file_loader = FileSystemLoader(file_path)
    env = Environment(loader=file_loader)
    template = env.get_template(f"{template_name}.txt")
    return template.render(**kwargs)
