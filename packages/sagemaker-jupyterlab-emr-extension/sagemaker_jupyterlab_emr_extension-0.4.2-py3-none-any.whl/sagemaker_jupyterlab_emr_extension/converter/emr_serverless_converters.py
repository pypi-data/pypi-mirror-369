def convert_serverless_application_summary(application={}):
    converted_application = {
        "id": application.get("id"),
        "arn": application.get("arn"),
        "name": application.get("name"),
        "status": application.get("state"),
        "createdAt": str(application.get("createdAt")),
    }

    return converted_application


def convert_list_serverless_applications_response(list_applications_response: {}):
    applications_list = []
    applications = list_applications_response.get("applications", [])
    next_token = list_applications_response.get("nextToken")
    if not applications:
        return applications_list
    else:
        for application in applications:
            applications_list.append(
                convert_serverless_application_summary(application)
            )
    return {"applications": applications_list, "nextToken": next_token}


def convert_get_serverless_application_response(get_application_response: {}):
    application = get_application_response.get("application")

    if not application:
        return {"errorMessage": "Application is undefined"}
    else:
        return {
            "application": {
                "id": application.get("applicationId"),
                "arn": application.get("arn"),
                "name": application.get("name"),
                "releaseLabel": application.get("releaseLabel"),
                "architecture": application.get("architecture"),
                "livyEndpointEnabled": str(
                    application.get("interactiveConfiguration", {}).get(
                        "livyEndpointEnabled"
                    )
                ),
                "maximumCapacityCpu": application.get("maximumCapacity", {}).get("cpu"),
                "maximumCapacityMemory": application.get("maximumCapacity", {}).get(
                    "memory"
                ),
                "maximumCapacityDisk": application.get("maximumCapacity", {}).get(
                    "disk"
                ),
                "status": application.get("state"),
                "tags": application.get("tags", {}),
                "createdAt": str(application.get("createdAt")),
            }
        }
