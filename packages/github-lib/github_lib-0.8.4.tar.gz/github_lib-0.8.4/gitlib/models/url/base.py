from pydantic import BaseModel, HttpUrl


class GithubUrl(BaseModel):
    url: HttpUrl
