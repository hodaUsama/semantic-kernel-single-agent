import json
from datetime import datetime, timezone
from typing import Annotated, Any

from semantic_kernel.functions import kernel_function


class DeviceSupportPlugin:
    """
    Provides device information, Windows update history,
    and support-ticket creation for IT support scenarios.

    The data used in this demo is mocked. In a production system,
    these functions could call device-management and ticketing APIs.
    """

    @staticmethod
    def _print_tool_execution(
        tool_name: str,
        arguments: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """
        Prints a clear representation of the function call and its result.

        This logging is intended to make the Semantic Kernel
        function-calling workflow visible during the demo.
        """

        print("\n" + "=" * 70)
        print("TOOL EXECUTION")
        print("=" * 70)

        print(f"Tool: DeviceSupport.{tool_name}")

        print("\nArguments:")
        print(
            json.dumps(
                arguments,
                indent=2,
                ensure_ascii=False,
            )
        )

        print("\nReturned result:")
        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        print("=" * 70)

    @kernel_function(
        name="get_device_information",
        description=(
            "Retrieves the employee laptop hardware, operating system, "
            "storage, memory, and current device status. Call this function "
            "when diagnosing an employee laptop problem."
        ),
    )
    def get_device_information(
        self,
        employee_id: Annotated[
            str,
            "The unique employee ID associated with the laptop.",
        ],
    ) -> str:
        """
        Retrieves mocked device information for the supplied employee ID.
        """

        device_information = {
            "employee_id": employee_id,
            "device": {
                "manufacturer": "Dell",
                "model": "Latitude 7440",
                "device_type": "Laptop",
            },
            "operating_system": {
                "name": "Windows 11 Pro",
                "version": "24H2",
            },
            "hardware": {
                "memory": "16 GB RAM",
                "storage": "512 GB SSD",
                "available_storage": "118 GB",
            },
            "device_status": "Online",
        }

        self._print_tool_execution(
            tool_name="get_device_information",
            arguments={
                "employee_id": employee_id,
            },
            result=device_information,
        )

        return json.dumps(
            device_information,
            indent=2,
            ensure_ascii=False,
        )

    @kernel_function(
        name="get_recent_updates",
        description=(
            "Retrieves recently installed Windows updates and any known "
            "issues associated with those updates. Call this function when "
            "an employee reports that a problem started after an update."
        ),
    )
    def get_recent_updates(
        self,
        employee_id: Annotated[
            str,
            "The unique employee ID whose update history is required.",
        ],
    ) -> str:
        """
        Retrieves mocked Windows update information for the supplied employee.
        """

        update_information = {
            "employee_id": employee_id,
            "latest_update": {
                "knowledge_base_id": "KB5062553",
                "update_type": "Windows cumulative update",
                "installed_at": "2026-07-22T18:30:00",
                "installation_status": "Successfully installed",
            },
            "known_issue": {
                "is_known_issue": True,
                "description": (
                    "Several managed devices reported crashes "
                    "after installing this update."
                ),
                "affected_devices": "Multiple managed Windows devices",
            },
            "recommended_action": {
                "action": "Escalate to the Windows Support team",
                "requires_it_approval": True,
                "user_should_uninstall_update": False,
            },
        }

        self._print_tool_execution(
            tool_name="get_recent_updates",
            arguments={
                "employee_id": employee_id,
            },
            result=update_information,
        )

        return json.dumps(
            update_information,
            indent=2,
            ensure_ascii=False,
        )

    @kernel_function(
        name="create_support_ticket",
        description=(
            "Creates an IT support ticket for an employee issue that requires "
            "investigation or escalation. Call this function when a known "
            "update issue affects multiple devices, when IT approval is "
            "required, or when the remediation may risk data loss."
        ),
    )
    def create_support_ticket(
        self,
        employee_id: Annotated[
            str,
            "The employee ID associated with the reported problem.",
        ],
        issue_summary: Annotated[
            str,
            "A concise summary of the diagnosed technical issue.",
        ],
        priority: Annotated[
            str,
            "The ticket priority, such as Low, Medium, High, or Critical.",
        ],
    ) -> str:
        """
        Creates a mocked IT support ticket.

        In production, this function could call a real ticketing platform
        such as ServiceNow, Jira Service Management, or Azure DevOps.
        """

        created_at = datetime.now(timezone.utc)

        ticket_id = (
            f"INC-{created_at.strftime('%Y%m%d-%H%M%S')}"
        )

        ticket_information = {
            "ticket_id": ticket_id,
            "employee_id": employee_id,
            "issue_summary": issue_summary,
            "priority": priority,
            "assigned_team": "Windows Support",
            "status": "Open",
            "created_at_utc": created_at.isoformat(),
            "next_action": (
                "The Windows Support team will investigate the update "
                "and contact the employee."
            ),
        }

        self._print_tool_execution(
            tool_name="create_support_ticket",
            arguments={
                "employee_id": employee_id,
                "issue_summary": issue_summary,
                "priority": priority,
            },
            result=ticket_information,
        )

        return json.dumps(
            ticket_information,
            indent=2,
            ensure_ascii=False,
        )