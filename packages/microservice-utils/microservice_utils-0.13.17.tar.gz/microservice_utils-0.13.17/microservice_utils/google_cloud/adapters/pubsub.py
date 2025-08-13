import logging
import os
import tenacity
import typing

from google.cloud import pubsub

if typing.TYPE_CHECKING:
    from google.cloud.pubsub_v1.subscriber.message import Message
    from google.cloud.pubsub_v1.subscriber import futures

logging.getLogger("google").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class PublishError(Exception):
    pass


class Publisher:
    _client: pubsub.PublisherClient = None

    def __init__(self, gcp_project_id: str, *args, prepend_value: str = None, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._gcp_project_id = gcp_project_id
        self._prepend_value = prepend_value

    def format_topic_name(self, friendly_topic_name: str) -> str:
        return (
            f"projects/{self._gcp_project_id}/topics/"
            f"{self._prepend_value + '.' if self._prepend_value else ''}"
            f"{friendly_topic_name}"
        )

    def _get_client(self):
        if not self._client:
            self._client = pubsub.PublisherClient(
                *self._args,
                batch_settings=pubsub.types.BatchSettings(max_messages=250),
                **self._kwargs,
            )

        return self._client

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    )
    def publish(self, topic_name: str, data: bytes, **attributes: typing.Any) -> str:
        """Publish to a topic. Topic names will automatically have the prepended value
        added if it was provided at instantiation"""

        try:
            future = self._get_client().publish(
                self.format_topic_name(topic_name), data, **attributes
            )
            message_id = future.result()

            logger.info("Published message to Pub/Sub. ID: %s", message_id)

            return message_id
        except Exception as e:
            raise PublishError(f"Unable to publish message: {str(e)!r}")


class Subscriber:
    _clients: dict[str, pubsub.SubscriberClient]

    def __init__(self, gcp_project_id: str, *args, prepend_value: str = None, **kwargs):
        self._args = args
        self._clients = {}
        self._kwargs = kwargs
        self._futures: dict[str, futures.StreamingPullFuture] = {}
        self._gcp_project_id = gcp_project_id
        self._prepend_value = prepend_value

    def __enter__(self) -> "Subscriber":
        return self

    def __exit__(self, *args, **kwargs):
        for client in self._clients.values():
            client.close()

    def _instantiate_pubsub_client(self, subscription_name: str):
        self._clients[subscription_name] = pubsub.SubscriberClient(**self._kwargs)

    def get_subscription_name(self, friendly_subscription_name: str) -> str:
        return (
            f"projects/{self._gcp_project_id}/subscriptions/"
            f"{self._prepend_value + '.' if self._prepend_value else ''}"
            f"{friendly_subscription_name}"
        )

    def shutdown(self):
        """Initiate a graceful shutdown by canceling all the subscription futures."""

        for future in self._futures.values():
            future.cancel()
            future.result()

    def subscribe(
        self,
        subscription_name: str,
        handler: typing.Callable[["Message"], None],
        max_messages: int = 50,
        **kwargs,
    ) -> "futures.StreamingPullFuture":
        """Subscribe to a topic. Subscription name can optionally have a value
        prepended (e.g. environment name).
        If you do prepend a value, the name doesn't need to include the prepended
        value. For example, to subscribe to:
        projects/test/subscriptions/staging.accounts.users.billing,
        you need only provide "accounts.users.billing", assuming "staging" is the
        prepended value.
        """

        subscription_name = self.get_subscription_name(subscription_name)
        self._instantiate_pubsub_client(subscription_name)

        # subscribe
        fc = pubsub.types.FlowControl(max_messages=max_messages)

        subscription_future = self._clients[subscription_name].subscribe(
            subscription_name, handler, flow_control=fc
        )

        self._futures[subscription_name] = subscription_future

        return subscription_future

    def wait_for_shutdown(self):
        for future in self._futures.values():
            future.result()


if __name__ == "__main__":
    import sys
    import time

    """Usage for testing
    python pubsub.py [publish|subscribe] [topic_name|subscription_name]
    e.g. GCP_PROJECT_ID=the-sandbox python pubsub.py publish test
    e.g. GCP_PROJECT_ID=the-sandbox python pubsub.py subscribe test.test-subscriber
    """

    if len(sys.argv) != 3:
        raise RuntimeError("Expected 2 input arguments")

    def sample_handler(message: "Message"):
        print(message.data)
        message.ack()

    PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    ENVIRONMENT = os.getenv("PREPEND")

    action = sys.argv[1]
    topic_or_subscription_name = sys.argv[2]

    if action == "publish":
        publisher = Publisher(PROJECT_ID, prepend_value=ENVIRONMENT)

        try:
            message_id = publisher.publish(
                topic_or_subscription_name,
                bytes(f"Hello from pubsub.py at {time.time()}", "utf-8"),
            )
            print(f"Published successfully! Message ID: {message_id!r}")
        except PublishError as e:
            print(f"Publishing failed: {e!r}")
    elif action == "subscribe":
        subscriber = Subscriber(PROJECT_ID, prepend_value=ENVIRONMENT)

        with subscriber:
            subscriber.subscribe(topic_or_subscription_name, sample_handler)

            try:
                subscriber.wait_for_shutdown()
            except KeyboardInterrupt:
                subscriber.shutdown()
    else:
        print(f"Unknown action {action!r}")
