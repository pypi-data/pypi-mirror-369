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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from Avalara.SDK.models.A1099.V2.state_and_local_withholding_response import StateAndLocalWithholdingResponse
from Avalara.SDK.models.A1099.V2.state_efile_status_detail_response import StateEfileStatusDetailResponse
from Avalara.SDK.models.A1099.V2.status_detail import StatusDetail
from Avalara.SDK.models.A1099.V2.validation_error_response import ValidationErrorResponse
from typing import Optional, Set
from typing_extensions import Self

class Form1099BaseResponse(BaseModel):
    """
    Form1099BaseResponse
    """ # noqa: E501
    id: Annotated[str, Field(min_length=1, strict=True)] = Field(description="ID of the form")
    type: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Type of the form. Will be one of:  * 940  * 941  * 943  * 944  * 945  * 1042  * 1042-S  * 1095-B  * 1095-C  * 1097-BTC  * 1098  * 1098-C  * 1098-E  * 1098-Q  * 1098-T  * 3921  * 3922  * 5498  * 5498-ESA  * 5498-SA  * 1099-MISC  * 1099-A  * 1099-B  * 1099-C  * 1099-CAP  * 1099-DIV  * 1099-G  * 1099-INT  * 1099-K  * 1099-LS  * 1099-LTC  * 1099-NEC  * 1099-OID  * 1099-PATR  * 1099-Q  * 1099-R  * 1099-S  * 1099-SA  * T4A  * W-2  * W-2G  * 1099-HC")
    issuer_id: StrictInt = Field(description="Issuer ID", alias="issuerId")
    issuer_reference_id: Optional[StrictStr] = Field(default=None, description="Issuer Reference ID", alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, description="Issuer TIN", alias="issuerTin")
    tax_year: Optional[StrictInt] = Field(default=None, description="Tax year", alias="taxYear")
    federal_efile: StrictBool = Field(description="Boolean indicating that federal e-filing has been scheduled for this form", alias="federalEfile")
    federal_efile_status: Optional[StatusDetail] = Field(default=None, description="Federal e-file status", alias="federalEfileStatus")
    state_efile: StrictBool = Field(description="Boolean indicating that state e-filing has been scheduled for this form", alias="stateEfile")
    state_efile_status: Optional[List[StateEfileStatusDetailResponse]] = Field(default=None, description="State e-file status", alias="stateEfileStatus")
    postal_mail: StrictBool = Field(description="Boolean indicating that postal mailing to the recipient has been scheduled for this form", alias="postalMail")
    postal_mail_status: Optional[StatusDetail] = Field(default=None, description="Postal mail to recipient status", alias="postalMailStatus")
    tin_match: StrictBool = Field(description="Boolean indicating that TIN Matching has been scheduled for this form", alias="tinMatch")
    tin_match_status: Optional[StatusDetail] = Field(default=None, description="TIN Match status", alias="tinMatchStatus")
    address_verification: StrictBool = Field(description="Boolean indicating that address verification has been scheduled for this form", alias="addressVerification")
    address_verification_status: Optional[StatusDetail] = Field(default=None, description="Address verification status", alias="addressVerificationStatus")
    e_delivery_status: Optional[StatusDetail] = Field(default=None, description="EDelivery status", alias="eDeliveryStatus")
    reference_id: Optional[StrictStr] = Field(default=None, description="Reference ID", alias="referenceId")
    email: Optional[StrictStr] = Field(default=None, description="Recipient email address")
    tin_type: Optional[StrictStr] = Field(default=None, description="Type of TIN (Tax ID Number). Will be one of:  * SSN  * EIN  * ITIN  * ATIN", alias="tinType")
    tin: Optional[StrictStr] = Field(default=None, description="Recipient Tax ID Number")
    no_tin: Optional[StrictBool] = Field(default=None, description="Indicates whether the recipient has no TIN", alias="noTin")
    second_tin_notice: Optional[StrictBool] = Field(default=None, description="Second Tin Notice", alias="secondTinNotice")
    recipient_name: Optional[StrictStr] = Field(default=None, description="Recipient name", alias="recipientName")
    recipient_second_name: Optional[StrictStr] = Field(default=None, description="Recipient second name", alias="recipientSecondName")
    address: Optional[StrictStr] = Field(default=None, description="Address")
    address2: Optional[StrictStr] = Field(default=None, description="Address line 2")
    city: Optional[StrictStr] = Field(default=None, description="City")
    state: Optional[StrictStr] = Field(default=None, description="US state")
    zip: Optional[StrictStr] = Field(default=None, description="Zip/postal code")
    non_us_province: Optional[StrictStr] = Field(default=None, description="Foreign province", alias="nonUsProvince")
    country_code: Optional[StrictStr] = Field(default=None, description="Country code, as defined at https://www.irs.gov/e-file-providers/country-codes", alias="countryCode")
    account_number: Optional[StrictStr] = Field(default=None, description="Account Number", alias="accountNumber")
    office_code: Optional[StrictStr] = Field(default=None, description="Office Code", alias="officeCode")
    fatca_filing_requirement: Optional[StrictBool] = Field(default=None, description="FATCA filing requirement", alias="fatcaFilingRequirement")
    validation_errors: Optional[List[ValidationErrorResponse]] = Field(default=None, description="Validation errors", alias="validationErrors")
    created_at: Optional[datetime] = Field(default=None, description="Creation time", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="Update time", alias="updatedAt")
    state_and_local_withholding: Optional[StateAndLocalWithholdingResponse] = Field(default=None, alias="stateAndLocalWithholding")
    __properties: ClassVar[List[str]] = []

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
        """Create an instance of Form1099BaseResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "id",
            "federal_efile_status",
            "state_efile_status",
            "postal_mail_status",
            "tin_match_status",
            "address_verification_status",
            "e_delivery_status",
            "validation_errors",
            "created_at",
            "updated_at",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Form1099BaseResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
        })
        return _obj


