import botocore.exceptions

"""
    Common utility method to return status code and messages from 'botocore.exceptions.ClientError'
    from AWS services
 """


class EmrErrorHandler:
    @staticmethod
    def get_boto_error(boto_error: botocore.exceptions.ClientError):
        return {
            "http_code": boto_error.response["ResponseMetadata"]["HTTPStatusCode"],
            "message": {
                "code": boto_error.response["Error"]["Code"],
                "errorMessage": boto_error.response["Error"]["Message"],
            },
        }
