#  Quapp Platform Project
#  http_utils.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from urllib.parse import urlparse

from ..config.logging_config import logger
from ..data.response.custom_header import CustomHeader
from ..enum.http_header import HttpHeader
from ..enum.media_type import MediaType
from ..enum.token_type import TokenType

DEFAULT_WORKSPACE_HEADER = 'workspaceHeader'
DEFAULT_PROJECT_HEADER = 'projectHeader'
CUSTOM_HEADER_VALUE = 'value'
CUSTOM_HEADER_NAME = 'name'


def create_bearer_header(token, project_header: CustomHeader,
                         workspace_header: CustomHeader):
    """
    Creates an HTTP Bearer authorization header.

    This function takes a token as an input and constructs a dictionary containing the
    Bearer authorization header. The header consists of the token type "Bearer"
    followed by the provided token.

    Parameters:
    token: str
        The token string used for the authorization header.

    Returns:
    dict
        A dictionary containing the constructed Bearer authorization header.
    """
    project_header_name = getattr(project_header, CUSTOM_HEADER_NAME,
                                  DEFAULT_PROJECT_HEADER)
    project_header_value = getattr(project_header, CUSTOM_HEADER_VALUE, None)
    workspace_header_name = getattr(workspace_header, CUSTOM_HEADER_NAME,
                                    DEFAULT_WORKSPACE_HEADER)
    workspace_header_value = getattr(workspace_header, CUSTOM_HEADER_VALUE,
                                     None)

    return {
        HttpHeader.AUTHORIZATION.value: TokenType.BEARER.value + ' ' + token,
        project_header_name           : project_header_value,
        workspace_header_name         : workspace_header_value}


def create_application_json_header(token: str, project_header: CustomHeader,
                                   workspace_header: CustomHeader) -> dict:
    """
    Generates HTTP headers for JSON-based API requests, including authorization
    and optional custom project and workspace headers.

    Args:
        token: Authorization token of type string for the HTTP headers.
        project_header: CustomHeader object representing the project-specific
            custom header details.
        workspace_header: CustomHeader object representing the workspace-specific
            custom header details.

    Returns:
        dict: Dictionary containing HTTP headers with authorization, content type,
        accept headers, and custom project and workspace headers where applicable.
    """
    project_header_name = getattr(project_header, CUSTOM_HEADER_NAME,
                                  DEFAULT_PROJECT_HEADER)
    project_header_value = getattr(project_header, CUSTOM_HEADER_VALUE, None)
    workspace_header_name = getattr(workspace_header, CUSTOM_HEADER_NAME,
                                    DEFAULT_WORKSPACE_HEADER)
    workspace_header_value = getattr(workspace_header, CUSTOM_HEADER_VALUE,
                                     None)
    return {
        HttpHeader.AUTHORIZATION.value: '{0} {1}'.format(TokenType.BEARER.value,
                                                         token),
        HttpHeader.CONTENT_TYPE.value : MediaType.APPLICATION_JSON.value,
        HttpHeader.ACCEPT.value       : MediaType.APPLICATION_JSON.value,
        project_header_name           : project_header_value,
        workspace_header_name         : workspace_header_value}


def get_custom_header(request_data: dict, key: str) -> CustomHeader:
    """
    Retrieve and construct a CustomHeader object from request data.

    This function accesses a specified key in the request_data dictionary
    to extract the necessary information for creating a CustomHeader
    object. It retrieves the 'name' and 'value' properties from the
    nested dictionary corresponding to the provided key.

    Parameters:
    request_data (dict): The dictionary containing header details.
    key (str): The key used to extract the relevant header data.

    Returns:
    CustomHeader: An object that encapsulates the extracted 'name' and
    'value' of the custom header.
    """
    custom_header = request_data.get(key, {})
    return CustomHeader(name=custom_header.get(CUSTOM_HEADER_NAME),
                        value=custom_header.get(CUSTOM_HEADER_VALUE))


def get_job_id_from_url(url: str):
    """
    Extracts the job ID from a given URL. This function securely parses the given URL
    and attempts to retrieve the job ID located in the path, typically after the 'jobs'
    keyword. If the pattern is not found or the URL is invalid, it returns None.

    Args:
        url: The URL string from which the job ID will be extracted.

    Returns:
        str or None: The extracted job ID if present, otherwise returns None.
    """

    path = urlparse(url).path
    segments = [seg for seg in path.split('/') if seg]
    job_id = None

    logger.debug(f'Parsed URL segments: {segments}')

    if 'jobs' in segments:
        idx = segments.index('jobs')
        try:
            job_id = segments[idx + 1]
            logger.debug(f"Found job id after 'jobs': {job_id}")
        except IndexError:
            logger.exception("No job id found after 'jobs'")
    elif 'job' in segments:
        idx = segments.index('job')
        try:
            job_id = segments[idx + 1]
            logger.debug(f"Found job id after 'job': {job_id}")
        except IndexError:
            logger.exception("No job id found after 'job'")
    else:
        logger.exception("Neither 'job' nor 'jobs' found in URL segments.")

    return job_id
