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
from Avalara.SDK.models.A1099.V2.form1042_s_list import Form1042SList
from Avalara.SDK.models.A1099.V2.form1095_b_list import Form1095BList
from Avalara.SDK.models.A1099.V2.form1095_c_list import Form1095CList
from Avalara.SDK.models.A1099.V2.form1099_div_list import Form1099DivList
from Avalara.SDK.models.A1099.V2.form1099_int_list import Form1099IntList
from Avalara.SDK.models.A1099.V2.form1099_k_list import Form1099KList
from Avalara.SDK.models.A1099.V2.form1099_misc_list import Form1099MiscList
from Avalara.SDK.models.A1099.V2.form1099_nec_list import Form1099NecList
from Avalara.SDK.models.A1099.V2.form1099_r_list import Form1099RList
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

BULKUPSERT1099FORMSREQUEST_ONE_OF_SCHEMAS = ["Form1042SList", "Form1095BList", "Form1095CList", "Form1099DivList", "Form1099IntList", "Form1099KList", "Form1099MiscList", "Form1099NecList", "Form1099RList"]

class BulkUpsert1099FormsRequest(BaseModel):
    """
    BulkUpsert1099FormsRequest
    """
    # data type: Form1042SList
    oneof_schema_1_validator: Optional[Form1042SList] = None
    # data type: Form1095BList
    oneof_schema_2_validator: Optional[Form1095BList] = None
    # data type: Form1095CList
    oneof_schema_3_validator: Optional[Form1095CList] = None
    # data type: Form1099DivList
    oneof_schema_4_validator: Optional[Form1099DivList] = None
    # data type: Form1099IntList
    oneof_schema_5_validator: Optional[Form1099IntList] = None
    # data type: Form1099KList
    oneof_schema_6_validator: Optional[Form1099KList] = None
    # data type: Form1099MiscList
    oneof_schema_7_validator: Optional[Form1099MiscList] = None
    # data type: Form1099NecList
    oneof_schema_8_validator: Optional[Form1099NecList] = None
    # data type: Form1099RList
    oneof_schema_9_validator: Optional[Form1099RList] = None
    actual_instance: Optional[Union[Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList]] = None
    one_of_schemas: Set[str] = { "Form1042SList", "Form1095BList", "Form1095CList", "Form1099DivList", "Form1099IntList", "Form1099KList", "Form1099MiscList", "Form1099NecList", "Form1099RList" }

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
        instance = BulkUpsert1099FormsRequest.model_construct()
        error_messages = []
        match = 0
        # validate data type: Form1042SList
        if not isinstance(v, Form1042SList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1042SList`")
        else:
            match += 1
        # validate data type: Form1095BList
        if not isinstance(v, Form1095BList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1095BList`")
        else:
            match += 1
        # validate data type: Form1095CList
        if not isinstance(v, Form1095CList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1095CList`")
        else:
            match += 1
        # validate data type: Form1099DivList
        if not isinstance(v, Form1099DivList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099DivList`")
        else:
            match += 1
        # validate data type: Form1099IntList
        if not isinstance(v, Form1099IntList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099IntList`")
        else:
            match += 1
        # validate data type: Form1099KList
        if not isinstance(v, Form1099KList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099KList`")
        else:
            match += 1
        # validate data type: Form1099MiscList
        if not isinstance(v, Form1099MiscList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099MiscList`")
        else:
            match += 1
        # validate data type: Form1099NecList
        if not isinstance(v, Form1099NecList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099NecList`")
        else:
            match += 1
        # validate data type: Form1099RList
        if not isinstance(v, Form1099RList):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Form1099RList`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in BulkUpsert1099FormsRequest with oneOf schemas: Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in BulkUpsert1099FormsRequest with oneOf schemas: Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList. Details: " + ", ".join(error_messages))
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

        # deserialize data into Form1042SList
        try:
            instance.actual_instance = Form1042SList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1095BList
        try:
            instance.actual_instance = Form1095BList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1095CList
        try:
            instance.actual_instance = Form1095CList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099DivList
        try:
            instance.actual_instance = Form1099DivList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099IntList
        try:
            instance.actual_instance = Form1099IntList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099KList
        try:
            instance.actual_instance = Form1099KList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099MiscList
        try:
            instance.actual_instance = Form1099MiscList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099NecList
        try:
            instance.actual_instance = Form1099NecList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into Form1099RList
        try:
            instance.actual_instance = Form1099RList.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into BulkUpsert1099FormsRequest with oneOf schemas: Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into BulkUpsert1099FormsRequest with oneOf schemas: Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList. Details: " + ", ".join(error_messages))
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

    def to_dict(self) -> Optional[Union[Dict[str, Any], Form1042SList, Form1095BList, Form1095CList, Form1099DivList, Form1099IntList, Form1099KList, Form1099MiscList, Form1099NecList, Form1099RList]]:
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


