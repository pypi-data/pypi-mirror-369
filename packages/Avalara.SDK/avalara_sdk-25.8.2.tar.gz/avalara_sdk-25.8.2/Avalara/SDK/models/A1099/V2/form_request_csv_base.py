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
    ## 🔐 Authentication  Use **username/password** or generate a **license key** from: *Avalara Portal → Settings → License and API Keys*.  [More on authentication methods](https://developer.avalara.com/avatax-dm-combined-erp/common-setup/authentication/authentication-methods/)  [Test your credentials](https://developer.avalara.com/avatax/test-credentials/)  ## 📘 API & SDK Documentation  [Avalara SDK (.NET) on GitHub](https://github.com/avadev/Avalara-SDK-DotNet#avalarasdk--the-unified-c-library-for-next-gen-avalara-services)  [Code Examples – 1099 API](https://github.com/avadev/Avalara-SDK-DotNet/blob/main/docs/A1099/V2/Class1099IssuersApi.md#call1099issuersget) 

@author     Sachin Baijal <sachin.baijal@avalara.com>
@author     Jonathan Wenger <jonathan.wenger@avalara.com>
@copyright  2022 Avalara, Inc.
@license    https://www.apache.org/licenses/LICENSE-2.0
@version    25.7.2
@link       https://github.com/avadev/AvaTax-REST-V3-Python-SDK
"""

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.A1099.V2.state_and_local_withholding_request import StateAndLocalWithholdingRequest
from typing import Optional, Set
from typing_extensions import Self

class FormRequestCsvBase(BaseModel):
    """
    FormRequestCsvBase
    """ # noqa: E501
    issuer_reference_id: Optional[StrictStr] = Field(default=None, alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, alias="issuerTin")
    tax_year: Optional[StrictInt] = Field(default=None, alias="taxYear")
    issuer_id: Optional[StrictStr] = Field(default=None, alias="issuerId")
    reference_id: Optional[StrictStr] = Field(default=None, alias="referenceId")
    recipient_name: Optional[StrictStr] = Field(default=None, alias="recipientName")
    recipient_tin: Optional[StrictStr] = Field(default=None, alias="recipientTin")
    tin_type: Optional[StrictStr] = Field(default=None, alias="tinType")
    recipient_second_name: Optional[StrictStr] = Field(default=None, alias="recipientSecondName")
    address: Optional[StrictStr] = None
    address2: Optional[StrictStr] = None
    city: Optional[StrictStr] = None
    state: Optional[StrictStr] = None
    zip: Optional[StrictStr] = None
    recipient_email: Optional[StrictStr] = Field(default=None, alias="recipientEmail")
    account_number: Optional[StrictStr] = Field(default=None, alias="accountNumber")
    office_code: Optional[StrictStr] = Field(default=None, alias="officeCode")
    recipient_non_us_province: Optional[StrictStr] = Field(default=None, alias="recipientNonUsProvince")
    country_code: Optional[StrictStr] = Field(default=None, alias="countryCode")
    federal_e_file: Optional[StrictBool] = Field(default=None, alias="federalEFile")
    postal_mail: Optional[StrictBool] = Field(default=None, alias="postalMail")
    state_e_file: Optional[StrictBool] = Field(default=None, alias="stateEFile")
    tin_match: Optional[StrictBool] = Field(default=None, alias="tinMatch")
    address_verification: Optional[StrictBool] = Field(default=None, alias="addressVerification")
    state_and_local_withholding: Optional[StateAndLocalWithholdingRequest] = Field(default=None, alias="stateAndLocalWithholding")
    __properties: ClassVar[List[str]] = ["issuerId", "referenceId", "recipientName", "recipientTin", "tinType", "recipientSecondName", "address", "address2", "city", "state", "zip", "recipientEmail", "accountNumber", "officeCode", "recipientNonUsProvince", "countryCode", "federalEFile", "postalMail", "stateEFile", "tinMatch", "addressVerification", "stateAndLocalWithholding"]

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
        """Create an instance of FormRequestCsvBase from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of state_and_local_withholding
        if self.state_and_local_withholding:
            _dict['stateAndLocalWithholding'] = self.state_and_local_withholding.to_dict()
        # set to None if issuer_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_id is None and "issuer_id" in self.model_fields_set:
            _dict['issuerId'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if recipient_name (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_name is None and "recipient_name" in self.model_fields_set:
            _dict['recipientName'] = None

        # set to None if address2 (nullable) is None
        # and model_fields_set contains the field
        if self.address2 is None and "address2" in self.model_fields_set:
            _dict['address2'] = None

        # set to None if recipient_email (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_email is None and "recipient_email" in self.model_fields_set:
            _dict['recipientEmail'] = None

        # set to None if account_number (nullable) is None
        # and model_fields_set contains the field
        if self.account_number is None and "account_number" in self.model_fields_set:
            _dict['accountNumber'] = None

        # set to None if office_code (nullable) is None
        # and model_fields_set contains the field
        if self.office_code is None and "office_code" in self.model_fields_set:
            _dict['officeCode'] = None

        # set to None if recipient_non_us_province (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_non_us_province is None and "recipient_non_us_province" in self.model_fields_set:
            _dict['recipientNonUsProvince'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FormRequestCsvBase from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "issuerId": obj.get("issuerId"),
            "referenceId": obj.get("referenceId"),
            "recipientName": obj.get("recipientName"),
            "recipientTin": obj.get("recipientTin"),
            "tinType": obj.get("tinType"),
            "recipientSecondName": obj.get("recipientSecondName"),
            "address": obj.get("address"),
            "address2": obj.get("address2"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "recipientEmail": obj.get("recipientEmail"),
            "accountNumber": obj.get("accountNumber"),
            "officeCode": obj.get("officeCode"),
            "recipientNonUsProvince": obj.get("recipientNonUsProvince"),
            "countryCode": obj.get("countryCode"),
            "federalEFile": obj.get("federalEFile"),
            "postalMail": obj.get("postalMail"),
            "stateEFile": obj.get("stateEFile"),
            "tinMatch": obj.get("tinMatch"),
            "addressVerification": obj.get("addressVerification"),
            "stateAndLocalWithholding": StateAndLocalWithholdingRequest.from_dict(obj["stateAndLocalWithholding"]) if obj.get("stateAndLocalWithholding") is not None else None
        })
        return _obj


