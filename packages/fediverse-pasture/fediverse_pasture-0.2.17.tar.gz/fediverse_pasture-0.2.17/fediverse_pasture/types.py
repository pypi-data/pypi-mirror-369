# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Class to track messages

    :param steps: a log of strings"""

    steps: List[str] = field(default_factory=list)

    def add(self, msg):
        """Adds a message to steps and logs it to info"""
        logger.info(msg)
        self.steps.append(msg)

    def error(self, msg):
        """Logs an error and returns a message object"""
        logger.error(msg)
        return {"x error": msg, **self.response}

    @property
    def response(self):
        """Returns a dictionary with a single key "steps" containing the steps"""
        return {"steps": self.steps}


@dataclass
class ApplicationAdapterForLastActivity:
    """Basic type that is used to describe how to interact with
    an external application. actor_uri represents the actor
    a message will be sent to. fetch_activity is used to
    fetch this activity.

    :param actor_uri: The actor uri
    :param application_name: The name the application will be displayed as
    :param fetch_activity: coroutine that retrieves the activity with a specified
        published date.
    """

    actor_uri: str
    application_name: str
    fetch_activity: Callable[[datetime], Awaitable[dict | None]]


@dataclass
class ApplicationAdapterForActor:
    """Basic type that is used to describe how to interact with
    an external application. actor_uri represents the actor
    a message will be sent to.


    :param actor_uri: The actor uri
    :param application_name: The name the application will be displayed as
    """

    actor_uri: str
    application_name: str
