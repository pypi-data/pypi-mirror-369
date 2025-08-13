from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, validator


class Currency(BaseModel):
    currencyCodeA: int
    currencyCodeB: int
    date: int
    rateSell: float = None
    rateBuy: float = None
    rateCross: float = None

    def utc_date(self):
        return datetime.utcfromtimestamp(self.date)


class Account(BaseModel):
    id: str
    sendId: str
    balance: float
    credit_limit: float = Field(validation_alias='creditLimit')
    type: str
    currency_code: int = Field(validation_alias='currencyCode')
    cashback_type: str = Field(validation_alias='cashbackType')
    masked_pan: Optional[List[str]] = Field(validation_alias='maskedPan')
    iban: Optional[str] = None

    @field_validator('balance', 'credit_limit', mode='before')
    @classmethod
    def convert_to_money(cls, value) -> float:
        return value / 100


class ClientInfo(BaseModel):
    id: str = Field(validation_alias='clientId')
    name: str
    webhook_url: str = Field(validation_alias='webHookUrl')
    permissions: str
    accounts: List[Account]


class StatementItem(BaseModel):
    id: str
    time: int
    description: str
    mcc: int
    hold: bool
    amount: float
    operation_amount: int
    currency_code: int
    commission_rate: int
    cashback_amount: int
    balance: float
    comment: str = None
    receipt_id: str = None
    counter_edrpou: str = None
    counter_iban: str = None

    @validator('balance', 'amount', 'operation_amount', 'commission_rate', 'cashback_amount', pre=True, always=True)
    def convert_to_money(cls, value):
        return value / 100

    class Config:
        fields = {
            'operation_amount': 'operationAmount',
            'currency_code': 'currencyCode',
            'commission_rate': 'commissionRate',
            'cashback_amount': 'cashbackAmount',
            'receipt_id': 'receiptId',
            'counter_edrpou': 'counterEdrpou',
            'counter_iban': 'counterIban',
        }
