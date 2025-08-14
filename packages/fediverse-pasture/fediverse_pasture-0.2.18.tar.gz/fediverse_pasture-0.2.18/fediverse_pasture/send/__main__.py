import asyncio
import click

from . import handle_send_to
from .modifier import ModifierBuilder


@click.command()
@click.option(
    "--domain",
    default="http://pasture-one-actor",
    help="Domain the actor is served one",
)
@click.option("--text", help="Content of the message to be send")
@click.argument("uri")
def send_to(domain, text, uri):
    modifier = ModifierBuilder(text=text).build()
    asyncio.run(handle_send_to(modifier, domain, uri))


if __name__ == "__main__":
    send_to()
