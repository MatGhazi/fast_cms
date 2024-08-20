from os import getenv

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader


MODE = 'async background'.split()[1]


async def send_email(
        background_tasks: BackgroundTasks,
        recipient: str, 
        subject: str, 
        template_name: str, 
        body: dict
):
    conf = ConnectionConfig(
        MAIL_USERNAME=getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=getenv('MAIL_PASSWORD'),
        MAIL_FROM=getenv('MAIL_FROM'),
        MAIL_PORT=getenv('MAIL_PORT'),
        MAIL_SERVER=getenv('MAIL_SERVER'),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
    )
    #
    templates_directory = './app/utils/email/templates'
    env = Environment(loader=FileSystemLoader(templates_directory))
    template = env.get_template(template_name)
    html_content = template.render(**body)
    #
    message = MessageSchema(
        recipients=[recipient],
        subject=subject,
        body=html_content,
        subtype='html'
    )
    #
    fm = FastMail(conf)
    match MODE:
        case 'async': await fm.send_message(message)
        case 'background': background_tasks.add_task(fm.send_message, message)


