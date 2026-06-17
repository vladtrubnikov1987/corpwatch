from repositories.report_repository import report_repository
from utils.logger import logger


class ReportService:
    def get_summary_report(self) -> dict:
        logger.info("Generating summary report")

        summary = report_repository.get_summary_report()

        return {
            "success": True,
            "report_type": "summary",
            "data": summary,
        }


report_service = ReportService()