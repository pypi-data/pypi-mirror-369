from pydantic import BaseModel, ConfigDict, Field


class TmailEmail(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(examples=["e3bf86faf1d13566b1b4752f9c16285baa2cff0c"])
    body: str
    date: str
    html: str | None = None
    sender: str
    subject: str
