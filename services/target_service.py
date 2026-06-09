from repositories.target_repository import target_repository


class TargetService:
    def validate_target_data(self, data: dict) -> None:
        required_fields = ["user_id", "name", "url"]

        for field in required_fields:
            if field not in data or data[field] in (None, ""):
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(data["user_id"], int):
            raise ValueError("Field user_id must be an integer")

        if not data["url"].startswith(("http://", "https://")):
            raise ValueError("Field url must start with http:// or https://")

    def create_target(self, data: dict) -> dict:
        self.validate_target_data(data)

        target_id = target_repository.create_target(data)

        return {
            "success": True,
            "message": "Monitoring target created successfully",
            "target_id": target_id,
        }

    def get_all_targets(self) -> dict:
        targets = target_repository.get_all_targets()

        return {
            "success": True,
            "targets": targets,
        }

    def get_target_by_id(self, target_id: int) -> dict:
        target = target_repository.get_target_by_id(target_id)

        if target is None:
            return {
                "success": False,
                "error": "Monitoring target not found",
            }

        return {
            "success": True,
            "target": target,
        }

    def update_target(self, target_id: int, data: dict) -> dict:
        self.validate_target_data(data)

        updated = target_repository.update_target(target_id, data)

        if not updated:
            return {
                "success": False,
                "error": "Monitoring target not found",
            }

        return {
            "success": True,
            "message": "Monitoring target updated successfully",
        }

    def deactivate_target(self, target_id: int) -> dict:
        deactivated = target_repository.deactivate_target(target_id)

        if not deactivated:
            return {
                "success": False,
                "error": "Monitoring target not found",
            }

        return {
            "success": True,
            "message": "Monitoring target deactivated successfully",
        }


target_service = TargetService()
