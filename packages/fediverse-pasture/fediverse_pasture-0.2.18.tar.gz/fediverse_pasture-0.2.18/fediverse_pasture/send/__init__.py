from bovine.clients import lookup_uri_with_webfinger
from bovine.utils import parse_fediverse_handle

from fediverse_pasture.runner import ActivitySender
from fediverse_pasture.one_actor import bovine_actor_and_session
from fediverse_pasture.types import MessageModifier


async def handle_send_to(
    modifier: MessageModifier,
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
        sender.init_create_note(modifier)

        await sender.send(uri)
