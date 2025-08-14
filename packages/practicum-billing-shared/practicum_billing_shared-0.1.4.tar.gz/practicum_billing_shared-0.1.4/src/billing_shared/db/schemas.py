from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.types import (
    CardNetwork,
    OrderStatus,
    PaymentMethodName,
    PaymentProviderName,
    PaymentStatus,
    RefundStatus,
)


class OrmModelDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None


class OrderAddDTO(BaseModel):
    title: str
    status: Literal[OrderStatus.NEW] = OrderStatus.NEW
    user_id: UUID


class OrderDTO(OrmModelDTO, OrderAddDTO):
    pass


class CardDetails(BaseModel):
    card_network: CardNetwork
    card_last_four: str = Field(min_length=4, max_length=4)
    expiry_year: int | None = None
    expiry_month: Literal["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", None] = None


class YooMoneyWalletDetails(BaseModel):
    title: str | None = None
    account_number: str | None = None


class PayerBankDetails(BaseModel):
    bank_id: str
    bic: str


class SbpDetails(BaseModel):
    title: str | None = None
    payer_bank_details: PayerBankDetails | None = None


class PaymentMethodAddDTO(BaseModel):
    user_id: UUID
    name: PaymentMethodName
    provider_name: PaymentProviderName
    id_at_provider: str
    details: Union[CardDetails, SbpDetails, YooMoneyWalletDetails]


class PaymentMethodDTO(OrmModelDTO, PaymentMethodAddDTO):
    pass


class PaymentAddDTO(BaseModel):
    currency: str = "RUB"
    amount: float
    status: Literal[PaymentStatus.CREATED] = PaymentStatus.CREATED
    user_id: UUID
    order_id: UUID
    payment_method_id: UUID | None = None


class PaymentDTO(OrmModelDTO, PaymentAddDTO):
    status: PaymentStatus
    is_refundable: bool | None
    external_id: str | None = None
    payment_method: PaymentMethodDTO | None = None
    result_data: dict | None = None


class RefundAddDTO(BaseModel):
    payment_id: UUID


class RefundDTO(OrmModelDTO, RefundAddDTO):
    status: RefundStatus
    external_id: str | None = None
    result_data: dict | None = None
