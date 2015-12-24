"""Generated message classes for cloudfunctions version v1beta1.

API for managing lightweight user-provided functions executed in response to
events.
"""
# NOTE: This file is autogenerated and should not be edited by hand.

from protorpc import messages as _messages

from googlecloudsdk.third_party.apitools.base.py import encoding


package = 'cloudfunctions'


class CallFunctionResponse(_messages.Message):
  """Response of CallFunction method.

  Fields:
    error: Either system or user-function generated error. Set if execution
      was not successful.
    executionId: Execution id of function invocation.
    result: Result populated for successful execution of synchronous function.
      Will not be populated if function does not return a result through
      context.
  """

  error = _messages.StringField(1)
  executionId = _messages.StringField(2)
  result = _messages.StringField(3)


class CloudfunctionsOperationsGetRequest(_messages.Message):
  """A CloudfunctionsOperationsGetRequest object.

  Fields:
    name: The name of the operation resource.
  """

  name = _messages.StringField(1, required=True)


class CloudfunctionsProjectsRegionsFunctionsCallRequest(_messages.Message):
  """A CloudfunctionsProjectsRegionsFunctionsCallRequest object.

  Fields:
    data: Input to be passed to the function.
    name: The name of the function to be called.
  """

  data = _messages.StringField(1)
  name = _messages.StringField(2, required=True)


class CloudfunctionsProjectsRegionsFunctionsCreateRequest(_messages.Message):
  """A CloudfunctionsProjectsRegionsFunctionsCreateRequest object.

  Fields:
    hostedFunction: A HostedFunction resource to be passed as the request
      body.
    location: The project and region in which the function should be created,
      specified in the format: projects/*/regions/*
  """

  hostedFunction = _messages.MessageField('HostedFunction', 1)
  location = _messages.StringField(2, required=True)


class CloudfunctionsProjectsRegionsFunctionsDeleteRequest(_messages.Message):
  """A CloudfunctionsProjectsRegionsFunctionsDeleteRequest object.

  Fields:
    name: The name of the function which should be deleted.
  """

  name = _messages.StringField(1, required=True)


class CloudfunctionsProjectsRegionsFunctionsGetRequest(_messages.Message):
  """A CloudfunctionsProjectsRegionsFunctionsGetRequest object.

  Fields:
    name: The name of the function which details should be obtained.
  """

  name = _messages.StringField(1, required=True)


class CloudfunctionsProjectsRegionsFunctionsListRequest(_messages.Message):
  """A CloudfunctionsProjectsRegionsFunctionsListRequest object.

  Fields:
    location: The project and region in which the function should be created,
      specified in the format: projects/*/regions/*
    pageSize: Maximum number of functions to return.
    pageToken: The value returned by the last ListFunctionsResponse; indicates
      that this is a continuation of a prior ListFunctions call, and that the
      system should return the next page of data.
  """

  location = _messages.StringField(1, required=True)
  pageSize = _messages.IntegerField(2, variant=_messages.Variant.INT32)
  pageToken = _messages.StringField(3)


class FunctionTrigger(_messages.Message):
  """Describes binding of computation to the event source.

  Fields:
    gsUri: Google Cloud Storage resource whose changes trigger the events.
      Currently, it must have the form gs://<bucket>/ (that is, it must refer
      to a bucket, rather than an object).
    pubsubTopic: A pub/sub type of source.
    webTrigger: A web endpoint (e.g. HTTP) type of source that can be trigger
      via URL.
  """

  gsUri = _messages.StringField(1)
  pubsubTopic = _messages.StringField(2)
  webTrigger = _messages.MessageField('WebTrigger', 3)


class HostedFunction(_messages.Message):
  """Describes a cloud function that contains user computation executed in
  response to an event. It encapsulate function and triggers configurations.

  Enums:
    StatusValueValuesEnum: [Output only] Status of the function deployment.

  Fields:
    entryPoint: The name of the function (as defined in source code) that will
      be executed. Defaults to the resource name suffix, if not specified. For
      backward compatibility, if function with given name is not found, then
      the system will try to use function named 'function'. For Node.js this
      is name of a function exported by the module specified in
      source_location.
    gcsUrl: GCS URL pointing to the zip archive which contains the function.
    latestOperation: [Output only] Name of the most recent operation modifying
      the function. If the function status is DEPLOYING or DELETING, then it
      points to the active operation.
    name: A user-defined name of the function. Function names must be unique
      globally and match pattern: projects/*/regions/*/functions/*
    oauthScopes: The set of Google API scopes to be made available to the
      function while it is being executed. Values should be in the format of
      scope developer codes, for example:
      "https://www.googleapis.com/auth/compute".
    sourceRepository: The hosted repository where the function is defined.
    status: [Output only] Status of the function deployment.
    triggers: List of triggers.
  """

  class StatusValueValuesEnum(_messages.Enum):
    """[Output only] Status of the function deployment.

    Values:
      STATUS_UNSPECIFIED: Status not specified.
      READY: Successfully deployed.
      FAILED: Not deployed correctly - behavior is undefined. The item should
        be updated or deleted to move it out of this state.
      DEPLOYING: Creation or update in progress.
      DELETING: Deletion in progress.
    """
    STATUS_UNSPECIFIED = 0
    READY = 1
    FAILED = 2
    DEPLOYING = 3
    DELETING = 4

  entryPoint = _messages.StringField(1)
  gcsUrl = _messages.StringField(2)
  latestOperation = _messages.StringField(3)
  name = _messages.StringField(4)
  oauthScopes = _messages.StringField(5, repeated=True)
  sourceRepository = _messages.MessageField('SourceRepository', 6)
  status = _messages.EnumField('StatusValueValuesEnum', 7)
  triggers = _messages.MessageField('FunctionTrigger', 8, repeated=True)


class ListFunctionsResponse(_messages.Message):
  """Response for the ListFunctions method.

  Fields:
    functions: The functions that match the request.
    nextPageToken: If not empty, indicates that there may be more functions
      that match the request; this value should be passed in a new
      ListFunctionsRequest to get more functions.
  """

  functions = _messages.MessageField('HostedFunction', 1, repeated=True)
  nextPageToken = _messages.StringField(2)


class Operation(_messages.Message):
  """This resource represents a long-running operation that is the result of a
  network API call.

  Messages:
    MetadataValue: Service-specific metadata associated with the operation.
      It typically contains progress information and common metadata such as
      create time. Some services might not provide such metadata.  Any method
      that returns a long-running operation should document the metadata type,
      if any.
    ResponseValue: The normal response of the operation in case of success.
      If the original method returns no data on success, such as `Delete`, the
      response is `google.protobuf.Empty`.  If the original method is standard
      `Get`/`Create`/`Update`, the response should be the resource.  For other
      methods, the response should have the type `XxxResponse`, where `Xxx` is
      the original method name.  For example, if the original method name is
      `TakeSnapshot()`, the inferred response type is `TakeSnapshotResponse`.

  Fields:
    done: If the value is `false`, it means the operation is still in
      progress. If true, the operation is completed, and either `error` or
      `response` is available.
    error: The error result of the operation in case of failure.
    metadata: Service-specific metadata associated with the operation.  It
      typically contains progress information and common metadata such as
      create time. Some services might not provide such metadata.  Any method
      that returns a long-running operation should document the metadata type,
      if any.
    name: The server-assigned name, which is only unique within the same
      service that originally returns it. If you use the default HTTP mapping
      above, the `name` should have the format of
      `operations/some/unique/name`.
    response: The normal response of the operation in case of success.  If the
      original method returns no data on success, such as `Delete`, the
      response is `google.protobuf.Empty`.  If the original method is standard
      `Get`/`Create`/`Update`, the response should be the resource.  For other
      methods, the response should have the type `XxxResponse`, where `Xxx` is
      the original method name.  For example, if the original method name is
      `TakeSnapshot()`, the inferred response type is `TakeSnapshotResponse`.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class MetadataValue(_messages.Message):
    """Service-specific metadata associated with the operation.  It typically
    contains progress information and common metadata such as create time.
    Some services might not provide such metadata.  Any method that returns a
    long-running operation should document the metadata type, if any.

    Messages:
      AdditionalProperty: An additional property for a MetadataValue object.

    Fields:
      additionalProperties: Properties of the object. Contains field @ype with
        type URL.
    """

    class AdditionalProperty(_messages.Message):
      """An additional property for a MetadataValue object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = _messages.StringField(1)
      value = _messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = _messages.MessageField('AdditionalProperty', 1, repeated=True)

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ResponseValue(_messages.Message):
    """The normal response of the operation in case of success.  If the
    original method returns no data on success, such as `Delete`, the response
    is `google.protobuf.Empty`.  If the original method is standard
    `Get`/`Create`/`Update`, the response should be the resource.  For other
    methods, the response should have the type `XxxResponse`, where `Xxx` is
    the original method name.  For example, if the original method name is
    `TakeSnapshot()`, the inferred response type is `TakeSnapshotResponse`.

    Messages:
      AdditionalProperty: An additional property for a ResponseValue object.

    Fields:
      additionalProperties: Properties of the object. Contains field @ype with
        type URL.
    """

    class AdditionalProperty(_messages.Message):
      """An additional property for a ResponseValue object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = _messages.StringField(1)
      value = _messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = _messages.MessageField('AdditionalProperty', 1, repeated=True)

  done = _messages.BooleanField(1)
  error = _messages.MessageField('Status', 2)
  metadata = _messages.MessageField('MetadataValue', 3)
  name = _messages.StringField(4)
  response = _messages.MessageField('ResponseValue', 5)


class OperationMetadata(_messages.Message):
  """Metadata describing an Operation

  Enums:
    TypeValueValuesEnum: Type of operation.

  Messages:
    RequestValue: The original request that started the operation.

  Fields:
    request: The original request that started the operation.
    target: Target of the operation - for example
      projects/project-1/regions/region-1/functions/function-1
    type: Type of operation.
  """

  class TypeValueValuesEnum(_messages.Enum):
    """Type of operation.

    Values:
      OPERATION_UNSPECIFIED: Unknown operation type.
      CREATE_FUNCTION: Triggered by CreateFunction call
      UPDATE_FUNCTION: Triggered by UpdateFunction call
      DELETE_FUNCTION: Triggered by DeleteFunction call.
    """
    OPERATION_UNSPECIFIED = 0
    CREATE_FUNCTION = 1
    UPDATE_FUNCTION = 2
    DELETE_FUNCTION = 3

  @encoding.MapUnrecognizedFields('additionalProperties')
  class RequestValue(_messages.Message):
    """The original request that started the operation.

    Messages:
      AdditionalProperty: An additional property for a RequestValue object.

    Fields:
      additionalProperties: Properties of the object. Contains field @ype with
        type URL.
    """

    class AdditionalProperty(_messages.Message):
      """An additional property for a RequestValue object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = _messages.StringField(1)
      value = _messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = _messages.MessageField('AdditionalProperty', 1, repeated=True)

  request = _messages.MessageField('RequestValue', 1)
  target = _messages.StringField(2)
  type = _messages.EnumField('TypeValueValuesEnum', 3)


class SourceRepository(_messages.Message):
  """Describes the location of the function source in a remote repository.

  Fields:
    branch: The name of the branch from which the function should be fetched.
    deployedRevision: [Output only] The id of the revision that was resolved
      at the moment of function creation or update. For example when a user
      deployed from a branch, it will be the revision id of the latest change
      on this branch at that time. If user deployed from revision then this
      value will be always equal to the revision specified by the user.
    repositoryUrl: URL to the hosted repository where the function is defined.
      Only paths in https://source.developers.google.com domain are supported.
      The path should contain the name of the repository.
    revision: The id of the revision that captures the state of the repository
      from which the function should be fetched.
    sourcePath: The path within the repository where the function is defined.
      The path should point to the directory where cloud functions files are
      located. Use '/' if the function is defined directly in the root
      directory of a repository.
    sourceUrl: A string attribute.
    tag: The name of the tag that captures the state of the repository from
      which the function should be fetched.
  """

  branch = _messages.StringField(1)
  deployedRevision = _messages.StringField(2)
  repositoryUrl = _messages.StringField(3)
  revision = _messages.StringField(4)
  sourcePath = _messages.StringField(5)
  sourceUrl = _messages.StringField(6)
  tag = _messages.StringField(7)


class StandardQueryParameters(_messages.Message):
  """Query parameters accepted by all methods.

  Enums:
    FXgafvValueValuesEnum: V1 error format.
    AltValueValuesEnum: Data format for response.

  Fields:
    f__xgafv: V1 error format.
    access_token: OAuth access token.
    alt: Data format for response.
    bearer_token: OAuth bearer token.
    callback: JSONP
    fields: Selector specifying which fields to include in a partial response.
    key: API key. Your API key identifies your project and provides you with
      API access, quota, and reports. Required unless you provide an OAuth 2.0
      token.
    oauth_token: OAuth 2.0 token for the current user.
    pp: Pretty-print response.
    prettyPrint: Returns response with indentations and line breaks.
    quotaUser: Available to use for quota purposes for server-side
      applications. Can be any arbitrary string assigned to a user, but should
      not exceed 40 characters.
    trace: A tracing token of the form "token:<tokenid>" or "email:<ldap>" to
      include in api requests.
    uploadType: Legacy upload protocol for media (e.g. "media", "multipart").
    upload_protocol: Upload protocol for media (e.g. "raw", "multipart").
  """

  class AltValueValuesEnum(_messages.Enum):
    """Data format for response.

    Values:
      json: Responses with Content-Type of application/json
      media: Media download with context-dependent Content-Type
      proto: Responses with Content-Type of application/x-protobuf
    """
    json = 0
    media = 1
    proto = 2

  class FXgafvValueValuesEnum(_messages.Enum):
    """V1 error format.

    Values:
      _1: v1 error format
      _2: v2 error format
    """
    _1 = 0
    _2 = 1

  f__xgafv = _messages.EnumField('FXgafvValueValuesEnum', 1)
  access_token = _messages.StringField(2)
  alt = _messages.EnumField('AltValueValuesEnum', 3, default=u'json')
  bearer_token = _messages.StringField(4)
  callback = _messages.StringField(5)
  fields = _messages.StringField(6)
  key = _messages.StringField(7)
  oauth_token = _messages.StringField(8)
  pp = _messages.BooleanField(9, default=True)
  prettyPrint = _messages.BooleanField(10, default=True)
  quotaUser = _messages.StringField(11)
  trace = _messages.StringField(12)
  uploadType = _messages.StringField(13)
  upload_protocol = _messages.StringField(14)


class Status(_messages.Message):
  """The `Status` type defines a logical error model that is suitable for
  different programming environments, including REST APIs and RPC APIs. It is
  used by [gRPC](https://github.com/grpc). The error model is designed to be:
  - Simple to use and understand for most users - Flexible enough to meet
  unexpected needs  # Overview  The `Status` message contains three pieces of
  data: error code, error message, and error details. The error code should be
  an enum value of google.rpc.Code, but it may accept additional error codes
  if needed.  The error message should be a developer-facing English message
  that helps developers *understand* and *resolve* the error. If a localized
  user-facing error message is needed, put the localized message in the error
  details or localize it in the client. The optional error details may contain
  arbitrary information about the error. There is a predefined set of error
  detail types in the package `google.rpc` which can be used for common error
  conditions.  # Language mapping  The `Status` message is the logical
  representation of the error model, but it is not necessarily the actual wire
  format. When the `Status` message is exposed in different client libraries
  and different wire protocols, it can be mapped differently. For example, it
  will likely be mapped to some exceptions in Java, but more likely mapped to
  some error codes in C.  # Other uses  The error model and the `Status`
  message can be used in a variety of environments, either with or without
  APIs, to provide a consistent developer experience across different
  environments.  Example uses of this error model include:  - Partial errors.
  If a service needs to return partial errors to the client,     it may embed
  the `Status` in the normal response to indicate the partial     errors.  -
  Workflow errors. A typical workflow has multiple steps. Each step may
  have a `Status` message for error reporting purpose.  - Batch operations. If
  a client uses batch request and batch response, the     `Status` message
  should be used directly inside batch response, one for     each error sub-
  response.  - Asynchronous operations. If an API call embeds asynchronous
  operation     results in its response, the status of those operations should
  be     represented directly using the `Status` message.  - Logging. If some
  API errors are stored in logs, the message `Status` could     be used
  directly after any stripping needed for security/privacy reasons.

  Messages:
    DetailsValueListEntry: A DetailsValueListEntry object.

  Fields:
    code: The status code, which should be an enum value of google.rpc.Code.
    details: A list of messages that carry the error details.  There will be a
      common set of message types for APIs to use.
    message: A developer-facing error message, which should be in English. Any
      user-facing error message should be localized and sent in the
      google.rpc.Status.details field, or localized by the client.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class DetailsValueListEntry(_messages.Message):
    """A DetailsValueListEntry object.

    Messages:
      AdditionalProperty: An additional property for a DetailsValueListEntry
        object.

    Fields:
      additionalProperties: Properties of the object. Contains field @ype with
        type URL.
    """

    class AdditionalProperty(_messages.Message):
      """An additional property for a DetailsValueListEntry object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = _messages.StringField(1)
      value = _messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = _messages.MessageField('AdditionalProperty', 1, repeated=True)

  code = _messages.IntegerField(1, variant=_messages.Variant.INT32)
  details = _messages.MessageField('DetailsValueListEntry', 2, repeated=True)
  message = _messages.StringField(3)


class WebTrigger(_messages.Message):
  """Describes WebTrigger, could be used to connect web hooks to function.

  Enums:
    ProtocolValueValuesEnum: Protocol accepted by WebTrigger.

  Fields:
    protocol: Protocol accepted by WebTrigger.
    url: [Output only] The deployed url for the function.
  """

  class ProtocolValueValuesEnum(_messages.Enum):
    """Protocol accepted by WebTrigger.

    Values:
      HTTP: HTTP protocol
    """
    HTTP = 0

  protocol = _messages.EnumField('ProtocolValueValuesEnum', 1)
  url = _messages.StringField(2)


encoding.AddCustomJsonEnumMapping(
    StandardQueryParameters.FXgafvValueValuesEnum, '_1', '1',
    package=u'cloudfunctions')
encoding.AddCustomJsonEnumMapping(
    StandardQueryParameters.FXgafvValueValuesEnum, '_2', '2',
    package=u'cloudfunctions')
encoding.AddCustomJsonFieldMapping(
    StandardQueryParameters, 'f__xgafv', '$.xgafv',
    package=u'cloudfunctions')
