"""Custom actor specification for dramatiq actors."""
from typing import Any, Callable, Dict

from dramatiq.actor import Actor
from dramatiq.brokers.rabbitmq import RabbitmqBroker


class LazyActor(Actor):
    """
    Lazy actor is an override of the base Actor class in dramatiq.

    By default, Actors in dramatiq try to connect to a broker as soon as they are loaded by python.
    This means that if you have not yet done your broker configuration, your actors will be
    trying to connect to a non-existent broker and will not work. This class makes your actors
    not try to connect to a broker until they have been explicitly called with init_broker.
    """

    def __init__(  # type: ignore
        self,
        fn: Callable,
        *args,
        broker: RabbitmqBroker,
        actor_name: str,
        queue_name: str,
        priority: int,
        options: Dict[str, Any],
        **kwargs,
    ) -> None:
        """
        Create an instance of a LazyActor. This typically should not be called directly.

        Have your dramatiq Actors inherit from this class to get the functionality within.

        @dramatiq.actor(actor_class=LazyActor)
        """
        self._fn = fn
        self._actor_name = actor_name
        self._queue_name = queue_name
        self._priority = priority
        self._options = options

    def init_actor(self, broker: RabbitmqBroker) -> None:
        """
        Connect the actor with the broker that is being given to it.

        :param broker: The rabbitmq broker to connect to.
        """
        super().__init__(
            self._fn,
            broker=broker,
            actor_name=self._actor_name,
            queue_name=self._queue_name,
            priority=self._priority,
            options=self._options,
        )
