#  Quapp Platform Project
#  response_utils.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from .http_utils import CUSTOM_HEADER_VALUE
from ..component.backend.job_fetcher import JobFetcher
from ..data.promise.post_processing_promise import PostProcessingPromise
from ..data.response.job_response import JobResponse
from ..enum.status.job_status import JobStatus
from ..enum.status.status_code import StatusCode

AUTHENTICATION = 'authentication'
BACKEND_AUTHENTICATION = 'backend_authentication'
PROJECT_HEADER = 'project_header'
PROVIDER_JOB_ID = 'provider_job_id'
WORKSPACE_HEADER = 'workspace_header'


def generate_response(job_response: JobResponse) -> dict:
    """
    Generates a standardized response dictionary based on the given job response.

    This function processes the provided JobResponse instance and constructs a
    response dictionary containing relevant job details such as status code,
    execution time, job results, and additional attributes if they exist. It ensures
    that all necessary information is included in the response for further
    processing or communication with other systems.

    Parameters:
        job_response (JobResponse): An instance of the JobResponse class containing
        detailed job information.

    Returns:
        dict: A dictionary containing the processed job response with keys such as
        'statusCode', 'body', 'userIdentity', 'userToken', 'projectId', and
        'workspaceId'.

    Raises:
        This function does not explicitly raise exceptions.
    """
    if job_response:
        status_code = job_response.status_code.value
        body = {'providerJobId': job_response.provider_job_id,
                'jobStatus'    : job_response.job_status,
                'jobResult'    : job_response.job_result,
                'contentType'  : job_response.content_type.value,
                'histogram'    : job_response.job_histogram,
                'executionTime': job_response.execution_time}

        # Add 'shots' only if it exists in the job_response
        if hasattr(job_response, 'shots'):
            body['shots'] = job_response.shots

    else:
        status_code = job_response.status_code.value
        body = 'Error in function code. Please contact the developer.'

    return {'statusCode'  : status_code,
            'body'        : body,
            'userIdentity': job_response.user_identity,
            'userToken'   : job_response.user_token,
            'projectId'   : getattr(
                    job_response.project_header, CUSTOM_HEADER_VALUE, None),
            'workspaceId' : getattr(
                    job_response.workspace_header, CUSTOM_HEADER_VALUE, None)}


def build_done_job_response(fetcher: JobFetcher = None,
                            post_promise: PostProcessingPromise = None) -> JobResponse | None:
    """
    Builds a JobResponse object for a completed job.

    This function assembles a JobResponse object which signifies the completion
    of a job. It extracts relevant information such as the provider job ID,
    authentication details, project header, and workspace header, and sets the
    status code to indicate the job is done. If both input parameters are missing,
    the function returns None.

    Parameters:
    fetcher (JobFetcher, optional): An optional job fetcher instance used to
        extract the provider job ID and other details.
    post_promise (PostProcessingPromise, optional): An optional post-processing
        promise instance to assist in extracting relevant details.

    Returns:
    JobResponse | None: A JobResponse object with the completed job information,
        or None if no inputs were provided.
    """
    return JobResponse(
            provider_job_id=__extract_value(PROVIDER_JOB_ID, fetcher,
                                            post_promise),
            authentication=__extract_authentication(fetcher, post_promise),
            project_header=__extract_value(PROJECT_HEADER, fetcher,
                                           post_promise),
            workspace_header=__extract_value(WORKSPACE_HEADER, fetcher,
                                             post_promise),
            status_code=StatusCode.DONE)


def build_error_job_response(exception: Exception,
                             job_response: JobResponse = None,
                             fetcher: JobFetcher = None,
                             post_promise: PostProcessingPromise = None,
                             message: str = None) -> JobResponse:
    """
    Builds and returns a JobResponse object populated with error-related information.

    This function constructs a JobResponse object that provides comprehensive details
    about an error occurrence. It extracts specific headers and identifiers from
    the given fetcher or post-promise if provided, and includes information
    about the error such as the exception and a corresponding message. The status
    and result of the job indicate an error state.

    Parameters:
    exception: Exception
        The exception instance representing the error that occurred.

    job_response: JobResponse, optional
        A JobResponse object to populate with error details. If not provided,
        a new JobResponse object will be created.

    fetcher: JobFetcher, optional
        An optional fetcher from which relevant headers and identifiers can
        be extracted.

    post_promise: PostProcessingPromise, optional
        An optional post-processing promise from which relevant headers and
        identifiers can be extracted.

    message: str, optional
        A custom error message to be included in the job response. If not
        specified, a default message "Unknown error occurred." will be used.

    Returns:
    JobResponse
        A JobResponse object populated with error-related details such as
        status, exception, and error message.
    """
    if job_response is None:
        job_response = JobResponse()
    job_response.provider_job_id = __extract_value(PROVIDER_JOB_ID, fetcher,
                                                   post_promise)
    job_response.authentication = __extract_authentication(fetcher,
                                                           post_promise)
    job_response.project_header = __extract_value(PROJECT_HEADER, fetcher,
                                                  post_promise)
    job_response.tenant_header = __extract_value(WORKSPACE_HEADER, fetcher,
                                                 post_promise)
    job_response.status_code = StatusCode.ERROR
    job_response.job_status = JobStatus.ERROR.value
    job_response.job_result = {'message'  : message or 'Unknown error occurred.',
                               'exception': str(exception)}
    return job_response


def __extract_authentication(fetcher: JobFetcher,
                             post_promise: PostProcessingPromise):
    """
    Extract authentication information from the provided fetcher or post promise.

    This function retrieves authentication data by first attempting to extract it from
    the JobFetcher instance. If it's not available on the JobFetcher, it then falls back
    to extracting it from the PostProcessingPromise instance. If neither source contains
    authentication data, a default value of None is returned.

    Parameters:
        fetcher (JobFetcher): The JobFetcher instance to retrieve authentication data from.
        post_promise (PostProcessingPromise): The PostProcessingPromise instance to retrieve
            authentication data from if not available on the fetcher.

    Returns:
        Any: The extracted authentication data, or None if no authentication data is found.
    """
    return getattr(fetcher, BACKEND_AUTHENTICATION,
                   getattr(post_promise, AUTHENTICATION, None))


def __extract_value(property_name: str, fetcher: JobFetcher,
                    post_promise: PostProcessingPromise):
    """
    Extracts a specified property value from a fetcher object or a fallback
    post-processing promise object.

    Parameters:
    property_name: str
        The name of the property to extract.
    fetcher: JobFetcher
        The primary object from which the property value is retrieved.
    post_promise: PostProcessingPromise
        The fallback object from which the property value is retrieved if
        unavailable in the fetcher.

    Returns:
    Any
        The value of the specified property retrieved from the fetcher or the
        fallback post-promise object.

    """
    return getattr(fetcher, property_name,
                   getattr(post_promise, property_name, None))
