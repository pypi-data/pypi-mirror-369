import math
from datetime import datetime
from datetime import timezone
from json import JSONDecodeError
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import numpy
import pandas
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import Parse
from google.protobuf.struct_pb2 import Value
from requests.exceptions import HTTPError

import tecton
from tecton._internals import errors
from tecton.framework.data_frame import FeatureVector
from tecton_core import conf
from tecton_core import errors as core_errors
from tecton_core import http
from tecton_core.request_context import RequestContext
from tecton_proto.api.featureservice.feature_service__client_pb2 import FeatureServerComplexDataType
from tecton_proto.api.featureservice.feature_service__client_pb2 import FeatureServerDataType
from tecton_proto.api.featureservice.feature_service__client_pb2 import GetFeaturesResponse
from tecton_proto.api.featureservice.feature_service__client_pb2 import GetFeaturesResult
from tecton_proto.api.featureservice.feature_service__client_pb2 import Metadata
from tecton_proto.api.featureservice.feature_service__client_pb2 import QueryFeaturesResponse


TYPE_BOOLEAN = "boolean"
TYPE_FLOAT64 = "float64"
TYPE_INT64 = "int64"
TYPE_STRING = "string"
TYPE_STRING_ARRAY = "string_array"
TYPE_NULL_VALUE = "null_value"
TYPE_ERROR = "error"


class _QueryHelper:
    def __init__(
        self,
        workspace_name: str,
        feature_service_name: Optional[str] = None,
        feature_view_name: Optional[str] = None,
    ):
        assert (feature_service_name is not None) ^ (feature_view_name is not None)
        self.workspace_name = workspace_name
        self.feature_service_name = feature_service_name
        self.feature_view_name = feature_view_name

    def _prepare_headers(self) -> Dict[str, str]:
        token = conf.get_or_none("TECTON_API_KEY")
        if not token:
            raise errors.FS_API_KEY_MISSING

        return {"authorization": f"Tecton-key {token}"}

    def query_features(self, join_keys: Mapping[str, Union[int, numpy.int_, str, bytes]]) -> "tecton.TectonDataFrame":
        """
        Queries the FeatureService with partial set of join_keys defined in the OnlineServingIndex
        of the enclosed feature definitions. Returns feature vectors for all matched records.
        See OnlineServingIndex.

        :param join_keys: Query join keys, i.e., a union of join keys in OnlineServingIndex of all
            enclosed feature definitions.
        :return: A TectonDataFrame
        """
        request_params = self._prepare_request_params(
            join_keys, request_context_map={}, request_context_schema=RequestContext({}), request_options={}
        )

        import json

        request_body = json.dumps({"params": request_params})

        http_response = http.session().post(
            urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/query-features"),
            data=request_body,
            headers=self._prepare_headers(),
        )

        self._detailed_http_raise_for_status(http_response)

        response = QueryFeaturesResponse()
        Parse(http_response.text, response, True)

        pandas_df = self._query_response_to_pandas(response, join_keys)

        import tecton

        return tecton.TectonDataFrame._create(pandas_df)

    def _prepare_request_params(
        self, join_keys, request_context_map=None, request_context_schema=None, request_options=None
    ) -> Dict[str, Any]:
        """
        Prepare the request parameters for an HTTP request to the Feature Server.

        This method builds a dictionary of parameters to be sent to the Feature Server API.
        It does not rely on protobuf-generated code, so that validation is left to the server
        and the SDK is not tightly coupled to the protobuf schema, which may change more frequently.

        Args:
            join_keys (Mapping): Dictionary of join key names to values. Values must be int, numpy.int_, str, bytes, or None.
            request_context_map (Optional[Mapping], optional): Dictionary of request context key-value pairs. Defaults to empty dict.
            request_context_schema (Optional[RequestContext], optional): Schema object for request context validation. Defaults to None.
            request_options (Optional[Dict], optional): Dictionary of request options (snake_case keys). Defaults to empty dict.

        Returns:
            dict: Dictionary of parameters ready to be serialized and sent to the Feature Server.

        Raises:
            errors.INVALID_INDIVIDUAL_JOIN_KEY_TYPE: If a join key value is of an unsupported type.
            errors.UNKNOWN_REQUEST_CONTEXT_KEY: If a request context key is not present in the schema.
        """
        request_context = request_context_map or {}
        request_options = request_options or {}

        params = {
            "workspaceName": self.workspace_name,
            "metadataOptions": {
                "includeNames": True,
                "includeDataTypes": True,
                "includeEffectiveTimes": True,
                "includeSloInfo": True,
            },
            "joinKeyMap": {},
            "requestContextMap": {},
            "requestOptions": {},
        }

        if self.feature_service_name is not None:
            params["featureServiceName"] = self.feature_service_name
        elif self.feature_view_name is not None:
            params["featureViewName"] = self.feature_view_name

        for k, v in join_keys.items():
            if type(v) not in (int, numpy.int_, str, bytes, type(None)):
                raise errors.INVALID_INDIVIDUAL_JOIN_KEY_TYPE(k, type(v))
            params["joinKeyMap"][k] = self._python_value_to_json(v)

        for k, v in request_context.items():
            data_type = request_context_schema.schema.get(k, None)
            if data_type is None:
                raise errors.UNKNOWN_REQUEST_CONTEXT_KEY(sorted(request_context_schema.schema.keys()), k)
            params["requestContextMap"][k] = self._python_value_to_json(v)

        for k, v in request_options.items():
            camel_case_key = self._snake_to_camel_case(k)
            # Only convert float edge cases for request options, preserve other types
            if isinstance(v, (float, numpy.floating)):
                params["requestOptions"][camel_case_key] = self._python_value_to_json(v)
            else:
                params["requestOptions"][camel_case_key] = v

        return params

    def _python_value_to_json(self, value):
        """Convert Python value to JSON-serializable format.

        Note: Integers are converted to strings to match the original proto behavior
        and server expectations for join keys.
        """
        if value is None:
            return None
        elif isinstance(value, bool):
            # Check bool first since bool is a subclass of int in Python
            return value
        elif isinstance(value, (int, numpy.int_)):
            # Convert integers to strings to match original proto behavior
            return str(value)
        elif isinstance(value, (float, numpy.floating)):
            # Handle special float values (inf, -inf, nan) for JSON compatibility
            if math.isinf(value):
                return "Infinity" if value > 0 else "-Infinity"
            elif math.isnan(value):
                return "NaN"
            else:
                return value
        elif isinstance(value, str):
            return value
        elif isinstance(value, datetime):
            # Convert datetime to ISO 8601 format expected by the server
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: self._python_value_to_json(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._python_value_to_json(item) for item in value]
        else:
            msg = f"Unsupported type: {type(value)}"
            raise ValueError(msg)

    def get_feature_vector(
        self,
        join_keys: Mapping[str, Union[int, numpy.int_, str, bool]],
        include_join_keys_in_response: bool,
        request_context_map: Mapping[str, Union[int, numpy.int_, str, float, bool]],
        request_context_schema: RequestContext,
        request_options: Optional[Dict[str, Any]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton FeatureVector.

        :param join_keys: Join keys of the enclosed feature definitions.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.
        :param request_options: Dictionary of request options to control feature server behavior.

        :return: A FeatureVector of the results.
        """
        request_params = self._prepare_request_params(
            join_keys, request_context_map, request_context_schema, request_options
        )

        import json

        request_body = json.dumps({"params": request_params})

        http_response = http.session().post(
            urljoin(conf.get_or_raise("FEATURE_SERVICE") + "/", "v1/feature-service/get-features"),
            data=request_body,
            headers=self._prepare_headers(),
        )

        self._detailed_http_raise_for_status(http_response)

        response = GetFeaturesResponse()
        Parse(http_response.text, response, True)

        return self._response_to_feature_vector(response, include_join_keys_in_response, join_keys)

    def _response_to_feature_vector(
        self,
        response: GetFeaturesResponse,
        include_join_keys: bool,
        join_keys: Dict,
    ) -> FeatureVector:
        features = {}
        if include_join_keys:
            for k, v in join_keys.items():
                features[k] = v

        features.update(self._feature_dict(response.result, response.metadata))
        metadata_values = self._prepare_metadata_response(response.metadata)
        return FeatureVector(
            names=list(features.keys()),
            values=list(features.values()),
            effective_times=[metadata_values["effective_time"].get(name) for name in features.keys()],
            slo_info=metadata_values["slo_info"],
        )

    def _prepare_metadata_response(self, metadata: Metadata) -> Dict[str, dict]:
        metadata_values = {}
        metadata_values["slo_info"] = MessageToDict(metadata.slo_info)

        times = {}
        for i, feature in enumerate(metadata.features):
            time = metadata.features[i].effective_time
            time = datetime.utcfromtimestamp(time.seconds)
            times[metadata.features[i].name] = time

        metadata_values["effective_time"] = times
        return metadata_values

    def _feature_dict(self, result: GetFeaturesResult, metadata: Metadata) -> Dict[str, Union[int, str, float, list]]:
        values = {}
        for i, feature in enumerate(result.features):
            values[metadata.features[i].name] = self._pb_to_python_value(feature, metadata.features[i].data_type)

        for i, jk in enumerate(result.join_keys):
            values[metadata.join_keys[i].name] = self._pb_to_python_value(jk, metadata.join_keys[i].data_type)
        return values

    def _snake_to_camel_case(self, snake_str: str) -> str:
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    def _detailed_http_raise_for_status(self, http_response):
        try:
            http_response.raise_for_status()
        except HTTPError as e:
            try:
                details = http_response.json()
            except JSONDecodeError as json_e:
                msg = f"unable to process response ({http_response.status_code} error)"
                raise errors.FS_INTERNAL_ERROR(msg)

            # Include the actual error message details in the exception if available.
            if "message" in details and "code" in details:
                msg = details["message"]

                status = http_response.status_code
                if status == 400 or status == 401 or status == 403:
                    raise core_errors.TectonValidationError(msg)
                elif status == 404:
                    raise core_errors.TectonNotFoundError(msg)

                raise errors.FS_INTERNAL_ERROR(msg)
            else:
                # Otherwise just throw the original error.
                raise e

    def _query_response_to_pandas(
        self, response: QueryFeaturesResponse, join_keys: Mapping[str, Union[int, numpy.int_, str, bytes]]
    ):
        response_count = len(response.results)
        data = {key: [value] * response_count for key, value in join_keys.items()}
        for result in response.results:
            features = self._feature_dict(result, response.metadata)
            # note that int(1) = numpy.int_(1) so dict lookup works here
            for k, v in features.items():
                if k not in data.keys():
                    data[k] = []
                data[k] = [*list(data[k]), v]  # type: ignore
        return pandas.DataFrame(data=data)

    def _pb_to_python_value(self, v: Value, data_type: FeatureServerComplexDataType):
        """Converts a "Value" wrapped value into the type indicated by "type"."""
        which = v.WhichOneof("kind")
        if which is None or which == TYPE_NULL_VALUE:
            return None
        val = getattr(v, which)

        if data_type.type in (FeatureServerDataType.string, FeatureServerDataType.boolean):
            return val
        elif data_type.type in (FeatureServerDataType.float64, FeatureServerDataType.float32):
            return float(val)
        elif data_type.type == FeatureServerDataType.int64:
            # The feature server returns int64s as strings, which need to be cast.
            return int(val)
        elif data_type.type == FeatureServerDataType.timestamp:
            # Trying to parse a string with microseconds using "%Y-%m-%dT%H:%M:%SZ" will raise a ValueError so we need to try both.
            try:
                return datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            except ValueError:
                return datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        elif data_type.type == FeatureServerDataType.array:
            return [self._pb_to_python_value(vi, data_type.element_type) for vi in val.values]
        elif data_type.type == FeatureServerDataType.struct:
            # Structs are returned as a list of values with the same order and length as the metadata's
            # `FeatureServerComplexDataType.fields`.
            struct = {}
            for i, field in enumerate(data_type.fields):
                python_value = self._pb_to_python_value(val.values[i], field.data_type)
                if python_value is not None:
                    struct[field.name] = python_value
            return struct
        elif data_type.type == FeatureServerDataType.map:
            return {k: self._pb_to_python_value(v, data_type.value_type) for k, v in val.fields.items()}
        else:
            msg = f"Unexpected type '{data_type}' - Expected float64, int64, string, boolean, timestamp, array, or struct."
            raise Exception(msg)
