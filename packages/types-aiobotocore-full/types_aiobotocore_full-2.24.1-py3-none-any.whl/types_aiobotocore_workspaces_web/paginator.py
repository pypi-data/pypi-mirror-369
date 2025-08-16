"""
Type annotations for workspaces-web service client paginators.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/paginators/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_workspaces_web.client import WorkSpacesWebClient
    from types_aiobotocore_workspaces_web.paginator import (
        ListDataProtectionSettingsPaginator,
        ListSessionsPaginator,
    )

    session = get_session()
    with session.create_client("workspaces-web") as client:
        client: WorkSpacesWebClient

        list_data_protection_settings_paginator: ListDataProtectionSettingsPaginator = client.get_paginator("list_data_protection_settings")
        list_sessions_paginator: ListSessionsPaginator = client.get_paginator("list_sessions")
    ```
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aiobotocore.paginate import AioPageIterator, AioPaginator

from .type_defs import (
    ListDataProtectionSettingsRequestPaginateTypeDef,
    ListDataProtectionSettingsResponseTypeDef,
    ListSessionsRequestPaginateTypeDef,
    ListSessionsResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack


__all__ = ("ListDataProtectionSettingsPaginator", "ListSessionsPaginator")


if TYPE_CHECKING:
    _ListDataProtectionSettingsPaginatorBase = AioPaginator[
        ListDataProtectionSettingsResponseTypeDef
    ]
else:
    _ListDataProtectionSettingsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDataProtectionSettingsPaginator(_ListDataProtectionSettingsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListDataProtectionSettings.html#WorkSpacesWeb.Paginator.ListDataProtectionSettings)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/paginators/#listdataprotectionsettingspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDataProtectionSettingsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDataProtectionSettingsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListDataProtectionSettings.html#WorkSpacesWeb.Paginator.ListDataProtectionSettings.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/paginators/#listdataprotectionsettingspaginator)
        """


if TYPE_CHECKING:
    _ListSessionsPaginatorBase = AioPaginator[ListSessionsResponseTypeDef]
else:
    _ListSessionsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListSessionsPaginator(_ListSessionsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListSessions.html#WorkSpacesWeb.Paginator.ListSessions)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/paginators/#listsessionspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListSessionsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListSessionsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces-web/paginator/ListSessions.html#WorkSpacesWeb.Paginator.ListSessions.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_workspaces_web/paginators/#listsessionspaginator)
        """
