from typing import List

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.user_pb2 import (
    LoginRequest, UserCreateRequest, User, UserGetRequest, UserListRequest, UserPublicKeyRequest, UserPublicKeyResponse
)


class APIUser:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def create(self, name: str, email: str, user_collection_id: str) -> User:
        """
        Description

        Create a new user in the system, assigned to the specified department. This functionality is only available
        for an admin user. This automatically creates an aoi_collection associated to this user.

        :param name:
        :param user_collection_id:
        :param email:
        :return:
        """
        request = UserCreateRequest(
            name=name,
            email=email,
            user_collection_id=user_collection_id
        )
        response = await self.__client.api.user.create(request)
        return response.user

    async def update(self, user_id: str, name: str = None, email: str = None):
        """
        Description

        Update Mutable fields for the given user.

        :param user_id:
        :param name:
        :param email:
        :return:
        """
        pass

    async def get(self, ids: List) -> List[User]:
        """
        Description
        Returns the details of the specified user. If no user is given, returns details for the requesting user.
        The specified user must belong to the same department as the requesting user, otherwise an error is thrown.

        :param ids:
        :return: List[User]
        """
        request = UserGetRequest(
            ids=ids
        )
        response = await self.__client.api.user.get(request)
        return response.users

    async def list(self, email: str) -> List[User]:
        """
        Description
        Returns the details of the specified user. If no user is given, returns details for the requesting user.
        The specified user must belong to the same department as the requesting user, otherwise an error is thrown.

        :param email:
        :return: List[User]
        """
        request = UserListRequest(
            email=email
        )
        response = await self.__client.api.user.list(request)
        return response.users

    async def delete(self, user_ids: List):
        """
        Description

        Delete a user from the system, ensuring that they are no longer able to log into the system and they are
        not able to consume any credits. This functionality is only available for an admin user.
        This is a soft delete, so references to the user do not break.

        :param user_ids:
        :return:
        """
        pass

    async def login(self, email: str, password: str):
        """
        Description

        Login using user's email and password. The endpoint returns a JWT access token that is needed to use the API.
        Note: This endpoint does NOT require token authentication.

        :param email:
        :param password:
        :return:
        """
        request = LoginRequest(
            email=email,
            password=password
        )
        response = await self.__client.api.user.login(request, timeout=self.__timeout)
        return response

    async def public_key_request(self):
        request = UserPublicKeyRequest()
        response = await self.__client.api.user.get_public_key(request, timeout=self.__timeout)
        return response.key_pem

    async def send_temp_password(self, email: str):
        """
        Description

        Generates a temporary password that is sent to the user's email address, which can be used to regain access
        to the system. It is strongly encouraged to change your password after getting a temporary password.
        This endpoint does NOT require token authentication.

        :param email:
        :return:
        """

        pass

    async def change_password(self, user_id: str, old_password: str, new_password: str):
        """
        Description

        Changes the user's password. Although an authenticated endpoint, still requires the user to
        enter their old password in order to change it.

        :param user_id:
        :param old_password:
        :param new_password:
        :return:
        """

        pass
