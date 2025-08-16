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
from typing import Optional, Set
from typing_extensions import Self

class IssuerResponse(BaseModel):
    """
    IssuerResponse
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Unique identifier set when the record is created")
    name: Optional[StrictStr] = Field(default=None, description="Legal name, not DBA")
    name_dba: Optional[StrictStr] = Field(default=None, description="Optional DBA name or continuation of a long legal name", alias="nameDba")
    tin: Optional[StrictStr] = Field(default=None, description="Tax identification number")
    reference_id: Optional[StrictStr] = Field(default=None, description="Optional identifier for your reference, never shown to any agency or recipient.  We will also prefix download filenames with this value, if present.  Can only include letters, numbers, dashes, underscores and spaces.", alias="referenceId")
    telephone: Optional[StrictStr] = Field(default=None, description="Telephone number")
    tax_year: Optional[StrictInt] = Field(default=None, description="Tax year", alias="taxYear")
    country_code: Optional[StrictStr] = Field(default=None, description="If there is a transfer agent, use the address of the transfer agent.", alias="countryCode")
    email: Optional[StrictStr] = Field(default=None, description="Email address")
    address: Optional[StrictStr] = Field(default=None, description="Address")
    city: Optional[StrictStr] = Field(default=None, description="City")
    state: Optional[StrictStr] = Field(default=None, description="State")
    zip: Optional[StrictStr] = Field(default=None, description="Zip code")
    foreign_province: Optional[StrictStr] = Field(default=None, description="Foreign province", alias="foreignProvince")
    transfer_agent_name: Optional[StrictStr] = Field(default=None, description="Transfer Agent's Name", alias="transferAgentName")
    last_filing: Optional[StrictBool] = Field(default=None, description="Last year of filing for this payer", alias="lastFiling")
    created_at: Optional[datetime] = Field(default=None, description="Date time when the issuer was created", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="Date time when the issuer was updated", alias="updatedAt")
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
        """Create an instance of IssuerResponse from a JSON string"""
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
        """
        excluded_fields: Set[str] = set([
            "id",
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
        """Create an instance of IssuerResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
        })
        return _obj


