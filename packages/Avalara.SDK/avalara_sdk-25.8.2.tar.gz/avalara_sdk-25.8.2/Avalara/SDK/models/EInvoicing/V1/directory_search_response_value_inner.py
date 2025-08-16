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

    Avalara E-Invoicing API
    An API that supports sending data for an E-Invoicing compliance use-case. 

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

from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.EInvoicing.V1.directory_search_response_value_inner_addresses_inner import DirectorySearchResponseValueInnerAddressesInner
from Avalara.SDK.models.EInvoicing.V1.directory_search_response_value_inner_identifiers_inner import DirectorySearchResponseValueInnerIdentifiersInner
from Avalara.SDK.models.EInvoicing.V1.directory_search_response_value_inner_supported_document_types_inner import DirectorySearchResponseValueInnerSupportedDocumentTypesInner
from typing import Optional, Set
from typing_extensions import Self

class DirectorySearchResponseValueInner(BaseModel):
    """
    DirectorySearchResponseValueInner
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Avalara unique ID of the participant in the directory.")
    name: Optional[StrictStr] = Field(default=None, description="Name of the participant (typically, the name of the business entity).")
    network: Optional[StrictStr] = Field(default=None, description="The network where the participant is present.")
    registration_date: Optional[date] = Field(default=None, description="Registration date of the participant if available", alias="registrationDate")
    identifiers: Optional[List[DirectorySearchResponseValueInnerIdentifiersInner]] = None
    addresses: Optional[List[DirectorySearchResponseValueInnerAddressesInner]] = None
    supported_document_types: Optional[List[DirectorySearchResponseValueInnerSupportedDocumentTypesInner]] = Field(default=None, alias="supportedDocumentTypes")
    __properties: ClassVar[List[str]] = ["id", "name", "network", "registrationDate", "identifiers", "addresses", "supportedDocumentTypes"]

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
        """Create an instance of DirectorySearchResponseValueInner from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in identifiers (list)
        _items = []
        if self.identifiers:
            for _item in self.identifiers:
                if _item:
                    _items.append(_item.to_dict())
            _dict['identifiers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in addresses (list)
        _items = []
        if self.addresses:
            for _item in self.addresses:
                if _item:
                    _items.append(_item.to_dict())
            _dict['addresses'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in supported_document_types (list)
        _items = []
        if self.supported_document_types:
            for _item in self.supported_document_types:
                if _item:
                    _items.append(_item.to_dict())
            _dict['supportedDocumentTypes'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DirectorySearchResponseValueInner from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "network": obj.get("network"),
            "registrationDate": obj.get("registrationDate"),
            "identifiers": [DirectorySearchResponseValueInnerIdentifiersInner.from_dict(_item) for _item in obj["identifiers"]] if obj.get("identifiers") is not None else None,
            "addresses": [DirectorySearchResponseValueInnerAddressesInner.from_dict(_item) for _item in obj["addresses"]] if obj.get("addresses") is not None else None,
            "supportedDocumentTypes": [DirectorySearchResponseValueInnerSupportedDocumentTypesInner.from_dict(_item) for _item in obj["supportedDocumentTypes"]] if obj.get("supportedDocumentTypes") is not None else None
        })
        return _obj


