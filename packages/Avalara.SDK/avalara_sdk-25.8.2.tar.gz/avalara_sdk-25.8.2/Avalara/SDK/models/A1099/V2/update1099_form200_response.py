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
from Avalara.SDK.models.A1099.V2.form1042_s_response import Form1042SResponse
from Avalara.SDK.models.A1099.V2.form1095_b_response import Form1095BResponse
from Avalara.SDK.models.A1099.V2.form1099_div_response import Form1099DivResponse
from Avalara.SDK.models.A1099.V2.form1099_int_response import Form1099IntResponse
from Avalara.SDK.models.A1099.V2.form1099_k_response import Form1099KResponse
from Avalara.SDK.models.A1099.V2.form1099_misc_response import Form1099MiscResponse
from Avalara.SDK.models.A1099.V2.form1099_nec_response import Form1099NecResponse
from Avalara.SDK.models.A1099.V2.form1099_r_response import Form1099RResponse
from Avalara.SDK.models.A1099.V2.form_response_base import FormResponseBase
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

UPDATE1099FORM200RESPONSE_ONE_OF_SCHEMAS = ["Form1042SResponse", "Form1095BResponse", "Form1099DivResponse", "Form1099IntResponse", "Form1099KResponse", "Form1099MiscResponse", "Form1099NecResponse", "Form1099RResponse", "FormResponseBase"]

class Update1099Form200Response(BaseModel):
    """
    Update1099Form200Response
    """
    # data type: FormResponseBase
    oneof_schema_1_validator: Optional[FormResponseBase] = None
    # data type: Form1042SResponse
    oneof_schema_2_validator: Optional[Form1042SResponse] = None
    # data type: Form1095BResponse
    oneof_schema_3_validator: Optional[Form1095BResponse] = None
    # data type: Form1099DivResponse
    oneof_schema_4_validator: Optional[Form1099DivResponse] = None
    # data type: Form1099IntResponse
    oneof_schema_5_validator: Optional[Form1099IntResponse] = None
    # data type: Form1099KResponse
    oneof_schema_6_validator: Optional[Form1099KResponse] = None
    # data type: Form1099MiscResponse
    oneof_schema_7_validator: Optional[Form1099MiscResponse] = None
    # data type: Form1099NecResponse
    oneof_schema_8_validator: Optional[Form1099NecResponse] = None
    # data type: Form1099RResponse
    oneof_schema_9_validator: Optional[Form1099RResponse] = None
    actual_instance: Optional[Union[Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase]] = None
    one_of_schemas: Set[str] = { "Form1042SResponse", "Form1095BResponse", "Form1099DivResponse", "Form1099IntResponse", "Form1099KResponse", "Form1099MiscResponse", "Form1099NecResponse", "Form1099RResponse", "FormResponseBase" }

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
        instance = Update1099Form200Response.model_construct()
        error_messages = []
        match = 0
        # validate data type: FormResponseBase
        if not isinstance(v, FormResponseBase):
            error_messages.append(f"Error! Input type `{type(v)}` is not `FormResponseBase`")
        else:
            match += 1
        # validate data type: Form1042SResponse
        if not isinstance(v, Form1042SResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1042SResponse`")
        else:
            match += 1
        # validate data type: Form1095BResponse
        if not isinstance(v, Form1095BResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1095BResponse`")
        else:
            match += 1
        # validate data type: Form1099DivResponse
        if not isinstance(v, Form1099DivResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099DivResponse`")
        else:
            match += 1
        # validate data type: Form1099IntResponse
        if not isinstance(v, Form1099IntResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099IntResponse`")
        else:
            match += 1
        # validate data type: Form1099KResponse
        if not isinstance(v, Form1099KResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099KResponse`")
        else:
            match += 1
        # validate data type: Form1099MiscResponse
        if not isinstance(v, Form1099MiscResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099MiscResponse`")
        else:
            match += 1
        # validate data type: Form1099NecResponse
        if not isinstance(v, Form1099NecResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099NecResponse`")
        else:
            match += 1
        # validate data type: Form1099RResponse
        if not isinstance(v, Form1099RResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099RResponse`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in Update1099Form200Response with oneOf schemas: Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in Update1099Form200Response with oneOf schemas: Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase. Details: " + ", ".join(error_messages))
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

        # deserialize data into FormResponseBase
        try:
            instance.actual_instance = FormResponseBase.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1042SResponse
        try:
            instance.actual_instance = Form1042SResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1095BResponse
        try:
            instance.actual_instance = Form1095BResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099DivResponse
        try:
            instance.actual_instance = Form1099DivResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099IntResponse
        try:
            instance.actual_instance = Form1099IntResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099KResponse
        try:
            instance.actual_instance = Form1099KResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099MiscResponse
        try:
            instance.actual_instance = Form1099MiscResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099NecResponse
        try:
            instance.actual_instance = Form1099NecResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099RResponse
        try:
            instance.actual_instance = Form1099RResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into Update1099Form200Response with oneOf schemas: Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into Update1099Form200Response with oneOf schemas: Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase. Details: " + ", ".join(error_messages))
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

    def to_dict(self) -> Optional[Union[Dict[str, Any], Form1042SResponse, Form1095BResponse, Form1099DivResponse, Form1099IntResponse, Form1099KResponse, Form1099MiscResponse, Form1099NecResponse, Form1099RResponse, FormResponseBase]]:
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


