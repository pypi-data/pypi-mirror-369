# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

# This script is used to run Pycloud tests on AWS CodeBuild.
# The Codebuild job PSRCloudTests_pycloud was originally created for PSRCloud
# automation tests and is reused here to run Pycloud tests remotely

import argparse
import time

import boto3

PROJECT_NAME = "PSRCloudTests_pycloud"
LOG_GROUP_NAME = f"/aws/codebuild/{PROJECT_NAME}"
REGION = "us-east-1"

argparser = argparse.ArgumentParser()
argparser.add_argument("--branch", default="main")
argparser.add_argument("--cluster", default="Staging")
argparser.add_argument("tests", default="", nargs="*")
args = argparser.parse_args()

tests_names = " ".join(args.tests)

codebuild_client = boto3.client("codebuild", region_name=REGION)
logs_client = boto3.client("logs", region_name=REGION)


def run_codebuild_build(project_name: str) -> str:
    response = codebuild_client.start_build(
        projectName=project_name,
        environmentVariablesOverride=[
            {"name": "GIT_BRANCH", "value": args.branch, "type": "PLAINTEXT"},
            {
                "name": "PSRCLOUD_TEST_CLUSTER",
                "value": args.cluster,
                "type": "PLAINTEXT",
            },
            {"name": "TESTS_NAMES", "value": tests_names, "type": "PLAINTEXT"},
        ],
    )
    build_id = response["build"]["id"]
    print(f"Build started successfully! Build ID: {build_id}")
    print("")
    return build_id


def get_build_status(build_id):
    build_ids = [build_id]
    response = codebuild_client.batch_get_builds(ids=build_ids)
    return response["builds"][0]["buildStatus"]


def stream_logs(log_group_name, log_stream_name, next_token=None):
    log_params = {
        "logGroupName": log_group_name,
        "logStreamName": log_stream_name,
        "startFromHead": True,
    }
    if next_token:
        log_params["nextToken"] = next_token
    try:
        response = logs_client.get_log_events(**log_params)
        for event in response["events"]:
            print(event["message"][:-1])
    except:
        return None
    return response.get("nextForwardToken")


def main():
    build_id = run_codebuild_build(PROJECT_NAME)
    next_forward_token = None

    while True:
        status = get_build_status(build_id)
        if status == "FAILED":
            print("Build failed")
            exit(1)
        elif status == "SUCCEEDED":
            print("Build succeeded")
            exit(0)
        elif status == "IN_PROGRESS":
            log_stream_name = build_id.split(":")[1]
            next_forward_token = stream_logs(
                LOG_GROUP_NAME, log_stream_name, next_forward_token
            )
        time.sleep(1)


if __name__ == "__main__":
    main()
