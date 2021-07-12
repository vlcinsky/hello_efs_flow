import os

import prefect
from prefect import Flow, Parameter, task
from prefect.executors import LocalDaskExecutor
from prefect.run_configs import ECSRun

from prefect.storage import S3


@task
def say_hello(name):
    # Load the greeting to use from an environment variable
    greeting = os.environ.get("GREETING")
    logger = prefect.context.get("logger")
    logger.info(f"{greeting}, {name}!")


storage = S3(bucket="prefect-storage-cet")
with Flow("hello-gitlab-flow", storage=storage) as flow:
    people = Parameter("people", default=["Arthur", "Ford", "Marvin"])
    say_hello.map(people)

# Configure the `GREETING` environment variable for this flow
# flow.run_config = LocalRun(env={"GREETING": "Hello"})
flow.run_config = ECSRun(
    env={"GREETING": "Hello"},
    task_role_arn="arn:aws:iam::230477879165:role/ecsTaskExecutionRole",
    execution_role_arn="arn:aws:iam::230477879165:role/ecsTaskExecutionRole",
    task_definition_path="hello_flow.json",
    run_task_kwargs={
        "networkConfiguration": {
            "awsvpcConfiguration": {
                "subnets": [
                    "subnet-0891d16c2bd98276d",
                    "subnet-05caea547b8a1e200",
                    "subnet-0264a2e28dab5f124",
                ],
                "assignPublicIp": "ENABLED",
                "securityGroups": ["sg-0d471249999bc87fc"],
            }
        }
    },
)

# Use a `LocalDaskExecutor` to run this flow
# This will run tasks in a thread pool, allowing for parallel execution
flow.executor = LocalDaskExecutor()

# Register the flow under the "tutorial" project
flow.register(project_name="tutorial", labels=["cet", "prefect"])
