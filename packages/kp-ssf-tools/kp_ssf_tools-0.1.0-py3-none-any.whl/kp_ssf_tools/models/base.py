from pydantic import BaseModel, ConfigDict


class SSFToolsBaseModel(BaseModel):
    """Base model for all SSF Tools data models. Sets common config."""

    model_config: ConfigDict = {
        "use_enum_values": True,
    }
