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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing_extensions import Annotated
from Avalara.SDK.models.A1099.V2.state_and_local_withholding_response import StateAndLocalWithholdingResponse
from Avalara.SDK.models.A1099.V2.state_efile_status_detail_response import StateEfileStatusDetailResponse
from Avalara.SDK.models.A1099.V2.status_detail import StatusDetail
from Avalara.SDK.models.A1099.V2.validation_error_response import ValidationErrorResponse
from typing import Optional, Set
from typing_extensions import Self

class Form1099RListItemResponse(BaseModel):
    """
    Form1099RListItemResponse
    """ # noqa: E501
    gross_distributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Gross distribution", alias="grossDistributions")
    taxable_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Taxable amount", alias="taxableAmount")
    taxable_amount_not_determined: Optional[StrictBool] = Field(default=None, description="Taxable amount not determined", alias="taxableAmountNotDetermined")
    total_distribution_indicator: Optional[StrictBool] = Field(default=None, description="Total distribution", alias="totalDistributionIndicator")
    capital_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Capital gain (included in Box 2a)", alias="capitalGain")
    fed_income_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Federal income tax withheld", alias="fedIncomeTaxWithheld")
    employee_contributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Employee contributions/Designated Roth contributions or insurance premiums", alias="employeeContributions")
    net_unrealized_appreciation: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Net unrealized appreciation in employer's securities", alias="netUnrealizedAppreciation")
    distribution_code_required: Optional[StrictStr] = Field(default=None, description="Distribution code", alias="distributionCodeRequired")
    distribution_code_optional: Optional[StrictStr] = Field(default=None, description="Second distribution code", alias="distributionCodeOptional")
    ira_sep_simple_indicator: Optional[StrictBool] = Field(default=None, description="IRA/SEP/SIMPLE", alias="iraSepSimpleIndicator")
    total_ira_sep_simple_distribution: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Traditional IRA/SEP/SIMPLE or Roth conversion amount", alias="totalIraSepSimpleDistribution")
    other: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Other amount")
    other_percent: Optional[StrictStr] = Field(default=None, description="Other percentage", alias="otherPercent")
    percentage_total_distribution: Optional[StrictStr] = Field(default=None, description="Total distribution percentage", alias="percentageTotalDistribution")
    total_employee_contributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Total employee contributions", alias="totalEmployeeContributions")
    amount_allocable_to_irr: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount allocable to IRR within 5 years", alias="amountAllocableToIrr")
    first_year_designated_roth_contrib: Optional[StrictStr] = Field(default=None, description="First year of designated Roth contribution", alias="firstYearDesignatedRothContrib")
    date_of_payment: Optional[StrictStr] = Field(default=None, description="Date of payment", alias="dateOfPayment")
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
    __properties: ClassVar[List[str]] = ["id", "type", "issuerId", "issuerReferenceId", "issuerTin", "taxYear", "federalEfile", "federalEfileStatus", "stateEfile", "stateEfileStatus", "postalMail", "postalMailStatus", "tinMatch", "tinMatchStatus", "addressVerification", "addressVerificationStatus", "eDeliveryStatus", "referenceId", "email", "tinType", "tin", "noTin", "secondTinNotice", "recipientName", "recipientSecondName", "address", "address2", "city", "state", "zip", "nonUsProvince", "countryCode", "accountNumber", "officeCode", "fatcaFilingRequirement", "validationErrors", "createdAt", "updatedAt", "stateAndLocalWithholding"]

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
        """Create an instance of Form1099RListItemResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of federal_efile_status
        if self.federal_efile_status:
            _dict['federalEfileStatus'] = self.federal_efile_status.to_dict()
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
        # override the default output from pydantic by calling `to_dict()` of e_delivery_status
        if self.e_delivery_status:
            _dict['eDeliveryStatus'] = self.e_delivery_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in validation_errors (list)
        _items = []
        if self.validation_errors:
            for _item in self.validation_errors:
                if _item:
                    _items.append(_item.to_dict())
            _dict['validationErrors'] = _items
        # override the default output from pydantic by calling `to_dict()` of state_and_local_withholding
        if self.state_and_local_withholding:
            _dict['stateAndLocalWithholding'] = self.state_and_local_withholding.to_dict()
        # set to None if issuer_reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_reference_id is None and "issuer_reference_id" in self.model_fields_set:
            _dict['issuerReferenceId'] = None

        # set to None if issuer_tin (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_tin is None and "issuer_tin" in self.model_fields_set:
            _dict['issuerTin'] = None

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

        # set to None if e_delivery_status (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_status is None and "e_delivery_status" in self.model_fields_set:
            _dict['eDeliveryStatus'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if tin_type (nullable) is None
        # and model_fields_set contains the field
        if self.tin_type is None and "tin_type" in self.model_fields_set:
            _dict['tinType'] = None

        # set to None if tin (nullable) is None
        # and model_fields_set contains the field
        if self.tin is None and "tin" in self.model_fields_set:
            _dict['tin'] = None

        # set to None if second_tin_notice (nullable) is None
        # and model_fields_set contains the field
        if self.second_tin_notice is None and "second_tin_notice" in self.model_fields_set:
            _dict['secondTinNotice'] = None

        # set to None if recipient_name (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_name is None and "recipient_name" in self.model_fields_set:
            _dict['recipientName'] = None

        # set to None if recipient_second_name (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_second_name is None and "recipient_second_name" in self.model_fields_set:
            _dict['recipientSecondName'] = None

        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

        # set to None if address2 (nullable) is None
        # and model_fields_set contains the field
        if self.address2 is None and "address2" in self.model_fields_set:
            _dict['address2'] = None

        # set to None if city (nullable) is None
        # and model_fields_set contains the field
        if self.city is None and "city" in self.model_fields_set:
            _dict['city'] = None

        # set to None if state (nullable) is None
        # and model_fields_set contains the field
        if self.state is None and "state" in self.model_fields_set:
            _dict['state'] = None

        # set to None if zip (nullable) is None
        # and model_fields_set contains the field
        if self.zip is None and "zip" in self.model_fields_set:
            _dict['zip'] = None

        # set to None if non_us_province (nullable) is None
        # and model_fields_set contains the field
        if self.non_us_province is None and "non_us_province" in self.model_fields_set:
            _dict['nonUsProvince'] = None

        # set to None if country_code (nullable) is None
        # and model_fields_set contains the field
        if self.country_code is None and "country_code" in self.model_fields_set:
            _dict['countryCode'] = None

        # set to None if account_number (nullable) is None
        # and model_fields_set contains the field
        if self.account_number is None and "account_number" in self.model_fields_set:
            _dict['accountNumber'] = None

        # set to None if office_code (nullable) is None
        # and model_fields_set contains the field
        if self.office_code is None and "office_code" in self.model_fields_set:
            _dict['officeCode'] = None

        # set to None if fatca_filing_requirement (nullable) is None
        # and model_fields_set contains the field
        if self.fatca_filing_requirement is None and "fatca_filing_requirement" in self.model_fields_set:
            _dict['fatcaFilingRequirement'] = None

        # set to None if validation_errors (nullable) is None
        # and model_fields_set contains the field
        if self.validation_errors is None and "validation_errors" in self.model_fields_set:
            _dict['validationErrors'] = None

        # set to None if state_and_local_withholding (nullable) is None
        # and model_fields_set contains the field
        if self.state_and_local_withholding is None and "state_and_local_withholding" in self.model_fields_set:
            _dict['stateAndLocalWithholding'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Form1099RListItemResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "type": obj.get("type"),
            "issuerId": obj.get("issuerId"),
            "issuerReferenceId": obj.get("issuerReferenceId"),
            "issuerTin": obj.get("issuerTin"),
            "taxYear": obj.get("taxYear"),
            "federalEfile": obj.get("federalEfile"),
            "federalEfileStatus": StatusDetail.from_dict(obj["federalEfileStatus"]) if obj.get("federalEfileStatus") is not None else None,
            "stateEfile": obj.get("stateEfile"),
            "stateEfileStatus": [StateEfileStatusDetailResponse.from_dict(_item) for _item in obj["stateEfileStatus"]] if obj.get("stateEfileStatus") is not None else None,
            "postalMail": obj.get("postalMail"),
            "postalMailStatus": StatusDetail.from_dict(obj["postalMailStatus"]) if obj.get("postalMailStatus") is not None else None,
            "tinMatch": obj.get("tinMatch"),
            "tinMatchStatus": StatusDetail.from_dict(obj["tinMatchStatus"]) if obj.get("tinMatchStatus") is not None else None,
            "addressVerification": obj.get("addressVerification"),
            "addressVerificationStatus": StatusDetail.from_dict(obj["addressVerificationStatus"]) if obj.get("addressVerificationStatus") is not None else None,
            "eDeliveryStatus": StatusDetail.from_dict(obj["eDeliveryStatus"]) if obj.get("eDeliveryStatus") is not None else None,
            "referenceId": obj.get("referenceId"),
            "email": obj.get("email"),
            "tinType": obj.get("tinType"),
            "tin": obj.get("tin"),
            "noTin": obj.get("noTin"),
            "secondTinNotice": obj.get("secondTinNotice"),
            "recipientName": obj.get("recipientName"),
            "recipientSecondName": obj.get("recipientSecondName"),
            "address": obj.get("address"),
            "address2": obj.get("address2"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "nonUsProvince": obj.get("nonUsProvince"),
            "countryCode": obj.get("countryCode"),
            "accountNumber": obj.get("accountNumber"),
            "officeCode": obj.get("officeCode"),
            "fatcaFilingRequirement": obj.get("fatcaFilingRequirement"),
            "validationErrors": [ValidationErrorResponse.from_dict(_item) for _item in obj["validationErrors"]] if obj.get("validationErrors") is not None else None,
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt"),
            "stateAndLocalWithholding": StateAndLocalWithholdingResponse.from_dict(obj["stateAndLocalWithholding"]) if obj.get("stateAndLocalWithholding") is not None else None
        })
        return _obj


