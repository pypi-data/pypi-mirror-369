"""
Income API implementation.
Based on PHP library's Api\\Income class.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from ._http import AsyncHTTPClient
from .dto.income import (
    AtomDateTime,
    CancelCommentType,
    CancelRequest,
    IncomeClient,
    IncomeRequest,
    IncomeServiceItem,
    IncomeType,
    PaymentType,
)


class IncomeAPI:
    """
    Income API for creating and managing receipts.

    Provides async methods for:
    - Creating income receipts (single or multiple items)
    - Cancelling income receipts

    Maps to PHP Api\\Income functionality.
    """

    def __init__(self, http_client: AsyncHTTPClient):
        self.http = http_client

    async def create(
        self,
        name: str,
        amount: Decimal | float | int | str,
        quantity: Decimal | float | int | str = 1,
        operation_time: datetime | None = None,
        client: IncomeClient | None = None,
    ) -> dict[str, Any]:
        """
        Create income receipt with single service item.

        Maps to PHP Income::create() method.

        Args:
            name: Service name/description
            amount: Service amount (converted to Decimal)
            quantity: Service quantity (converted to Decimal, default: 1)
            operation_time: Operation datetime (default: now)
            client: Client information (default: individual client)

        Returns:
            Dictionary with response data including approvedReceiptUuid

        Raises:
            ValidationException: For validation errors
            DomainException: For other API errors
        """
        # Convert to IncomeServiceItem
        service_item = IncomeServiceItem(
            name=name,
            amount=Decimal(str(amount)),
            quantity=Decimal(str(quantity)),
        )

        return await self.create_multiple_items([service_item], operation_time, client)

    async def create_multiple_items(
        self,
        services: list[IncomeServiceItem],
        operation_time: datetime | None = None,
        client: IncomeClient | None = None,
    ) -> dict[str, Any]:
        """
        Create income receipt with multiple service items.

        Maps to PHP Income::createMultipleItems() method.

        Args:
            services: List of service items
            operation_time: Operation datetime (default: now)
            client: Client information (default: individual client)

        Returns:
            Dictionary with response data including approvedReceiptUuid

        Raises:
            ValidationException: For validation errors (empty items, invalid amounts, etc.)
            DomainException: For other API errors
        """
        if not services:
            raise ValueError("Services cannot be empty")

        # Validate client for legal entity (mirrors PHP validation)
        if client and client.income_type == IncomeType.FROM_LEGAL_ENTITY:
            if not client.inn:
                raise ValueError("Client INN cannot be empty for legal entity")
            if not client.display_name:
                raise ValueError("Client DisplayName cannot be empty for legal entity")

        # Calculate total amount (mirrors PHP BigDecimal logic)
        total_amount = sum(item.get_total_amount() for item in services)

        # Create request object
        request = IncomeRequest(
            operation_time=(
                AtomDateTime.from_datetime(operation_time)
                if operation_time
                else AtomDateTime.now()
            ),
            request_time=AtomDateTime.now(),
            services=services,
            total_amount=str(total_amount),
            client=client or IncomeClient(),
            payment_type=PaymentType.CASH,
            ignore_max_total_income_restriction=False,
        )

        # Make API request
        response = await self.http.post("/income", json_data=request.model_dump())
        return response.json()  # type: ignore[no-any-return]

    async def cancel(
        self,
        receipt_uuid: str,
        comment: CancelCommentType | str,
        operation_time: datetime | None = None,
        request_time: datetime | None = None,
        partner_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel income receipt.

        Maps to PHP Income::cancel() method.

        Args:
            receipt_uuid: Receipt UUID to cancel
            comment: Cancellation reason (enum or string)
            operation_time: Operation datetime (default: now)
            request_time: Request datetime (default: now)
            partner_code: Partner code (optional)

        Returns:
            Dictionary with cancellation response data

        Raises:
            ValidationException: For validation errors (empty UUID, invalid comment)
            DomainException: For other API errors
        """
        # Validate receipt UUID
        if not receipt_uuid.strip():
            raise ValueError("Receipt UUID cannot be empty")

        # Convert comment to enum if string
        if isinstance(comment, str):
            # Try to find matching enum value
            comment_enum = None
            for enum_val in CancelCommentType:
                if enum_val.value == comment:
                    comment_enum = enum_val
                    break

            if comment_enum is None:
                valid_comments = [e.value for e in CancelCommentType]
                raise ValueError(
                    f"Comment is invalid. Must be one of: {valid_comments}"
                )

            comment = comment_enum

        # Create request object
        request = CancelRequest(
            operation_time=(
                AtomDateTime.from_datetime(operation_time)
                if operation_time
                else AtomDateTime.now()
            ),
            request_time=(
                AtomDateTime.from_datetime(request_time)
                if request_time
                else AtomDateTime.now()
            ),
            comment=comment,
            receipt_uuid=receipt_uuid.strip(),
            partner_code=partner_code,
        )

        # Make API request
        response = await self.http.post("/cancel", json_data=request.model_dump())
        return response.json()  # type: ignore[no-any-return]
