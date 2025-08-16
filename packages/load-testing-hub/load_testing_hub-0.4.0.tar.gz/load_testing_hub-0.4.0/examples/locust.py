import asyncio
from pathlib import Path

from pydantic import HttpUrl

from load_testing_hub import (
    Service,
    Scenario,
    Pipeline,
    upload_locust_report,
    UploadLocustReportParams
)


async def main():
    await upload_locust_report(
        UploadLocustReportParams(
            api_url="http://localhost:8000",
            service=Service(id=1),
            scenario=Scenario(
                id=1,
                name="get accounts",
                file="./scenarios/get_accounts/v1.0.conf",
                version="v1.0",
                number_of_users=500,
                runtime_duration="3m"
            ),
            trigger_pipeline=Pipeline(
                ci_job_url=HttpUrl("http://localhost:8001/pipeline/1/job/3"),
                ci_pipeline_url=HttpUrl("http://localhost:8001/pipeline/1"),
                ci_project_version="v1.11.0"
            ),
            load_tests_pipeline=Pipeline(
                ci_job_url=HttpUrl("http://localhost:8001/pipeline/3/job/9"),
                ci_pipeline_url=HttpUrl("http://localhost:8001/pipeline/3"),
            ),
            csv_locust_stats_file=Path("locust_stats.csv"),
            json_locust_ratio_file=Path("locust_ratio.json"),
            csv_locust_exceptions_file=Path("locust_exceptions.csv"),
            csv_locust_stats_history_file=Path("locust_stats_history.csv"),
        )
    )


asyncio.run(main())
