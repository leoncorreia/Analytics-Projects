from pydantic import BaseModel


class ProviderHealth(BaseModel):
    name: str
    configured: bool
    demo_mode: bool

