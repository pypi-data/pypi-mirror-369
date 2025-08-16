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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class CoveredIndividualReferenceResponse(BaseModel):
    """
    CoveredIndividualReferenceResponse
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Covered individual ID")
    first_name: Optional[StrictStr] = Field(default=None, description="Covered individual's first name", alias="firstName")
    middle_name: Optional[StrictStr] = Field(default=None, description="Covered individual's middle name", alias="middleName")
    last_name: Optional[StrictStr] = Field(default=None, description="Covered individual's last name", alias="lastName")
    name_suffix: Optional[StrictStr] = Field(default=None, description="Covered individual's name suffix", alias="nameSuffix")
    tin: Optional[StrictStr] = Field(default=None, description="Covered individual's TIN (SSN or ITIN)")
    birth_date: Optional[datetime] = Field(default=None, description="Covered individual's date of birth", alias="birthDate")
    covered_month0: Optional[StrictBool] = Field(default=None, description="Coverage indicator for all 12 months", alias="coveredMonth0")
    covered_month1: Optional[StrictBool] = Field(default=None, description="Coverage indicator for January", alias="coveredMonth1")
    covered_month2: Optional[StrictBool] = Field(default=None, description="Coverage indicator for February", alias="coveredMonth2")
    covered_month3: Optional[StrictBool] = Field(default=None, description="Coverage indicator for March", alias="coveredMonth3")
    covered_month4: Optional[StrictBool] = Field(default=None, description="Coverage indicator for April", alias="coveredMonth4")
    covered_month5: Optional[StrictBool] = Field(default=None, description="Coverage indicator for May", alias="coveredMonth5")
    covered_month6: Optional[StrictBool] = Field(default=None, description="Coverage indicator for June", alias="coveredMonth6")
    covered_month7: Optional[StrictBool] = Field(default=None, description="Coverage indicator for July", alias="coveredMonth7")
    covered_month8: Optional[StrictBool] = Field(default=None, description="Coverage indicator for August", alias="coveredMonth8")
    covered_month9: Optional[StrictBool] = Field(default=None, description="Coverage indicator for September", alias="coveredMonth9")
    covered_month10: Optional[StrictBool] = Field(default=None, description="Coverage indicator for October", alias="coveredMonth10")
    covered_month11: Optional[StrictBool] = Field(default=None, description="Coverage indicator for November", alias="coveredMonth11")
    covered_month12: Optional[StrictBool] = Field(default=None, description="Coverage indicator for December", alias="coveredMonth12")
    __properties: ClassVar[List[str]] = ["id", "firstName", "middleName", "lastName", "nameSuffix", "tin", "birthDate", "coveredMonth0", "coveredMonth1", "coveredMonth2", "coveredMonth3", "coveredMonth4", "coveredMonth5", "coveredMonth6", "coveredMonth7", "coveredMonth8", "coveredMonth9", "coveredMonth10", "coveredMonth11", "coveredMonth12"]

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
        """Create an instance of CoveredIndividualReferenceResponse from a JSON string"""
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
        # set to None if first_name (nullable) is None
        # and model_fields_set contains the field
        if self.first_name is None and "first_name" in self.model_fields_set:
            _dict['firstName'] = None

        # set to None if middle_name (nullable) is None
        # and model_fields_set contains the field
        if self.middle_name is None and "middle_name" in self.model_fields_set:
            _dict['middleName'] = None

        # set to None if last_name (nullable) is None
        # and model_fields_set contains the field
        if self.last_name is None and "last_name" in self.model_fields_set:
            _dict['lastName'] = None

        # set to None if name_suffix (nullable) is None
        # and model_fields_set contains the field
        if self.name_suffix is None and "name_suffix" in self.model_fields_set:
            _dict['nameSuffix'] = None

        # set to None if tin (nullable) is None
        # and model_fields_set contains the field
        if self.tin is None and "tin" in self.model_fields_set:
            _dict['tin'] = None

        # set to None if birth_date (nullable) is None
        # and model_fields_set contains the field
        if self.birth_date is None and "birth_date" in self.model_fields_set:
            _dict['birthDate'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CoveredIndividualReferenceResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "firstName": obj.get("firstName"),
            "middleName": obj.get("middleName"),
            "lastName": obj.get("lastName"),
            "nameSuffix": obj.get("nameSuffix"),
            "tin": obj.get("tin"),
            "birthDate": obj.get("birthDate"),
            "coveredMonth0": obj.get("coveredMonth0"),
            "coveredMonth1": obj.get("coveredMonth1"),
            "coveredMonth2": obj.get("coveredMonth2"),
            "coveredMonth3": obj.get("coveredMonth3"),
            "coveredMonth4": obj.get("coveredMonth4"),
            "coveredMonth5": obj.get("coveredMonth5"),
            "coveredMonth6": obj.get("coveredMonth6"),
            "coveredMonth7": obj.get("coveredMonth7"),
            "coveredMonth8": obj.get("coveredMonth8"),
            "coveredMonth9": obj.get("coveredMonth9"),
            "coveredMonth10": obj.get("coveredMonth10"),
            "coveredMonth11": obj.get("coveredMonth11"),
            "coveredMonth12": obj.get("coveredMonth12")
        })
        return _obj


