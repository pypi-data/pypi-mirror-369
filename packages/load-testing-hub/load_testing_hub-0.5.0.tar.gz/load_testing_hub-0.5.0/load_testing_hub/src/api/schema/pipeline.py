from pydantic import BaseModel


class Pipeline(BaseModel):
    ci_job_url: str | None = None
    ci_pipeline_url: str | None = None
    ci_project_version: str | None = None
