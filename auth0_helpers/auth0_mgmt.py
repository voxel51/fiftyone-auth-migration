"""
| Copyright 2017-2024 Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import asyncio
import datetime
from typing import Any, AsyncIterator, Literal

import aiohttp
import auth0.authentication
import auth0.exceptions
import auth0.management
import backoff
from config import Config
from fiftyone_helpers import Group, Organization, User, UserRole


class Auth0BackoffWrapper:
    """Wraps all instance methods in backoff when rate limiting error is hit"""

    def __init__(self, instance):
        self.__instance = instance

    def __getattr__(self, name):
        if not hasattr(self.__instance, name):
            raise AttributeError(f"'{type(self.__instance)}' object has no attribute 'name'")

        attr = getattr(self.__instance, name)
        return (
            backoff.on_exception(
                backoff.expo,
                (auth0.exceptions.RateLimitError),
                max_tries=Config.MAX_HTTP_RETRIES,
                logger=None,
            )(attr)
            if callable(attr)
            else attr
        )


class Auth0ManagementAPIFactory:
    """Factory for creating Auth0 Management API clients"""

    def __init__(
        self,
        client_domain: str,
        client_id: str,
        client_secret: str,
        audience: str,
        /,
        client_expiry: int | datetime.timedelta | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        self.__client_domain = client_domain
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__audience = audience

        self.__mgmt_client: auth0.management.Auth0 = None
        self.__mgmt_client_lock = asyncio.Lock()
        self.__mgmt_client_expires_at: datetime.datetime = None

        self.__client_session = session

        if client_expiry is not None:
            if isinstance(client_expiry, int):  # If int it's in seconds
                client_expiry = datetime.timedelta(seconds=client_expiry)
            elif not isinstance(client_expiry, datetime.timedelta):
                raise TypeError(
                    "'client_expiry' must be an instance of " f"`{datetime.timedelta.__name__}`"
                )

        self.__mgmt_client_expiry = client_expiry

    @property
    def audience(self) -> str:
        return self.__audience

    @property
    def domain(self) -> str:
        return self.__client_domain

    async def get_client(self) -> auth0.management.Auth0:
        # Using a lock to make sure that only one accessor can refresh the
        # auth0 client at a time if it's about to expire.
        async with self.__mgmt_client_lock:
            now = datetime.datetime.utcnow()

            # Set a new auth0 client if one does not exist or an existing
            # client is about to expire.
            if not self.__mgmt_client or self.__mgmt_client_expires_at <= now:
                get_token = auth0.authentication.GetToken(
                    self.__client_domain,
                    self.__client_id,
                    client_secret=self.__client_secret,
                )

                # Subtracting arbitrary modifier so refresh happens a little
                # sooner with less chance of hard erroring in downstream use.
                mgmt_token = get_token.client_credentials(self.__audience)
                mgmt_token_expiry = datetime.timedelta(seconds=mgmt_token["expires_in"])
                self.__mgmt_client_expires_at = (
                    now
                    # Use token expiry if not provided expiry or provided
                    # expiry is bigger than token expiry.
                    + (
                        min(mgmt_token_expiry, self.__mgmt_client_expiry)
                        if self.__mgmt_client_expiry is not None
                        else mgmt_token_expiry
                    )
                    # small buffer to avoid hard errors
                    - datetime.timedelta(seconds=30)
                )

                self.__mgmt_client = auth0.management.Auth0(
                    self.__client_domain, mgmt_token["access_token"]
                )

                if self.__client_session:
                    self.__mgmt_client.set_session(self.__client_session)

            return self.__mgmt_client

    async def get_organizations(self) -> auth0.management.Organizations:
        mgmt_client = await self.get_client()
        return Auth0BackoffWrapper(mgmt_client.organizations)

    async def get_roles(self) -> auth0.management.Roles:
        mgmt_client = await self.get_client()
        return Auth0BackoffWrapper(mgmt_client.roles)

    async def get_users(self) -> auth0.management.Users:
        mgmt_client = await self.get_client()
        return Auth0BackoffWrapper(mgmt_client.users)




_PER_PAGE = 100


class Auth0UserBuilder:
    """Build a User from and an Auth0 user dictionary, using cached semi-expensive operations"""

    def __init__(
        self,
        auth0_management_api_factory,
        organization_manager,
    ):

        self.__mgmt_api_factory = auth0_management_api_factory
        self.__organization_manager = organization_manager

        self.__default_user_role: UserRole | None = None
        self.__organization: Organization | None = None
        self.__role_map: dict[UserRole, str] | None = None

    @property
    async def default_user_role(self) -> UserRole:
        if not self.__default_user_role:
            # Defer default user role retrieval until it is needed.
            # org_settings = await self.__organization_manager.get_settings()
            self.__default_user_role = UserRole.GUEST # org_settings["default_user_role"]

        return self.__default_user_role

    @property
    async def organization(self) -> Organization:
        if not self.__organization:
            self.__organization = await self.__organization_manager.get_organization()
        return self.__organization

    @property
    async def role_map(self) -> dict[UserRole, str]:
        if self.__role_map is None:
            self.__role_map = await _get_role_map(self.__mgmt_api_factory)
        return self.__role_map

    async def build(self, auth0_member: dict[str, Any]) -> User:
        user_id = auth0_member["user_id"]

        organization = await self.organization

        member_role: UserRole
        try:
            # Use max of the set roles to determine the actual role.
            member_role = max(
                {
                    UserRole(auth0_role["name"])
                    for auth0_role in auth0_member["roles"]
                    if hasattr(UserRole, auth0_role["name"])
                }
            )
        except ValueError:
            # The are no roles currently set for the member. Use the default role.
            member_role = await self.default_user_role
            role_map = await self.role_map

            # TODO: Update here to fill in the value of the default role if one wasn't in Auth0

            # print(f"Adding role: '{member_role}' to Auth0 member: '{user_id}'")
            # try:
            #     # Explicitly add the role add to the organization member.
            #     auth0_mgmt_organizations = await self.__mgmt_api_factory.get_organizations()
            #     create_role_fn = auth0_mgmt_organizations.create_organization_member_roles_async
            #     await create_role_fn(organization.id, user_id, {"roles": [role_map[member_role]]})
            # except Exception as err:  # pylint: disable=broad-except
            #     # Except and warn. This isn't a show stopper error as we have already added
            #     # the default in memory.
            #     print(
            #         f"Error adding role: '{member_role}' to Auth0 member: '{user_id}'. " f"{err}"
            #     )
        # Create user model
        return User(
            email=auth0_member["email"],
            id=auth0_member["user_id"],
            name=auth0_member["name"],
            organization=organization,
            picture=auth0_member.get("picture"),
            role=member_role,
        )


async def _get_role_map(
    auth0_management_api_factory,
) -> dict[UserRole, str]:
    """Get a mapping between roles and their Auth0 ID.

    Returns:
        dict[constants.UserRole, str]: A map of the role and the Auth0 ID.
    """

    role_map = {}

    auth0_roles = await auth0_management_api_factory.get_roles()
    role_result = await auth0_roles.list_async()
    for role in UserRole:
        auth0_role = next(
            (r for r in role_result["roles"] if r["name"] == role.value),
            None,
        )

        if not auth0_role:
            auth0_role = await auth0_roles.create_async(
                {"name": role.value, "description": role.value.lower()}
            )

        role_map[role] = auth0_role["id"]

    return role_map

class Auth0Manager:
    """Organization and User management using (mostly) Auth0."""

    def __init__(
        self,
        organization_id: str,
        auth0_management_api_factory,
    ):
        self._organization_id = organization_id
        self.__mgmt_api_factory = auth0_management_api_factory

        self.__role_map: dict[UserRole, str] | None = None

    async def count_invitations(self) -> int:
        page = 0

        count: int = 0

        auth0_mgmt_orgs = await self.__mgmt_api_factory.get_organizations()
        while True:
            # Get invitations from Auth0
            res = await auth0_mgmt_orgs.all_organization_invitations_async(
                self._organization_id,
                page=page,
                per_page=_PER_PAGE,
            )

            if (length := len(res)) == 0:
                break

            count += length

            page += 1

        return count

    async def count_users(self) -> int:
        auth0_mgmt_organizations = await self.__mgmt_api_factory.get_organizations()

        count = 0

        from_param = None
        while True:
            auth0_member_res = await auth0_mgmt_organizations.all_organization_members_async(
                self._organization_id,
                fields=["user_id"],
                take=100,  # 100 is the maximum value for this param.
                from_param=from_param,
            )

            count += len(auth0_member_res["members"])

            if (from_param := auth0_member_res.get("next")) is None:
                break

        return count

    async def create_group(self, /, name: str, description: str, accessor_id: str) -> Group:
        raise NotImplementedError

    async def delete_group(self, group_id: str) -> None:
        raise NotImplementedError

    async def get_group(self, identifier: str) -> Group | None:
        raise NotImplementedError


    async def get_organization(self) -> Organization:
        print("Retrieving Organization from Auth0...")
        auth0_mgmt_orgs = await self.__mgmt_api_factory.get_organizations()
        response = await auth0_mgmt_orgs.get_organization_async(self._organization_id)

        return Organization(
            id=response["id"],
            name=response["name"],
            display_name=response["display_name"],
            logo_url=response.get("branding", {}).get("logo_url"),
            pypi_token=response.get("metadata", {}).get("pypi_token"),
        )

    async def get_user(self, user_id: str) -> User | None:
        async for user in self.iter_users(search=[(user_id, ("email", "user_id"))]):
            return user
        return None

    async def iter_groups(
        self,
        /,
        search: list[tuple[str, list[Literal["id", "name", "slug", "user"]]]] | None = None,
        order: tuple[Literal["name"], Literal[1, -1]] | None = None,
    ) -> AsyncIterator[Group]:
        raise NotImplementedError


    async def _build_user(
        self, user_builder: Auth0UserBuilder, auth0_member: dict[str, Any]
    ) -> User:
        return await user_builder.build(auth0_member)

    async def __iter_users(
        self, search: list[tuple[str, list[Literal["email", "id", "name"]]]] | None
    ) -> AsyncIterator[User]:
        search = (
            [
                (
                    re.compile(re.escape(term.lower()), re.IGNORECASE),
                    ["id" if field == "user_id" else field for field in fields],
                )
                for term, fields in search
            ]
            if search
            else []
        )

        user_builder = Auth0UserBuilder(self.__mgmt_api_factory, self)
        auth0_mgmt_organizations = await self.__mgmt_api_factory.get_organizations()

        from_param = None
        while True:
            auth0_member_res = await auth0_mgmt_organizations.all_organization_members_async(
                self._organization_id,
                fields=["roles", "user_id", "email", "picture", "name"],
                take=_PER_PAGE,
                from_param=from_param,
            )

            for auth0_member in auth0_member_res["members"]:
                user = await self._build_user(user_builder, auth0_member)

                for pattern, fields in search:
                    if not any(re.search(pattern, getattr(user, field)) for field in fields):
                        break
                else:
                    yield user

            if (from_param := auth0_member_res.get("next")) is None:
                break

    async def iter_users(
        self,
        /,
        search: list[tuple[str, list[Literal["email", "id", "name"]]]] | None = None,
        order: tuple[Literal["email", "name"], Literal[1, -1]] | None = None,
    ) -> AsyncIterator[User]:
        print("Retrieving User Information from Auth0...")
        user_iter = self.__iter_users(search)

        # Only sort if `order`` is explicitly provided. Getting all the user into memory to sort
        # can be an expensive operation.
        if order is None:
            async for user in user_iter:
                yield user
        else:
            users = [user async for user in user_iter]

            key, reverse = order[0], order[1] != 1
            for user in sorted(
                users, key=lambda user: getattr(user, key).lower(), reverse=reverse
            ):
                yield user

    async def remove_user(self, user_id: str) -> None:
        if not await self._is_auth0_organization_member(user_id):
            return

        auth_mgmt_organizations = await self.__mgmt_api_factory.get_organizations()

        # Remove member from organization.
        await auth_mgmt_organizations.delete_organization_members_async(
            self._organization_id, {"members": [user_id]}
        )

    async def revoke_invitation(self, invitation_id: str) -> None:
        auth0_mgmt_orgs = await self.__mgmt_api_factory.get_organizations()
        await auth0_mgmt_orgs.delete_organization_invitation_async(
            self._organization_id, invitation_id
        )


    async def set_user_role(self, user_id: str, role: UserRole) -> None:
        # Get all roles and the member's roles.
        auth0_mgmt_orgs = await self.__mgmt_api_factory.get_organizations()

        role_map = await self._get_role_map()

        get_member_roles = auth0_mgmt_orgs.all_organization_member_roles_async
        member_roles_response = await get_member_roles(self._organization_id, user_id)

        # Add the roles to the member's roles.
        add_role_id = role_map[role]
        tasks = [
            auth0_mgmt_orgs.create_organization_member_roles_async(
                self._organization_id, user_id, {"roles": [add_role_id]}
            )
        ]

        # Remove any other roles that might be attached to the member. This
        # could be from manually added through Auth0 or cleanup of old roles.
        if remove_role_ids := [r["id"] for r in member_roles_response if r["id"] != add_role_id]:
            task = auth0_mgmt_orgs.delete_organization_member_roles_async(
                self._organization_id, user_id, {"roles": remove_role_ids}
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def update_group(
        self,
        /,
        identifier: str,
        name: str,
        description: str,
        accessor_id: str,
        user_ids: list[str] | None,
    ):
        raise NotImplementedError

    async def _get_role_map(self) -> dict[UserRole, str]:
        """Get a mapping between roles and their Auth0 ID.

        Returns:
            dict[constants.UserRole, str]: A map of the role and the Auth0 ID.
        """
        if self.__role_map is None:
            self.__role_map = await _get_role_map(self.__mgmt_api_factory)

        return self.__role_map

    async def _is_auth0_organization_member(self, user_id: str) -> bool:
        """Determine whether a user is a member of this organization.

        Args:
            user_id (str): The user ID.

        Returns:
            bool: Whether the user is a member or not.
        """

        auth_mgmt_orgs = await self.__mgmt_api_factory.get_organizations()

        from_ = None
        while True:
            response = await auth_mgmt_orgs.all_organization_members_async(
                self._organization_id, take=_PER_PAGE, from_param=from_
            )

            for member in response["members"]:
                if member["user_id"] == user_id:
                    return True

            if "next" not in response:
                break

            from_ = response["next"]

        return False
