"""Information about and for meta-processes, such as CI/CD, monitoring, and logging."""

from pydantic import AliasChoices, AnyUrl, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings


class SharedCISettings(BaseSettings):
    """Shared settings for CI/CD pipelines."""

    tests_ongoing: bool = Field(default=False)
