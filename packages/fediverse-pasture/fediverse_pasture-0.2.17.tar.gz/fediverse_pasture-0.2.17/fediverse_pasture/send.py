import asyncio
import click

from bovine.clients import lookup_uri_with_webfinger
from bovine.utils import parse_fediverse_handle

from .runner import ActivitySender
from .one_actor import bovine_actor_and_session


async def handle_send_to(
    domain: str,
    uri: str,
):
    async with bovine_actor_and_session(domain) as (bovine_actor, actor, session):
        if uri.startswith("acct:"):
            _, acct_domain = parse_fediverse_handle(uri)

            candidate_uri, _ = await lookup_uri_with_webfinger(
                session, uri, domain=f"http://{acct_domain}"
            )

            if not candidate_uri:
                raise ValueError(f"Could not resolve {uri} to an actor URI")

            uri = candidate_uri

        sender = ActivitySender.for_actor(bovine_actor, actor)
        sender.init_create_note(lambda x: {**x, "content": "text"})

        await sender.send(uri)


@click.command()
@click.option(
    "--domain",
    default="http://pasture-one-actor",
    help="Domain the actor is served one",
)
@click.argument("uri")
def send_to(domain, uri):
    asyncio.run(handle_send_to(domain, uri))


if __name__ == "__main__":
    send_to()
