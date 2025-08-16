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
from Avalara.SDK.models.A1099.V2.form1042_s_list_item_response import Form1042SListItemResponse
from Avalara.SDK.models.A1099.V2.form1095_b_list_item_response import Form1095BListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_base_response import Form1099BaseResponse
from Avalara.SDK.models.A1099.V2.form1099_div_list_item_response import Form1099DivListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_int_list_item_response import Form1099IntListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_k_list_item_response import Form1099KListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_misc_list_item_response import Form1099MiscListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_nec_list_item_response import Form1099NecListItemResponse
from Avalara.SDK.models.A1099.V2.form1099_r_list_item_response import Form1099RListItemResponse
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

FORM1099LISTRESPONSEVALUEINNER_ONE_OF_SCHEMAS = ["Form1042SListItemResponse", "Form1095BListItemResponse", "Form1099BaseResponse", "Form1099DivListItemResponse", "Form1099IntListItemResponse", "Form1099KListItemResponse", "Form1099MiscListItemResponse", "Form1099NecListItemResponse", "Form1099RListItemResponse"]

class Form1099ListResponseValueInner(BaseModel):
    """
    Form1099ListResponseValueInner
    """
    # data type: Form1099BaseResponse
    oneof_schema_1_validator: Optional[Form1099BaseResponse] = None
    # data type: Form1042SListItemResponse
    oneof_schema_2_validator: Optional[Form1042SListItemResponse] = None
    # data type: Form1095BListItemResponse
    oneof_schema_3_validator: Optional[Form1095BListItemResponse] = None
    # data type: Form1099DivListItemResponse
    oneof_schema_4_validator: Optional[Form1099DivListItemResponse] = None
    # data type: Form1099IntListItemResponse
    oneof_schema_5_validator: Optional[Form1099IntListItemResponse] = None
    # data type: Form1099KListItemResponse
    oneof_schema_6_validator: Optional[Form1099KListItemResponse] = None
    # data type: Form1099MiscListItemResponse
    oneof_schema_7_validator: Optional[Form1099MiscListItemResponse] = None
    # data type: Form1099NecListItemResponse
    oneof_schema_8_validator: Optional[Form1099NecListItemResponse] = None
    # data type: Form1099RListItemResponse
    oneof_schema_9_validator: Optional[Form1099RListItemResponse] = None
    actual_instance: Optional[Union[Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse]] = None
    one_of_schemas: Set[str] = { "Form1042SListItemResponse", "Form1095BListItemResponse", "Form1099BaseResponse", "Form1099DivListItemResponse", "Form1099IntListItemResponse", "Form1099KListItemResponse", "Form1099MiscListItemResponse", "Form1099NecListItemResponse", "Form1099RListItemResponse" }

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
        instance = Form1099ListResponseValueInner.model_construct()
        error_messages = []
        match = 0
        # validate data type: Form1099BaseResponse
        if not isinstance(v, Form1099BaseResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099BaseResponse`")
        else:
            match += 1
        # validate data type: Form1042SListItemResponse
        if not isinstance(v, Form1042SListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1042SListItemResponse`")
        else:
            match += 1
        # validate data type: Form1095BListItemResponse
        if not isinstance(v, Form1095BListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1095BListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099DivListItemResponse
        if not isinstance(v, Form1099DivListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099DivListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099IntListItemResponse
        if not isinstance(v, Form1099IntListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099IntListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099KListItemResponse
        if not isinstance(v, Form1099KListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099KListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099MiscListItemResponse
        if not isinstance(v, Form1099MiscListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099MiscListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099NecListItemResponse
        if not isinstance(v, Form1099NecListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099NecListItemResponse`")
        else:
            match += 1
        # validate data type: Form1099RListItemResponse
        if not isinstance(v, Form1099RListItemResponse):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099RListItemResponse`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in Form1099ListResponseValueInner with oneOf schemas: Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in Form1099ListResponseValueInner with oneOf schemas: Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse. Details: " + ", ".join(error_messages))
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

        # deserialize data into Form1099BaseResponse
        try:
            instance.actual_instance = Form1099BaseResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1042SListItemResponse
        try:
            instance.actual_instance = Form1042SListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1095BListItemResponse
        try:
            instance.actual_instance = Form1095BListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099DivListItemResponse
        try:
            instance.actual_instance = Form1099DivListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099IntListItemResponse
        try:
            instance.actual_instance = Form1099IntListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099KListItemResponse
        try:
            instance.actual_instance = Form1099KListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099MiscListItemResponse
        try:
            instance.actual_instance = Form1099MiscListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099NecListItemResponse
        try:
            instance.actual_instance = Form1099NecListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099RListItemResponse
        try:
            instance.actual_instance = Form1099RListItemResponse.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into Form1099ListResponseValueInner with oneOf schemas: Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into Form1099ListResponseValueInner with oneOf schemas: Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse. Details: " + ", ".join(error_messages))
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

    def to_dict(self) -> Optional[Union[Dict[str, Any], Form1042SListItemResponse, Form1095BListItemResponse, Form1099BaseResponse, Form1099DivListItemResponse, Form1099IntListItemResponse, Form1099KListItemResponse, Form1099MiscListItemResponse, Form1099NecListItemResponse, Form1099RListItemResponse]]:
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


