import os

from .http_err import get_body_and_handle_err
from .raw_api.api.detection_rule_yaml import \
    run_detection_rule_yaml_tests, validate_detection_rule_yaml
from .raw_api.client import AuthenticatedClient
from .raw_api.models import RunDetectionRuleYamlTestsResponseData, \
    ValidateDetectionRuleYamlResponseData

DETECTION_RULE_SCHEMA_HEADER = "# schema: https://scanner.dev/schema/scanner-detection-rule.v1.json"


def has_yaml_extension(file_path: str) -> bool:
    return file_path.endswith(".yml") or file_path.endswith(".yaml")


def contains_schema(contents: str) -> bool:
    return DETECTION_RULE_SCHEMA_HEADER in contents


def validate_and_read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise Exception(f"File {file_path} not found.")

    if not has_yaml_extension(file_path):
        raise Exception(f"File {file_path} does not have a .yml or .yaml extension.")

    f = open(file_path, "r")
    contents = f.read()

    if not contains_schema(contents):
        raise Exception(f"File {file_path} does not contain the correct schema header.")

    return contents


class DetectionRuleYaml():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    def run_tests(
        self,
        file_path: str,
    ) -> RunDetectionRuleYamlTestsResponseData:
        data = validate_and_read_file(file_path)
        resp = run_detection_rule_yaml_tests.sync_detailed(
            client=self._client,
            body=data)

        return get_body_and_handle_err(resp)


    def validate(
        self,
        file_path: str,
    ) -> ValidateDetectionRuleYamlResponseData:
        data = validate_and_read_file(file_path)
        resp = validate_detection_rule_yaml.sync_detailed(
            client=self._client,
            body=data)

        return get_body_and_handle_err(resp)


class AsyncDetectionRuleYaml():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    async def run_tests(
        self,
        file_path: str,
    ) -> RunDetectionRuleYamlTestsResponseData:
        data = validate_and_read_file(file_path)
        resp = await run_detection_rule_yaml_tests.asyncio_detailed(
            client=self._client,
            body=data)

        return get_body_and_handle_err(resp)


    async def validate(
        self,
        file_path: str,
    ) -> ValidateDetectionRuleYamlResponseData:
        data = validate_and_read_file(file_path)
        resp = await validate_detection_rule_yaml.asyncio_detailed(
            client=self._client,
            body=data)

        return get_body_and_handle_err(resp)
