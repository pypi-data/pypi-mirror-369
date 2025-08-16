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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class Attribute(BaseModel):
    """
    Attribute
    """ # noqa: E501
    dry_run: Optional[StrictBool] = Field(default=None, alias="dryRun")
    upsert: Optional[StrictBool] = None
    status: Optional[StrictStr] = None
    error_message: Optional[StrictStr] = Field(default=None, alias="errorMessage")
    total_processed: Optional[StrictInt] = Field(default=None, alias="totalProcessed")
    total_rows: Optional[StrictInt] = Field(default=None, alias="totalRows")
    updated_valid: Optional[StrictInt] = Field(default=None, alias="updatedValid")
    updated_no_email: Optional[StrictInt] = Field(default=None, alias="updatedNoEmail")
    updated_invalid: Optional[StrictInt] = Field(default=None, alias="updatedInvalid")
    skipped_duplicate: Optional[StrictInt] = Field(default=None, alias="skippedDuplicate")
    skipped_invalid: Optional[StrictInt] = Field(default=None, alias="skippedInvalid")
    skipped_multiple_matches: Optional[StrictInt] = Field(default=None, alias="skippedMultipleMatches")
    not_found: Optional[StrictInt] = Field(default=None, alias="notFound")
    created_invalid: Optional[StrictInt] = Field(default=None, alias="createdInvalid")
    created_no_email: Optional[StrictInt] = Field(default=None, alias="createdNoEmail")
    created_valid: Optional[StrictInt] = Field(default=None, alias="createdValid")
    __properties: ClassVar[List[str]] = ["dryRun", "upsert", "status", "errorMessage", "totalProcessed", "totalRows", "updatedValid", "updatedNoEmail", "updatedInvalid", "skippedDuplicate", "skippedInvalid", "skippedMultipleMatches", "notFound", "createdInvalid", "createdNoEmail", "createdValid"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['InProgress', 'Success', 'Failed']):
            raise ValueError("must be one of enum values ('InProgress', 'Success', 'Failed')")
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
        """Create an instance of Attribute from a JSON string"""
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
        """Create an instance of Attribute from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "dryRun": obj.get("dryRun"),
            "upsert": obj.get("upsert"),
            "status": obj.get("status"),
            "errorMessage": obj.get("errorMessage"),
            "totalProcessed": obj.get("totalProcessed"),
            "totalRows": obj.get("totalRows"),
            "updatedValid": obj.get("updatedValid"),
            "updatedNoEmail": obj.get("updatedNoEmail"),
            "updatedInvalid": obj.get("updatedInvalid"),
            "skippedDuplicate": obj.get("skippedDuplicate"),
            "skippedInvalid": obj.get("skippedInvalid"),
            "skippedMultipleMatches": obj.get("skippedMultipleMatches"),
            "notFound": obj.get("notFound"),
            "createdInvalid": obj.get("createdInvalid"),
            "createdNoEmail": obj.get("createdNoEmail"),
            "createdValid": obj.get("createdValid")
        })
        return _obj


