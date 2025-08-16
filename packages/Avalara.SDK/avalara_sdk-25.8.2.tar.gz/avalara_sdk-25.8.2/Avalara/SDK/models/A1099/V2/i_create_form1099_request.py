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
import json
import pprint
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from Avalara.SDK.models.A1099.V2.form1099_div_request import Form1099DivRequest
from Avalara.SDK.models.A1099.V2.form1099_k_request import Form1099KRequest
from Avalara.SDK.models.A1099.V2.form1099_misc_request import Form1099MiscRequest
from Avalara.SDK.models.A1099.V2.form1099_nec_request import Form1099NecRequest
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

ICREATEFORM1099REQUEST_ONE_OF_SCHEMAS = ["Form1099DivRequest", "Form1099KRequest", "Form1099MiscRequest", "Form1099NecRequest"]

class ICreateForm1099Request(BaseModel):
    """
    ICreateForm1099Request
    """
    # data type: Form1099DivRequest
    oneof_schema_1_validator: Optional[Form1099DivRequest] = None
    # data type: Form1099MiscRequest
    oneof_schema_2_validator: Optional[Form1099MiscRequest] = None
    # data type: Form1099KRequest
    oneof_schema_3_validator: Optional[Form1099KRequest] = None
    # data type: Form1099NecRequest
    oneof_schema_4_validator: Optional[Form1099NecRequest] = None
    actual_instance: Optional[Union[Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest]] = None
    one_of_schemas: Set[str] = { "Form1099DivRequest", "Form1099KRequest", "Form1099MiscRequest", "Form1099NecRequest" }

    model_config = ConfigDict(
        validate_assignment=True,
        protected_namespaces=(),
    )


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = ICreateForm1099Request.model_construct()
        error_messages = []
        match = 0
        # validate data type: Form1099DivRequest
        if not isinstance(v, Form1099DivRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099DivRequest`")
        else:
            match += 1
        # validate data type: Form1099MiscRequest
        if not isinstance(v, Form1099MiscRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099MiscRequest`")
        else:
            match += 1
        # validate data type: Form1099KRequest
        if not isinstance(v, Form1099KRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099KRequest`")
        else:
            match += 1
        # validate data type: Form1099NecRequest
        if not isinstance(v, Form1099NecRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099NecRequest`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in ICreateForm1099Request with oneOf schemas: Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in ICreateForm1099Request with oneOf schemas: Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: Union[str, Dict[str, Any]]) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into Form1099DivRequest
        try:
            instance.actual_instance = Form1099DivRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099MiscRequest
        try:
            instance.actual_instance = Form1099MiscRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099KRequest
        try:
            instance.actual_instance = Form1099KRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099NecRequest
        try:
            instance.actual_instance = Form1099NecRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into ICreateForm1099Request with oneOf schemas: Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into ICreateForm1099Request with oneOf schemas: Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        if hasattr(self.actual_instance, "to_json") and callable(self.actual_instance.to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Optional[Union[Dict[str, Any], Form1099DivRequest, Form1099KRequest, Form1099MiscRequest, Form1099NecRequest]]:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        if hasattr(self.actual_instance, "to_dict") and callable(self.actual_instance.to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())


