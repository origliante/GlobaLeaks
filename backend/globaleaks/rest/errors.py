# -*- coding: UTF-8
#
#   errors
#   ******
#
# Here shall go all the error messages that a GLBackend can generate.
# GLException is the class inherit by the other Errors, and define the
# class variables expected in the Error handler routine

from cyclone.web import HTTPError

class GLException(HTTPError):
    reason = "GLTypesError not set"
    log_message = "GLException"
    error_code = 0
    status_code = 500 # generic Server error
    
    def __init__(self):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s: <<%s>> (%d) HTTP:%d" % (
            self.__class__.__name__, self.reason,
            self.error_code, self.status_code
        )

class InvalidInputFormat(GLException):
    """
    The expected format described in the REST specification is not
    respected by the data body in the HTTP request.
    """
    error_code = 10
    status_code = 406 # Not Acceptable

    def __init__(self, wrong_source):
        self.reason = "Invalid Input Format [%s]" % wrong_source
        self.arguments = [wrong_source]


class TokenFailure(GLException):
    """
    Some kind of reason to reject a submission Token
    """
    error_code = 11
    status_code = 401

    def __init__(self, reason):
        self.reason = ("Unacceptable condition for usage of Token: %s" % reason)


class ContextIdNotFound(GLException):
    """
    The context_id used do not exist in the database.
    """
    reason = "Not found a Context with the specified ID"
    error_code = 12
    status_code = 404 # Not Found


class TipIdNotFound(GLException):
    """
    The Tip Id requested do not exists in the database.
    """
    reason = "Not found a Tip with the specified ID"
    error_code = 13
    status_code = 404 # Not Found


class TipReceiptNotFound(GLException):
    """
    The WhisleBlower receipt is not related to any of the whistleblower tips
    """
    reason = "Not found a Whistleblower Tip with the specified ID"
    error_code = 14
    status_code = 404 # Not Found


# UNUSED ERROR CODE 15 16 17 18 HERE!


class DatabaseIntegrityError(GLException):
    """
    A query on the database resulted in an integrity error
    """
    reasone = "A query on the database resulted in an integrity error"
    error_code = 19
    status_code = 404 # Not Found

    def __init__(self, dberror):
        self.arguments = [dberror]

class ReceiverIdNotFound(GLException):
    """
    The Receiver ID requested do not exists in the database.
    """
    reason = "No Receiver was found for the specified ID"
    error_code = 20
    status_code = 404 # Not Found


# UNUSED ERROR CODE 21 HERE!


class SubmissionFailFields(GLException):
    """
    If the fields required values and format type do not fit the requirement, this
    error is raised. The Client has to enforce as possible the Input Format, when this
    Client output validation fail, this error may happen.
    """
    error_code = 22
    status_code = 412 # Precondition Failed

    def __init__(self, wrong_field):
        self.reason = "Submission do not validate the input fields [%s]" % wrong_field
        self.arguments = [wrong_field]


# UNUSED ERROR CODE 23 24 HERE!


class ForbiddenOperation(GLException):
    """
    Receiver or Whistleblower has tried one operation not permitted by their privileges
    """
    reason = "Operation Forbidden"
    error_code = 25
    status_code = 401 # Unauthorized


class FileIdNotFound(GLException):
    """
    The requested file Id do not exist in the database
    """
    reason = "Not found a File with the specified ID "
    error_code = 26
    status_code = 404 # Not Found


# UNUSED ERROR CODE 28 HERE!


class InvalidAuthentication(GLException):
    """
    An invalid request was presented
    """
    reason = "Authentication Failed"
    error_code = 29
    status_code = 401 # Unauthorized


class NotAuthenticated(GLException):
    """
    The user attempted to access a not-authorized request. The output messages
    may contain reasons about the Authentication failure, but they are specify
    only if users has show knowledge of good credentials.
    """
    error_code = 30
    status_code = 412 # Precondition Failed
    reason = "Not Authenticated"


class InternalServerError(GLException):
    """
    Error in interaction with the OS
    """
    error_code = 31
    status_code = 500

    def __init__(self, details):
        self.reason = "Internal Server Error (%s)" % details
        self.arguments = [details]


# UNUSED ERROR CODE 32 33 HERE!


class InvalidOldPassword(GLException):
    """
    Receiver or Node required the old password equal to the current password,
    before change with a new secret.
    """
    reason = "The specified old password is not valid"
    error_code = 34
    status_code = 406


class CommentNotFound(GLException):
    """
    A Comment UUID expected has not been found
    """
    reason = "The specified comment was not found"
    error_code = 35
    status_code = 404


class InvalidHostSpecified(GLException):
    """
    The host delcared by the client 'Host:' field is not between
    the list of the acceptable hosts
    """
    reason = "The specified host do not match a configured one"
    error_code = 36
    status_code = 417 # Expectation Fail


class TorNetworkRequired(GLException):
    """
    A connection receiver not via Tor network is required to
    be enforced with anonymity
    """
    reason = "Resource can be accessed only within Tor network"
    error_code = 37
    status_code = 417 # Expectation Fail


class ReservedFileName(GLException):
    """
    The files uploaded in the static file directory, are also used for Receivers portrait
    and Node Logo.
    """
    reason = "The file uploaded has a reserved name"
    error_code = 38
    status_code = 403 # Forbidden


class FileTooBig(GLException):
    """
    Raised by GLHTTPConnection, when the uploaded file is bigger than acceptable
    """
    error_code = 39
    status_code = 400 # Bad Request

    def __init__(self, size_limit):
        self.reason = ("Provided file upload overcomes size limits (%d Mb)" %
                       size_limit)
        self.arguments = [size_limit]


class PGPKeyInvalid(GLException):
    """
    The provided PGP key has an invalid format and can't be imported
    """
    reason = "The proposed PGP key can't be imported"
    error_code = 40
    status_code = 406


# UNUSED ERROR CODE 41 42 43 44 45 HERE!


class InvalidTipTimeToLive(GLException):
    """
    The provided tip_timetolive contains weird values
    """
    reason = "Invalid timerange provided for Tip time to live"
    error_code =  46
    status_code = 406

# UNUSED ERROR CODE 47 48 HERE!

class FileRequiredMissing(GLException):
    """
    A submission has been finalized without a file, and
    the context enforce the presence.
    """
    reason = "A file attachment is required to complete the submission"
    error_code =  49
    status_code = 406


class ExtendTipLifeNotEnabled(GLException):
    """
    Ability to postpone expiration date is not enabled in the node
    """
    reason = "This node do not permit expiration date extensions"
    error_code =  50
    status_code = 403


class StaticFileNotFound(GLException):
    """
    It has been requested an operation on a non existent static file
    """
    reason = "Requested an operation on a non existent static file"
    error_code = 51
    status_code = 404


class LangFileNotFound(GLException):
    """
    It has been requested an operation on a non existent language file
    """
    reason = "Requested an operation on a non existent language file"
    error_code = 52
    status_code = 404


class DirectoryTraversalError(GLException):
    """
    Blocked file operation out of the expected path
    """
    reason = "Blocked file operation out of the expected path"
    error_code = 53
    status_code = 403


class SubmissionDisabled(GLException):
    reason = "Submissions are not possible right now"
    error_code = 52
    status_code = 503 # Service not available

# UNUSED ERROR CODE 53, 54 HERE!

class FloodException(GLException):
    error_code = 55
    status_code = 403

    def __init__(self, seconds):
        self.reason = "Chill out for another %s seconds"
        self.arguments = [seconds]


# Remind: the FloodException are not used at the moment
class SubmissionFlood(FloodException):
    error_code = 56
    status_code = 403

    def __init__(self, seconds):
        self.reason = "Too many submissions in %d seconds" % seconds
        self.arguments = [seconds]


class FileUploadFlood(FloodException):
    error_code = 57
    status_code = 403

    def __init__(self, seconds):
        self.reason = "Too many file uploads in %d seconds" % seconds
        self.arguments = [seconds]


class FieldIdNotFound(GLException):
    error_code = 58
    status_code = 404
    reason = "Not found a Field with the specified ID"


class ModelNotFound(GLException):
    """
    Error class for a generic model
    """
    error_code = 59
    status_code = 404

    def __init__(self, model=None):
        if model is None:
            self.reason = "Model not found"
        else:
            self.reason = "Model of type {} has not been found".format(model)


class TipMessagesNotFound(GLException):
    error_code = 60
    status_code = 404
    reason = "Not found Tip Messages for the specified ID"
