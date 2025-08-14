# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from pydantic import BaseModel
from typing import List


class ActorKeyPair(BaseModel):
    """Represents a key pair for the actor"""

    name: str
    """Name of the key used in the key id in the form `key_id = f"{actor_id}#{name}"`"""
    public: str
    """The PEM encoded public key"""
    private: str
    """The PEM encoded private key"""


class ActorData(BaseModel):
    """Represents an Actor"""

    actor_name: str
    """The name of the actor used in the actor_id"""
    key_pairs: List[ActorKeyPair] = []
    """List of keys"""
    user_part: str | None = None
    """User as part of the acct-uri for webfinger, None means webfinger lookup is not possible"""

    summary: str = ""
    """Summary part of actor profile"""

    requires_signed_get_for_actor: bool = False
    """If true, validates the signature on `GET /actor`"""
    requires_signed_post_for_inbox: bool = False
    """If true, validates the signature on `POST /inbox`"""
