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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.A1099.V2.covered_individual_request import CoveredIndividualRequest
from Avalara.SDK.models.A1099.V2.offer_and_coverage_request import OfferAndCoverageRequest
from Avalara.SDK.models.A1099.V2.state_and_local_withholding_request import StateAndLocalWithholdingRequest
from typing import Optional, Set
from typing_extensions import Self

class Form1095CListItem(BaseModel):
    """
    Form1095CListItem
    """ # noqa: E501
    employee_first_name: Optional[StrictStr] = Field(default=None, description="Employee's first name", alias="employeeFirstName")
    employee_middle_name: Optional[StrictStr] = Field(default=None, description="Employee's middle name", alias="employeeMiddleName")
    employee_last_name: Optional[StrictStr] = Field(default=None, description="Employee's last name", alias="employeeLastName")
    employee_name_suffix: Optional[StrictStr] = Field(default=None, description="Employee's name suffix", alias="employeeNameSuffix")
    recipient_date_of_birth: Optional[datetime] = Field(default=None, description="Recipient's date of birth", alias="recipientDateOfBirth")
    plan_start_month: Optional[StrictStr] = Field(default=None, description="Plan start month", alias="planStartMonth")
    offer_and_coverages: Optional[List[OfferAndCoverageRequest]] = Field(default=None, description="Offer and coverage information", alias="offerAndCoverages")
    employer_provided_si_coverage: Optional[StrictBool] = Field(default=None, description="Employer provided self-insured coverage", alias="employerProvidedSiCoverage")
    covered_individuals: Optional[List[CoveredIndividualRequest]] = Field(default=None, description="Covered individuals information", alias="coveredIndividuals")
    issuer_reference_id: Optional[StrictStr] = Field(default=None, description="Issuer Reference ID. One of `issuerReferenceId` or `issuerTin` is required.", alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, description="Issuer TIN. One of `issuerReferenceId` or `issuerTin` is required.", alias="issuerTin")
    tax_year: StrictInt = Field(description="Tax year", alias="taxYear")
    issuer_id: Optional[StrictStr] = Field(default=None, description="Issuer ID", alias="issuerId")
    reference_id: Optional[StrictStr] = Field(default=None, description="Reference ID", alias="referenceId")
    recipient_tin: Optional[StrictStr] = Field(default=None, description="Recipient Tax ID Number", alias="recipientTin")
    recipient_name: Optional[StrictStr] = Field(default=None, description="Recipient name", alias="recipientName")
    tin_type: Optional[StrictStr] = Field(default=None, description="Type of TIN (Tax ID Number). Will be one of:  * SSN  * EIN  * ITIN  * ATIN", alias="tinType")
    recipient_second_name: Optional[StrictStr] = Field(default=None, description="Recipient second name", alias="recipientSecondName")
    address: Optional[StrictStr] = Field(default=None, description="Address")
    address2: Optional[StrictStr] = Field(default=None, description="Address line 2")
    city: Optional[StrictStr] = Field(default=None, description="City")
    state: Optional[StrictStr] = Field(default=None, description="US state. Required if CountryCode is \"US\".")
    zip: Optional[StrictStr] = Field(default=None, description="Zip/postal code")
    email: Optional[StrictStr] = Field(default=None, description="Recipient email address")
    account_number: Optional[StrictStr] = Field(default=None, description="Account number", alias="accountNumber")
    office_code: Optional[StrictStr] = Field(default=None, description="Office code", alias="officeCode")
    non_us_province: Optional[StrictStr] = Field(default=None, description="Foreign province", alias="nonUsProvince")
    country_code: Optional[StrictStr] = Field(default=None, description="Country code, as defined at https://www.irs.gov/e-file-providers/country-codes", alias="countryCode")
    federal_e_file: Optional[StrictBool] = Field(default=None, description="Boolean indicating that federal e-filing should be scheduled for this form", alias="federalEFile")
    postal_mail: Optional[StrictBool] = Field(default=None, description="Boolean indicating that postal mailing to the recipient should be scheduled for this form", alias="postalMail")
    state_e_file: Optional[StrictBool] = Field(default=None, description="Boolean indicating that state e-filing should be scheduled for this form", alias="stateEFile")
    tin_match: Optional[StrictBool] = Field(default=None, description="Boolean indicating that TIN Matching should be scheduled for this form", alias="tinMatch")
    no_tin: Optional[StrictBool] = Field(default=None, description="Indicates whether the recipient has no TIN", alias="noTin")
    second_tin_notice: Optional[StrictBool] = Field(default=None, description="Second TIN notice in three years", alias="secondTinNotice")
    fatca_filing_requirement: Optional[StrictBool] = Field(default=None, description="Fatca filing requirement", alias="fatcaFilingRequirement")
    address_verification: Optional[StrictBool] = Field(default=None, description="Boolean indicating that address verification should be scheduled for this form", alias="addressVerification")
    state_and_local_withholding: Optional[StateAndLocalWithholdingRequest] = Field(default=None, description="State and local withholding information", alias="stateAndLocalWithholding")
    __properties: ClassVar[List[str]] = ["issuerReferenceId", "issuerTin", "taxYear", "issuerId", "referenceId", "recipientTin", "recipientName", "tinType", "recipientSecondName", "address", "address2", "city", "state", "zip", "email", "accountNumber", "officeCode", "nonUsProvince", "countryCode", "federalEFile", "postalMail", "stateEFile", "tinMatch", "noTin", "secondTinNotice", "fatcaFilingRequirement", "addressVerification", "stateAndLocalWithholding"]

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
        """Create an instance of Form1095CListItem from a JSON string"""
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
        # set to None if issuer_reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_reference_id is None and "issuer_reference_id" in self.model_fields_set:
            _dict['issuerReferenceId'] = None

        # set to None if issuer_tin (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_tin is None and "issuer_tin" in self.model_fields_set:
            _dict['issuerTin'] = None

        # set to None if issuer_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_id is None and "issuer_id" in self.model_fields_set:
            _dict['issuerId'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if recipient_tin (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_tin is None and "recipient_tin" in self.model_fields_set:
            _dict['recipientTin'] = None

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

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if account_number (nullable) is None
        # and model_fields_set contains the field
        if self.account_number is None and "account_number" in self.model_fields_set:
            _dict['accountNumber'] = None

        # set to None if office_code (nullable) is None
        # and model_fields_set contains the field
        if self.office_code is None and "office_code" in self.model_fields_set:
            _dict['officeCode'] = None

        # set to None if non_us_province (nullable) is None
        # and model_fields_set contains the field
        if self.non_us_province is None and "non_us_province" in self.model_fields_set:
            _dict['nonUsProvince'] = None

        # set to None if country_code (nullable) is None
        # and model_fields_set contains the field
        if self.country_code is None and "country_code" in self.model_fields_set:
            _dict['countryCode'] = None

        # set to None if second_tin_notice (nullable) is None
        # and model_fields_set contains the field
        if self.second_tin_notice is None and "second_tin_notice" in self.model_fields_set:
            _dict['secondTinNotice'] = None

        # set to None if state_and_local_withholding (nullable) is None
        # and model_fields_set contains the field
        if self.state_and_local_withholding is None and "state_and_local_withholding" in self.model_fields_set:
            _dict['stateAndLocalWithholding'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Form1095CListItem from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "issuerReferenceId": obj.get("issuerReferenceId"),
            "issuerTin": obj.get("issuerTin"),
            "taxYear": obj.get("taxYear"),
            "issuerId": obj.get("issuerId"),
            "referenceId": obj.get("referenceId"),
            "recipientTin": obj.get("recipientTin"),
            "recipientName": obj.get("recipientName"),
            "tinType": obj.get("tinType"),
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
            "fatcaFilingRequirement": obj.get("fatcaFilingRequirement"),
            "addressVerification": obj.get("addressVerification"),
            "stateAndLocalWithholding": StateAndLocalWithholdingRequest.from_dict(obj["stateAndLocalWithholding"]) if obj.get("stateAndLocalWithholding") is not None else None
        })
        return _obj


