# Run prefect on AWS ECS with attached AWS EFS volume

This repository test possibility to run a prefect task using ECSRun with the task having access to Amazon EFS volume.

## Motivation

Processing larger datasets may require temporary storage with unpredictable size.

Using local storage of a virtual machine (EC2), using ECS docker volume or using AWS Lambda function storage have limits, which are not easy to overcome.

Using Amazon Elastic File System seems to be perfect fit for this type of tasks for following reasons:

- practically unlimited size
- option to automatically remove files after pre-defined time (to limit costs)
- persistency
- accessible from different virtual machines, Amazon Lambda functions or containers at once
- it behaves as standard volume so it operations like sorting or compressing using multiple cores and multiple temporary files is possible (opposite to data being stored on AWS S3)

## Proposed architecture

### Prefect Cloud

Serves as flow coordinator.

### ECS cluster created by Amazon ECS (with prefect agent)

An ECS cluster runs prefect agent which registers with Prefect Cloud to get things to do.

### Prefect agent

Runs on ECS cluster and listens to the Prefect Cloud to get flows to run.

### Storage AWS S3

For storing flow definitions, AWS S3 is used (in this example we use bucket "prefect-storage-cet")

### Amazon EFS as volume to mount

There is created EFS volume which is intended to be mounted to containers, which will need them to use.

The EFS is created in the same region (eu-west-1) as the ECS.

## Challenges

The ECS job running actual flow must get access to the EFS volume. The challenge is, that this job is being created by prefect agent so all the configuration related to getting access to EFS must be probably fully configured by the ECSRun.

# Hello Flow

Hello flow is just very simple flow to test EFS can be accessed. (actual production job is going to run tasks which will do sorting of large files and compression using pbzip2 or other tools being able to use multiple cores and needing enough storage for input, temporary and resulting files)

Current Flow version does not use EFS at all, it only logs something using prefect logger. Intended use of EFS is whatever proves the tasks have access to EFS, e.g. creating random file in predefined folder and then printing to logs all files found in that directory.

## Installation

Using python 3.7.7 and poetry 1.1.6 or higher:

```shell
$ poetry install
```

### Configuration

Make sure, the bucket used as storage is created and can be access by jobs run within ECS.

The task is defined by file `hello_flow.json` and provided to the flow via `task_definition_path` parameter of `ECSRun`.

`ECSRun` parameter `run_task_kwargs` is used to provide values needed to created the container with proper access to EFS.

### Usage

To activate the environment:

```shell
$ poetry shell
(.venv) $
```

To register the flow:

```shell
(.venv) $ python hellow_flow.py
```

To run the job, go to Prefect Cloud find the project and run the latest registered version of the task.

### Issues

When the flow does not use `run_task_kwargs` parameter, all works fine.

When it is used, the job fails to start, agent attempts to start it but without any entry in prefect logs and it looks like the flow gets somehow stuck before being actually started. After few attempts (it takes around 45 minutes) the Prefect Cloud stops trying any more and reports flow failure.

# References

[pcloud]: cloud.prefect.io/
[efs]: https://aws.amazon.com/efs/
[ecs]: https://aws.amazon.com/ecs/
[s3]: https://aws.amazon.com/s3/
[pbzip2]: http://compression.ca/pbzip2/
