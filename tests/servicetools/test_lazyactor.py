from unittest.mock import MagicMock

import dramatiq
import servicetools.lazyactor as under_test


@dramatiq.actor(actor_class=under_test.LazyActor)
def test_func(fake: str) -> None:
    pass


class TestLazyActors:
    def test_broker_is_not_set(self):
        assert not getattr(test_func, "broker", None)

    def test_broker_is_set_when_init(self):
        mock_broker = MagicMock()
        test_func.init_actor(mock_broker)
        assert test_func.broker
