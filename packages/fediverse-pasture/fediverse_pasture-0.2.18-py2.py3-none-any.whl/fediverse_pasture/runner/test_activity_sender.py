# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock

from fediverse_pasture.data_provider import DataProvider, bovine_actor_for_actor_data

from . import ActivitySender


@pytest.fixture
def activity_sender():
    dp = DataProvider.generate(with_possible_actors=False)

    bovine_actor, actor_object = bovine_actor_for_actor_data(
        "http://localhost/actor", dp.one_actor
    )

    yield ActivitySender.for_actor(bovine_actor, actor_object)


def test_activity_sender(activity_sender):
    activity_sender.init_create_note(lambda x: {**x, "content": "text"})

    assert isinstance(activity_sender.published, datetime)
    assert isinstance(activity_sender.note, dict)

    obj = activity_sender.note

    assert obj.get("content") == "text"

    text = json.dumps(activity_sender.note)

    assert len(text) > 20


async def test_activity_sender_modifying_to(activity_sender):
    activity_sender.init_create_note(lambda x: {**x})
    assert activity_sender.note.get("to") == ["as:Public"]

    activity_sender.init_create_note(lambda x: {**x, "to": ["Public"]})
    assert activity_sender.note.get("to") == ["Public"]

    activity_sender.bovine_actor.post = AsyncMock()
    activity_sender.bovine_actor.get = AsyncMock(
        return_value={"inbox": "https://remote.example/inbox"}
    )

    await activity_sender.send("https://remote.example")

    activity_sender.bovine_actor.get.assert_awaited_once()
    assert activity_sender.bovine_actor.get.await_args == [("https://remote.example",)]
    activity_sender.bovine_actor.post.assert_awaited_once()

    data = activity_sender.bovine_actor.post.await_args[0][1]

    assert set(data["to"]) == {"https://remote.example", "Public"}
