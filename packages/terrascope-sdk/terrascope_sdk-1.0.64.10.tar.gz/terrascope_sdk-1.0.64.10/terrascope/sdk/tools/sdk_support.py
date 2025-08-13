from typing import List

import chardet
from terrascope_api.models.common_models_pb2 import Pagination


class SDKSupport:
    @staticmethod
    async def get_all_paginated_objects(request, api_function, timeout) -> List:
        responses = []

        response = await api_function(request, timeout=timeout)
        responses.append(response)

        # Add subsequent result pages if exist
        pagination: Pagination = response.pagination
        while pagination.next_page_token:
            # update request to call the new page
            pagination = Pagination(
                page_token=responses[len(responses) - 1].pagination.next_page_token,
                page_size=responses[len(responses) - 1].pagination.page_size
            )
            request.pagination.MergeFrom(pagination)
            responses.append(await api_function(request, timeout=timeout))
            # set the next page token now that we have the new page
            pagination = Pagination(next_page_token=responses[len(responses) - 1].pagination.next_page_token)

        return responses

    @staticmethod
    def determine_encoding(filename):
        with open(filename, 'rb') as f:
            file_bytes = f.read()
            detection = chardet.detect(file_bytes)
            encoding = detection["encoding"]
            confidence = detection["confidence"]

        return encoding, confidence
