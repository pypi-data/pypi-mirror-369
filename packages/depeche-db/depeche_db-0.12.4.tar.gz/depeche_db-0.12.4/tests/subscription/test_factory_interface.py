from depeche_db import MessageHandlerRegister, MessagePartitioner, StoredMessage
from tests._account_example import (
    AccountEvent,
)


class MyPartitioner(MessagePartitioner[AccountEvent]):
    def get_partition(self, event: StoredMessage[AccountEvent]) -> int:
        return int(str(event.message.account_id)[-1])


def test_factory(store_factory, identifier):
    handlers = MessageHandlerRegister[AccountEvent]()
    store = store_factory()
    stream = store.aggregated_stream(
        name=identifier(),
        partitioner=MyPartitioner(),
        stream_wildcards=["%"],
    )
    subscription = stream.subscription(
        name=identifier(),
        handlers=handlers,
        batch_size=1,
    )

    assert subscription.runner._handler._register is handlers
    assert subscription.runner._batch_size == 1
