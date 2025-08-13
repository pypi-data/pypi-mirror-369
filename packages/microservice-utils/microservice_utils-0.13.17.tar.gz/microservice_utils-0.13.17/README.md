# microservice-utils

Utilities and adapters for speeding up microservice development.

## Optional Dependencies (Extras)

The package offers optional functionality through extras. Extras can be installed with the package using the following syntax:

```bash
pip install microservice-utils[gcp_pubsub]
```

**Available extras:**

- **events**: Support for event-driven architectures using pydantic for data validation and parsing.
- **gcp_cloud_run**: Support for Google Cloud Run with the google-cloud-run client library.
- **gcp_cloud_tasks**: Support for Google Cloud Tasks with the google-cloud-tasks client library.
- **gcp_pubsub**: Support for Google Cloud Pub/Sub using the google-cloud-pubsub client library and tenacity for retries.
- **gcp_storage**: Use GCP Cloud Storage with the async gcloud-aio-storage library.
- **novu**: Support for the open-source [novu](https://novu.co) notification center.
- **openai**: Support for completions with the OpenAI API.
- **pinecone**: Support for semantic search with Pinecone.

To install multiple extras, separate them with commas:

```bash
pip install microservice-utils[events,gcp_cloud_run,gcp_cloud_tasks,gcp_pubsub,openai,pinecone]
```

## GCP Pub/Sub
You can subscribe to multiple subscriptions by subsequently calling `subscribe()`. `wait_for_shutdown` will block IO
for all the subscriptions and wait for the app to be signaled to shut down.

```python
from microservice_utils.google_cloud.adapters.pubsub import Subscriber

subscriber = Subscriber("your-gcp-project-id", prepend_value="staging")

with subscriber:
    subscriber.subscribe(
        "accounts__users", sample_handler
    )

    try:
        subscriber.wait_for_shutdown()
    except KeyboardInterrupt:
        # Gracefully shut down in response to Ctrl+C (or other events)
        subscriber.shutdown()
```

## Releasing a new version
- Update the package version using semver rules (`microservice-utils/__init__.py`)
- Commit and push change
- Create a new tag with the version (e.g. `git tag -a vx.x.x -m ''`)
- `git push --tags` to push the new tag and start the release workflow

## Todos

- [x] Events
- [x] GCP Pub/Sub
- [x] GCP Cloud Tasks
- [ ] JWT validation utils
- [x] Logging
