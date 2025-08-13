from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrincipalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PRINCIPAL_TYPE_UNSPECIFIED: _ClassVar[PrincipalType]
    PRINCIPAL_TYPE_USER: _ClassVar[PrincipalType]
    PRINCIPAL_TYPE_SERVICE_ACCOUNT: _ClassVar[PrincipalType]
    PRINCIPAL_TYPE_GROUP: _ClassVar[PrincipalType]
    PRINCIPAL_TYPE_WORKSPACE: _ClassVar[PrincipalType]
PRINCIPAL_TYPE_UNSPECIFIED: PrincipalType
PRINCIPAL_TYPE_USER: PrincipalType
PRINCIPAL_TYPE_SERVICE_ACCOUNT: PrincipalType
PRINCIPAL_TYPE_GROUP: PrincipalType
PRINCIPAL_TYPE_WORKSPACE: PrincipalType

class Principal(_message.Message):
    __slots__ = ["principal_type", "id"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    principal_type: PrincipalType
    id: str
    def __init__(self, principal_type: _Optional[_Union[PrincipalType, str]] = ..., id: _Optional[str] = ...) -> None: ...

class PrincipalBasic(_message.Message):
    __slots__ = ["user", "service_account", "group", "workspace"]
    USER_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    user: UserBasic
    service_account: ServiceAccountBasic
    group: GroupBasic
    workspace: WorkspaceBasic
    def __init__(self, user: _Optional[_Union[UserBasic, _Mapping]] = ..., service_account: _Optional[_Union[ServiceAccountBasic, _Mapping]] = ..., group: _Optional[_Union[GroupBasic, _Mapping]] = ..., workspace: _Optional[_Union[WorkspaceBasic, _Mapping]] = ...) -> None: ...

class ServiceAccountBasic(_message.Message):
    __slots__ = ["id", "name", "description", "is_active", "creator", "owner"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_active: bool
    creator: Principal
    owner: PrincipalBasic
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_active: bool = ..., creator: _Optional[_Union[Principal, _Mapping]] = ..., owner: _Optional[_Union[PrincipalBasic, _Mapping]] = ...) -> None: ...

class UserBasic(_message.Message):
    __slots__ = ["okta_id", "first_name", "last_name", "login_email"]
    OKTA_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    LOGIN_EMAIL_FIELD_NUMBER: _ClassVar[int]
    okta_id: str
    first_name: str
    last_name: str
    login_email: str
    def __init__(self, okta_id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., login_email: _Optional[str] = ...) -> None: ...

class GroupBasic(_message.Message):
    __slots__ = ["id", "name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class WorkspaceBasic(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...
