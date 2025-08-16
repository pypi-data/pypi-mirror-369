# coding: utf-8

"""
AvaTax Software Development Kit for Python.

   Copyright 2022 Avalara, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

    Avalara 1099 & W-9 API Definition
    ## 🔐 Authentication  Generate a **license key** from: *[Avalara Portal](https://www.avalara.com/us/en/signin.html) → Settings → License and API Keys*.  [More on authentication methods](https://developer.avalara.com/avatax-dm-combined-erp/common-setup/authentication/authentication-methods/)  [Test your credentials](https://developer.avalara.com/avatax/test-credentials/)  ## 📘 API & SDK Documentation  [Avalara SDK (.NET) on GitHub](https://github.com/avadev/Avalara-SDK-DotNet#avalarasdk--the-unified-c-library-for-next-gen-avalara-services)  [Code Examples – 1099 API](https://github.com/avadev/Avalara-SDK-DotNet/blob/main/docs/A1099/V2/Class1099IssuersApi.md#call1099issuersget) 

@author     Sachin Baijal <sachin.baijal@avalara.com>
@author     Jonathan Wenger <jonathan.wenger@avalara.com>
@copyright  2022 Avalara, Inc.
@license    https://www.apache.org/licenses/LICENSE-2.0
@version    25.8.2
@link       https://github.com/avadev/AvaTax-REST-V3-Python-SDK
"""

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from Avalara.SDK.models.A1099.V2.state_and_local_withholding_response import StateAndLocalWithholdingResponse
from Avalara.SDK.models.A1099.V2.state_efile_status_detail_response import StateEfileStatusDetailResponse
from Avalara.SDK.models.A1099.V2.status_detail import StatusDetail
from Avalara.SDK.models.A1099.V2.validation_error_response import ValidationErrorResponse
from typing import Optional, Set
from typing_extensions import Self

class Form1099DivResponse(BaseModel):
    """
    Form1099DivResponse
    """ # noqa: E501
    total_ordinary_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalOrdinaryDividends")
    qualified_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="qualifiedDividends")
    total_capital_gain_distributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalCapitalGainDistributions")
    unrecaptured_section1250_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="unrecapturedSection1250Gain")
    section1202_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="section1202Gain")
    collectibles_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="collectiblesGain")
    section897_ordinary_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="section897OrdinaryDividends")
    section897_capital_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="section897CapitalGain")
    nondividend_distributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="nondividendDistributions")
    federal_income_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="federalIncomeTaxWithheld")
    section199_a_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="section199ADividends")
    investment_expenses: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="investmentExpenses")
    foreign_tax_paid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="foreignTaxPaid")
    foreign_country_or_us_possession: Optional[StrictStr] = Field(default=None, alias="foreignCountryOrUSPossession")
    cash_liquidation_distributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="cashLiquidationDistributions")
    noncash_liquidation_distributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="noncashLiquidationDistributions")
    exempt_interest_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="exemptInterestDividends")
    specified_private_activity_bond_interest_dividends: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="specifiedPrivateActivityBondInterestDividends")
    fatca_filing_requirement: Optional[StrictBool] = Field(default=None, alias="fatcaFilingRequirement")
    type: Optional[StrictStr] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    state_and_local_withholding: Optional[StateAndLocalWithholdingResponse] = Field(default=None, alias="stateAndLocalWithholding")
    tin_type: Optional[StrictStr] = Field(default=None, alias="tinType")
    id: Optional[StrictStr] = None
    issuer_id: Optional[StrictStr] = Field(default=None, alias="issuerId")
    issuer_reference_id: Optional[StrictStr] = Field(default=None, alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, alias="issuerTin")
    tax_year: Optional[StrictInt] = Field(default=None, alias="taxYear")
    reference_id: Optional[StrictStr] = Field(default=None, alias="referenceId")
    recipient_name: Optional[StrictStr] = Field(default=None, alias="recipientName")
    recipient_tin: Optional[StrictStr] = Field(default=None, alias="recipientTin")
    recipient_second_name: Optional[StrictStr] = Field(default=None, alias="recipientSecondName")
    address: Optional[StrictStr] = None
    address2: Optional[StrictStr] = None
    city: Optional[StrictStr] = None
    state: Optional[StrictStr] = None
    zip: Optional[StrictStr] = None
    email: Optional[StrictStr] = None
    account_number: Optional[StrictStr] = Field(default=None, alias="accountNumber")
    office_code: Optional[StrictStr] = Field(default=None, alias="officeCode")
    non_us_province: Optional[StrictStr] = Field(default=None, alias="nonUsProvince")
    country_code: Optional[StrictStr] = Field(default=None, alias="countryCode")
    federal_e_file: Optional[StrictBool] = Field(default=None, alias="federalEFile")
    postal_mail: Optional[StrictBool] = Field(default=None, alias="postalMail")
    state_e_file: Optional[StrictBool] = Field(default=None, alias="stateEFile")
    tin_match: Optional[StrictBool] = Field(default=None, alias="tinMatch")
    no_tin: Optional[StrictBool] = Field(default=None, alias="noTin")
    second_tin_notice: Optional[StrictBool] = Field(default=None, alias="secondTinNotice")
    address_verification: Optional[StrictBool] = Field(default=None, alias="addressVerification")
    federal_efile_status: Optional[StatusDetail] = Field(default=None, alias="federalEfileStatus")
    e_delivery_status: Optional[StatusDetail] = Field(default=None, alias="eDeliveryStatus")
    state_efile_status: Optional[List[StateEfileStatusDetailResponse]] = Field(default=None, alias="stateEfileStatus")
    postal_mail_status: Optional[StatusDetail] = Field(default=None, alias="postalMailStatus")
    tin_match_status: Optional[StatusDetail] = Field(default=None, alias="tinMatchStatus")
    address_verification_status: Optional[StatusDetail] = Field(default=None, alias="addressVerificationStatus")
    validation_errors: Optional[List[ValidationErrorResponse]] = Field(default=None, alias="validationErrors")
    __properties: ClassVar[List[str]] = ["type", "createdAt", "updatedAt", "stateAndLocalWithholding", "tinType", "id", "issuerId", "issuerReferenceId", "issuerTin", "taxYear", "referenceId", "recipientName", "recipientTin", "recipientSecondName", "address", "address2", "city", "state", "zip", "email", "accountNumber", "officeCode", "nonUsProvince", "countryCode", "federalEFile", "postalMail", "stateEFile", "tinMatch", "noTin", "secondTinNotice", "addressVerification", "federalEfileStatus", "eDeliveryStatus", "stateEfileStatus", "postalMailStatus", "tinMatchStatus", "addressVerificationStatus", "validationErrors"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT']):
            raise ValueError("must be one of enum values ('1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT')")
        return value

    @field_validator('tin_type')
    def tin_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['EIN', 'SSN', 'ITIN', 'ATIN']):
            raise ValueError("must be one of enum values ('EIN', 'SSN', 'ITIN', 'ATIN')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Form1099DivResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "type",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of state_and_local_withholding
        if self.state_and_local_withholding:
            _dict['stateAndLocalWithholding'] = self.state_and_local_withholding.to_dict()
        # override the default output from pydantic by calling `to_dict()` of federal_efile_status
        if self.federal_efile_status:
            _dict['federalEfileStatus'] = self.federal_efile_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of e_delivery_status
        if self.e_delivery_status:
            _dict['eDeliveryStatus'] = self.e_delivery_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in state_efile_status (list)
        _items = []
        if self.state_efile_status:
            for _item in self.state_efile_status:
                if _item:
                    _items.append(_item.to_dict())
            _dict['stateEfileStatus'] = _items
        # override the default output from pydantic by calling `to_dict()` of postal_mail_status
        if self.postal_mail_status:
            _dict['postalMailStatus'] = self.postal_mail_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of tin_match_status
        if self.tin_match_status:
            _dict['tinMatchStatus'] = self.tin_match_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of address_verification_status
        if self.address_verification_status:
            _dict['addressVerificationStatus'] = self.address_verification_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in validation_errors (list)
        _items = []
        if self.validation_errors:
            for _item in self.validation_errors:
                if _item:
                    _items.append(_item.to_dict())
            _dict['validationErrors'] = _items
        # set to None if federal_efile_status (nullable) is None
        # and model_fields_set contains the field
        if self.federal_efile_status is None and "federal_efile_status" in self.model_fields_set:
            _dict['federalEfileStatus'] = None

        # set to None if e_delivery_status (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_status is None and "e_delivery_status" in self.model_fields_set:
            _dict['eDeliveryStatus'] = None

        # set to None if state_efile_status (nullable) is None
        # and model_fields_set contains the field
        if self.state_efile_status is None and "state_efile_status" in self.model_fields_set:
            _dict['stateEfileStatus'] = None

        # set to None if postal_mail_status (nullable) is None
        # and model_fields_set contains the field
        if self.postal_mail_status is None and "postal_mail_status" in self.model_fields_set:
            _dict['postalMailStatus'] = None

        # set to None if tin_match_status (nullable) is None
        # and model_fields_set contains the field
        if self.tin_match_status is None and "tin_match_status" in self.model_fields_set:
            _dict['tinMatchStatus'] = None

        # set to None if address_verification_status (nullable) is None
        # and model_fields_set contains the field
        if self.address_verification_status is None and "address_verification_status" in self.model_fields_set:
            _dict['addressVerificationStatus'] = None

        # set to None if validation_errors (nullable) is None
        # and model_fields_set contains the field
        if self.validation_errors is None and "validation_errors" in self.model_fields_set:
            _dict['validationErrors'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Form1099DivResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "type": obj.get("type"),
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt"),
            "stateAndLocalWithholding": StateAndLocalWithholdingResponse.from_dict(obj["stateAndLocalWithholding"]) if obj.get("stateAndLocalWithholding") is not None else None,
            "tinType": obj.get("tinType"),
            "id": obj.get("id"),
            "issuerId": obj.get("issuerId"),
            "issuerReferenceId": obj.get("issuerReferenceId"),
            "issuerTin": obj.get("issuerTin"),
            "taxYear": obj.get("taxYear"),
            "referenceId": obj.get("referenceId"),
            "recipientName": obj.get("recipientName"),
            "recipientTin": obj.get("recipientTin"),
            "recipientSecondName": obj.get("recipientSecondName"),
            "address": obj.get("address"),
            "address2": obj.get("address2"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "email": obj.get("email"),
            "accountNumber": obj.get("accountNumber"),
            "officeCode": obj.get("officeCode"),
            "nonUsProvince": obj.get("nonUsProvince"),
            "countryCode": obj.get("countryCode"),
            "federalEFile": obj.get("federalEFile"),
            "postalMail": obj.get("postalMail"),
            "stateEFile": obj.get("stateEFile"),
            "tinMatch": obj.get("tinMatch"),
            "noTin": obj.get("noTin"),
            "secondTinNotice": obj.get("secondTinNotice"),
            "addressVerification": obj.get("addressVerification"),
            "federalEfileStatus": StatusDetail.from_dict(obj["federalEfileStatus"]) if obj.get("federalEfileStatus") is not None else None,
            "eDeliveryStatus": StatusDetail.from_dict(obj["eDeliveryStatus"]) if obj.get("eDeliveryStatus") is not None else None,
            "stateEfileStatus": [StateEfileStatusDetailResponse.from_dict(_item) for _item in obj["stateEfileStatus"]] if obj.get("stateEfileStatus") is not None else None,
            "postalMailStatus": StatusDetail.from_dict(obj["postalMailStatus"]) if obj.get("postalMailStatus") is not None else None,
            "tinMatchStatus": StatusDetail.from_dict(obj["tinMatchStatus"]) if obj.get("tinMatchStatus") is not None else None,
            "addressVerificationStatus": StatusDetail.from_dict(obj["addressVerificationStatus"]) if obj.get("addressVerificationStatus") is not None else None,
            "validationErrors": [ValidationErrorResponse.from_dict(_item) for _item in obj["validationErrors"]] if obj.get("validationErrors") is not None else None
        })
        return _obj


