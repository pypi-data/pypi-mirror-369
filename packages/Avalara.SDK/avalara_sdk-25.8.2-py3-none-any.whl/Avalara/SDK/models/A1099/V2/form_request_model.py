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
@version    25.7.0
@link       https://github.com/avadev/AvaTax-REST-V3-Python-SDK
"""

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class FormRequestModel(BaseModel):
    """
    FormRequestModel
    """ # noqa: E501
    id: Optional[StrictStr] = None
    type: Optional[StrictStr] = None
    form_type: Optional[StrictStr] = Field(default=None, description="\"W9\" is currently the only supported value", alias="formType")
    company_id: Optional[StrictInt] = Field(default=None, description="Track1099's ID of your company, found in the W-9 UI", alias="companyId")
    company_name: Optional[StrictStr] = Field(default=None, description="Name of your company, set in the W-9 UI", alias="companyName")
    company_email: Optional[StrictStr] = Field(default=None, description="Contact email of your company, set in the W-9 UI", alias="companyEmail")
    reference_id: Optional[StrictStr] = Field(default=None, description="Your internal identifier for the vendor from whom you are requesting a form", alias="referenceId")
    signed_at: Optional[datetime] = Field(default=None, description="The timestamp this vendor (identified by your ReferenceId) last signed a complete W-9, null if you did not include a ReferenceId or the vendor has not yet signed a W-9 in Track1099", alias="signedAt")
    tin_match_status: Optional[StrictStr] = Field(default=None, description="Result of IRS TIN match query for name and TIN in the last signed form, null if signed_at is null", alias="tinMatchStatus")
    expires_at: Optional[datetime] = Field(default=None, description="Timestamp when this FormRequest will expire, ttl (or 3600) seconds from creation", alias="expiresAt")
    signed_pdf: Optional[StrictStr] = Field(default=None, description="URL of PDF representation of just-signed form, otherwise null. Integrations may use this value to offer a \"download for your records\" function after a vendor completes and signs a form. Link expires at the same time as this FormRequest. Treat the format of this URL as opaque and expect it to change in the future.", alias="signedPdf")
    __properties: ClassVar[List[str]] = []

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['FormRequest']):
            raise ValueError("must be one of enum values ('FormRequest')")
        return value

    @field_validator('form_type')
    def form_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['W9']):
            raise ValueError("must be one of enum values ('W9')")
        return value

    @field_validator('tin_match_status')
    def tin_match_status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['None', 'Matched']):
            raise ValueError("must be one of enum values ('None', 'Matched')")
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
        """Create an instance of FormRequestModel from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FormRequestModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
        })
        return _obj


