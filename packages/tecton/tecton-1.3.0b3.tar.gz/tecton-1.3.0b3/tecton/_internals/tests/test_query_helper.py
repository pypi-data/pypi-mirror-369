import json
from datetime import datetime
from io import BytesIO
from typing import Optional
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

import numpy
import pandas
import requests
from google.protobuf.struct_pb2 import Struct
from google.protobuf.struct_pb2 import Value
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal

from tecton._internals.query_helper import _QueryHelper
from tecton_core import errors
from tecton_core.request_context import RequestContext
from tecton_proto.api.featureservice.feature_service__client_pb2 import FeatureServerComplexDataType
from tecton_proto.api.featureservice.feature_service__client_pb2 import FeatureServerDataType
from tecton_proto.api.featureservice.feature_service__client_pb2 import GetFeaturesResponse
from tecton_proto.api.featureservice.feature_service__client_pb2 import GetFeaturesResult
from tecton_proto.api.featureservice.feature_service__client_pb2 import Metadata
from tecton_proto.api.featureservice.feature_service__client_pb2 import QueryFeaturesResponse


def data_type(type_enum: int, element_type_enum: Optional[int] = None) -> FeatureServerComplexDataType:
    complex_type = FeatureServerComplexDataType()
    complex_type.type = type_enum
    if element_type_enum is not None:
        complex_type.element_type.type = element_type_enum
    return complex_type


def value_proto(value) -> Value:
    # Structs must be created from a top-level dictionary.
    wrapper_dict = {"k": value}
    s = Struct()
    s.update(wrapper_dict)
    return s.fields["k"]


class QueryHelperTest(TestCase):
    def setUp(self) -> None:
        self.query_helper = _QueryHelper("", feature_service_name="test1")

    def test_response_to_feature_vector(self):
        test_features = [
            ("f1", data_type(FeatureServerDataType.int64), value_proto("3")),
            ("f2", data_type(FeatureServerDataType.string), value_proto("three")),
            ("f3", data_type(FeatureServerDataType.float64), value_proto(33.3)),
            # The feature service JSON response uses strings for special float values (e.g. "NaN" and "Infinity").
            ("f4", data_type(FeatureServerDataType.float64), value_proto("Infinity")),
            ("f5", data_type(FeatureServerDataType.boolean), value_proto(True)),
            (
                "f6",
                data_type(FeatureServerDataType.array, FeatureServerDataType.string),
                value_proto(["one", "two", None]),
            ),
            ("f7", data_type(FeatureServerDataType.array, FeatureServerDataType.int64), value_proto(["1", "2", None])),
            (
                "f8",
                data_type(FeatureServerDataType.array, FeatureServerDataType.float32),
                value_proto([1.1, "Infinity", None]),
            ),
        ]
        response = GetFeaturesResponse()
        for f in test_features:
            feature = response.metadata.features.add()
            feature.name = f[0]
            feature.data_type.CopyFrom(f[1])
            response.result.features.extend([f[2]])

        actual_fv = self.query_helper._response_to_feature_vector(response, True, {"jk1": "abc"})
        actual_dict = actual_fv.to_dict()
        expected_dict = {
            "f1": 3,
            "f2": "three",
            "f3": 33.3,
            "f4": float("inf"),
            "f5": True,
            "f6": ["one", "two", None],
            "f7": [1, 2, None],
            "f8": [1.1, float("inf"), None],
            "jk1": "abc",
        }
        self.assertEqual(actual_dict, expected_dict)

        actual_pd = actual_fv.to_pandas()
        expected_pd = pandas.DataFrame(
            [
                [
                    "abc",
                    3,
                    "three",
                    33.3,
                    float("inf"),
                    True,
                    ["one", "two", None],
                    [1, 2, None],
                    [1.1, float("inf"), None],
                ]
            ],
            columns=["jk1", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
        )
        assert_frame_equal(actual_pd, expected_pd)

        actual_np = actual_fv.to_numpy()
        expected_np = numpy.array(
            ["abc", 3, "three", 33.3, float("inf"), True, ["one", "two", None], [1, 2, None], [1.1, float("inf"), None]]
        )
        assert_array_equal(actual_np, expected_np)

    def test_response_to_feature_vector_with_metadata(self):
        test_features = [
            ("f1", data_type(FeatureServerDataType.int64), value_proto("3"), 10000),
            ("f2", data_type(FeatureServerDataType.string), value_proto("three"), 100000),
            ("f3", data_type(FeatureServerDataType.float64), value_proto(33.3), 1000000),
            (
                "f4",
                data_type(FeatureServerDataType.array, FeatureServerDataType.string),
                value_proto(["one", "two", None]),
                10000000,
            ),
        ]
        response = GetFeaturesResponse()
        response.metadata.slo_info.slo_eligible = True
        for f in test_features:
            feature = response.metadata.features.add()
            feature.name = f[0]
            feature.data_type.CopyFrom(f[1])
            feature.effective_time.seconds = f[3]
            response.result.features.extend([f[2]])

        actual_fv = self.query_helper._response_to_feature_vector(response, True, {"jk1": "abc"})
        date1 = datetime.utcfromtimestamp(10000)
        date2 = datetime.utcfromtimestamp(100000)
        date3 = datetime.utcfromtimestamp(1000000)
        date4 = datetime.utcfromtimestamp(10000000)

        actual_dict = actual_fv.to_dict(return_effective_times=True)
        expected_dict = {
            "f1": {"value": 3, "effective_time": date1},
            "f2": {"value": "three", "effective_time": date2},
            "f3": {"value": 33.3, "effective_time": date3},
            "f4": {"value": ["one", "two", None], "effective_time": date4},
            "jk1": {"value": "abc", "effective_time": None},
        }
        self.assertEqual(actual_dict, expected_dict)

        actual_pd = actual_fv.to_pandas(return_effective_times=True)
        expected_pd = pandas.DataFrame(
            [
                ["jk1", "abc", None],
                ["f1", 3, date1],
                ["f2", "three", date2],
                ["f3", 33.3, date3],
                ["f4", ["one", "two", None], date4],
            ],
            columns=["name", "value", "effective_time"],
        )
        assert_frame_equal(actual_pd, expected_pd)

        actual_np = actual_fv.to_numpy(return_effective_times=True)
        expected_np = numpy.array([["abc", 3, "three", 33.3, ["one", "two", None]], [None, date1, date2, date3, date4]])
        assert_array_equal(actual_np, expected_np)

    def test_features_dict(self):
        result = GetFeaturesResult()
        meta = Metadata()

        feature = meta.features.add()
        feature.name = "race_track"
        feature.data_type.type = FeatureServerDataType.string
        result.features.extend([value_proto("silverstone")])

        wildcard_join_key = meta.join_keys.add()
        wildcard_join_key.name = "race_id"
        wildcard_join_key.data_type.type = FeatureServerDataType.int64
        result.join_keys.extend([value_proto("5")])

        actual = self.query_helper._feature_dict(result, meta)
        expected = {"race_track": "silverstone", "race_id": 5}
        self.assertEqual(actual, expected)

    def test_query_response_to_pandas(self):
        query_response = QueryFeaturesResponse()

        feature = query_response.metadata.features.add()
        feature.name = "race_track"
        feature.data_type.type = FeatureServerDataType.string
        wildcard_join_key = query_response.metadata.join_keys.add()
        wildcard_join_key.name = "race_id"
        wildcard_join_key.data_type.type = FeatureServerDataType.int64
        for i, val in enumerate([value_proto("silverstone"), value_proto("monza")]):
            result = query_response.results.add()
            feature_result = result.features.extend([val])
            join_key_result = result.join_keys.extend([value_proto(str(i))])

        actual = self.query_helper._query_response_to_pandas(query_response, {"race_season": 2020})
        expected = pandas.DataFrame(
            {
                "race_season": [2020, 2020],
                "race_track": ["silverstone", "monza"],
                "race_id": [0, 1],
            }
        )
        assert_frame_equal(actual, expected)

    def test_detailed_http_raise_for_status(self):
        def http_response(msg="OK", status=200, grpcCode=0):
            r = requests.Response()
            r.status_code = status
            r.raw = BytesIO(bytes(f'{{"message": "{msg}", "code": {grpcCode}}}', encoding="utf-8"))
            return r

        test_err_responses = [
            (http_response(msg="bad request", status=400), errors.TectonValidationError, "bad request"),
            (http_response(msg="no authN", status=401), errors.TectonValidationError, "no authN"),
            (http_response(msg="no authZ", status=403), errors.TectonValidationError, "no authZ"),
            (http_response(msg="not found", status=404), errors.TectonNotFoundError, "not found"),
            (http_response(msg="internal", status=500), errors.TectonInternalError, "internal"),
        ]

        # err responses
        for tr in test_err_responses:
            with self.assertRaisesRegex(tr[1], tr[2]) as e:
                self.query_helper._detailed_http_raise_for_status(tr[0])

        # ok response
        try:
            self.query_helper._detailed_http_raise_for_status(http_response())
        except Exception:
            self.assertTrue(False)

    @patch("tecton_core.http.session")
    @patch("tecton_core.conf.get_or_raise")
    @patch("tecton_core.conf.get_or_none")
    def test_get_feature_vector(self, mock_conf_get_or_none, mock_conf_get_or_raise, mock_http_session):
        """Test that get_feature_vector makes correct HTTP requests and processes responses properly."""
        # Setup mocks
        mock_conf_get_or_none.return_value = "test-api-key"
        mock_conf_get_or_raise.return_value = "https://feature-service-example.tecton.ai"

        # Create mock HTTP session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        # Create a realistic GetFeaturesResponse for the mock
        response_proto = GetFeaturesResponse()

        response_proto.metadata.slo_info.slo_eligible = True

        feature_meta = response_proto.metadata.features.add()
        feature_meta.name = "user_score"
        feature_meta.data_type.type = FeatureServerDataType.float64
        feature_meta.effective_time.seconds = 1640995200  # 2022-01-01 00:00:00

        join_key_meta = response_proto.metadata.join_keys.add()
        join_key_meta.name = "user_id"
        join_key_meta.data_type.type = FeatureServerDataType.string

        response_proto.result.features.extend([value_proto(0.85)])
        response_proto.result.join_keys.extend([value_proto("user_123")])

        # Mock the response text to return our proto as JSON
        from google.protobuf.json_format import MessageToJson

        mock_response.text = MessageToJson(response_proto)

        mock_session.post.return_value = mock_response
        mock_http_session.return_value = mock_session

        join_keys = {"user_id": "user_123", "merchant_id": "merchant_456"}
        request_context_map = {
            "transaction_amount": 100.50,
            "user_tier": "premium",
            "threshold": float("-inf"),
            "confidence": float("nan"),
            "score": float("inf"),
            "values": [1.0, float("inf"), float("-inf")],
            "metrics": {"accuracy": float("nan"), "precision": 0.95},
        }
        request_context_schema = RequestContext(
            {
                "transaction_amount": "float64",
                "user_tier": "string",
                "threshold": "float64",
                "confidence": "float64",
                "score": "float64",
                "values": "array",
                "metrics": "map",
            }
        )
        request_options = {
            "read_from_cache": False,
            "write_to_cache": True,
            "latency_budget_ms": 2000,
            "coerce_null_counts_to_zero": True,
            "cache_ttl": float("inf"),
            "timeout": float("nan"),
        }

        # Call the method under test
        result = self.query_helper.get_feature_vector(
            join_keys=join_keys,
            include_join_keys_in_response=True,
            request_context_map=request_context_map,
            request_context_schema=request_context_schema,
            request_options=request_options,
        )

        # Verify HTTP request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args

        # Check URL
        expected_url = "https://feature-service-example.tecton.ai/v1/feature-service/get-features"
        self.assertEqual(call_args[0][0], expected_url)

        # Check headers
        expected_headers = {"authorization": "Tecton-key test-api-key"}
        self.assertEqual(call_args[1]["headers"], expected_headers)

        # Check request body
        request_body = call_args[1]["data"]
        self.assertIsInstance(request_body, str)
        body_json = json.loads(request_body)
        self.assertEqual(
            body_json["params"],
            {
                "featureServiceName": "test1",
                "workspaceName": "",
                "metadataOptions": {
                    "includeNames": True,
                    "includeDataTypes": True,
                    "includeEffectiveTimes": True,
                    "includeSloInfo": True,
                },
                "joinKeyMap": {"user_id": "user_123", "merchant_id": "merchant_456"},
                "requestContextMap": {
                    "transaction_amount": 100.50,
                    "user_tier": "premium",
                    "threshold": "-Infinity",
                    "confidence": "NaN",
                    "score": "Infinity",
                    "values": [1.0, "Infinity", "-Infinity"],
                    "metrics": {"accuracy": "NaN", "precision": 0.95},
                },
                "requestOptions": {
                    "readFromCache": False,
                    "writeToCache": True,
                    "latencyBudgetMs": 2000,
                    "coerceNullCountsToZero": True,
                    "cacheTtl": "Infinity",
                    "timeout": "NaN",
                },
            },
        )

        # Verify response processing
        self.assertIsNotNone(result)
        result_dict = result.to_dict()

        self.assertEqual(
            result_dict,
            {
                "user_score": 0.85,
                "user_id": "user_123",
                "merchant_id": "merchant_456",
            },
        )

        self.assertEqual(result.slo_info, {"sloEligible": True})
