from typing import Annotated, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class KeeperLoginItemBase(BaseSettings):
    username: Annotated[str, Field(alias="login")]
    password: Annotated[str, Field(alias="password")]


class OnePasswordSettings(BaseSettings):
    token: str
    model_config = SettingsConfigDict(
        env_prefix="op_", case_sensitive=False, extra="ignore"
    )


class AzureAppRegistrationSecretsBase(BaseSettings):
    client_id: str
    tenant_id: str
    client_secret: str
    resource_app_id: Optional[str] = None
