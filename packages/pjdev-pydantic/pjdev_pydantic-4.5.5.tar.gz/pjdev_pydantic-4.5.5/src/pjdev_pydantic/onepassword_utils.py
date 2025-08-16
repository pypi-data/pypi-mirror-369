import asyncio
from typing import (
    Type,
    TypeVar,
    Tuple,
    Any,
    Dict,
    Annotated
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource
)
from pydantic.fields import FieldInfo
from loguru import logger

from onepassword.client import Client
import nest_asyncio

from pjdev_pydantic.models import OnePasswordSettings

nest_asyncio.apply()

T = TypeVar('T', bound=BaseSettings)


async def get_onepassword_client(settings: OnePasswordSettings) -> Client:
    return await Client.authenticate(auth=settings.token, integration_name="My 1Password Integration", integration_version="v1.0.0")


def onepassword_settings_source_class_factory(client: Client) -> Type[
    PydanticBaseSettingsSource]:

    class OnePasswordConfigSettingsSource(PydanticBaseSettingsSource):

        def get_field_value(
                self, field: FieldInfo, field_name: str
        ) -> Tuple[Any, str, bool]:
            if not field.alias:
                return None, field_name, False
            try:
                loop = asyncio.get_event_loop()
                future = client.secrets.resolve(f"op://{field.alias}")
                secret_value = loop.run_until_complete(future)
            except ValueError as e:
                logger.error(e)
                raise e
            return secret_value, field_name, False

        def prepare_field_value(
                self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
        ) -> Any:
            return value

        def __call__(self) -> Dict[str, Any]:
            d: Dict[str, Any] = {}

            for field_name, field in self.settings_cls.model_fields.items():
                field_value, field_key, value_is_complex = self.get_field_value(
                        field, field_name
                )
                field_value = self.prepare_field_value(
                        field_name, field, field_value, value_is_complex
                )
                if field_value is not None:
                    d[field_key] = field_value

            return d

    return OnePasswordConfigSettingsSource


def onepassword_settings_class_factory(class_type: Type[T], settings: OnePasswordSettings) -> Type[T]:
    class OnePasswordSecretsClass(class_type):
        model_config = SettingsConfigDict(
                populate_by_name=True
        )

        @classmethod
        def settings_customise_sources(
                cls,
                settings_cls: Type[class_type],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
        ) -> Tuple[PydanticBaseSettingsSource, ...]:
            loop = asyncio.get_event_loop()
            src = onepassword_settings_source_class_factory(
                            client=loop.run_until_complete(get_onepassword_client(settings))
                    )(settings_cls)
            return (src,)

    return OnePasswordSecretsClass


if __name__ == '__main__':
    from pydantic import Field
    from pathlib import Path

    _settings = OnePasswordSettings(
            _env_file=Path(__file__).parent / '.env'
    )


    class A(BaseSettings):
        db_pass: Annotated[str, Field(alias='fema/fcp-pj_db-pass/password')]


    async def main():
        _client = await get_onepassword_client(_settings)
        class_type = onepassword_settings_class_factory(A, _client)
        _config = class_type()
        print(_config)


    asyncio.run(main())
