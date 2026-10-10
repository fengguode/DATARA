"""Bounded in-memory upload handler for the private local FIT preview."""

from __future__ import annotations

from io import BytesIO

from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.files.uploadedfile import InMemoryUploadedFile

from datara.intake import MAX_FILE_BYTES

PREVIEW_ROUTE = "/fit/preview/"
REQUEST_OVERHEAD_BYTES = 128 * 1024


class PreviewUploadHandlerMiddleware:
    """Install the memory-only handler before CSRF parses this one route."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info == PREVIEW_ROUTE:
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            request.upload_handlers = [BoundedMemoryUploadHandler(request)]
        return self.get_response(request)


class BoundedMemoryUploadHandler(FileUploadHandler):
    """Accept at most one bounded file and never spool its bytes to disk."""

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        maximum = MAX_FILE_BYTES + REQUEST_OVERHEAD_BYTES
        if content_length is None or content_length > maximum:
            self.request._datara_upload_error = "request_too_large"
            return None
        return None

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        if getattr(self.request, "_datara_upload_error", None):
            raise StopUpload(connection_reset=False)
        self._file_count = getattr(self, "_file_count", 0) + 1
        if self._file_count > 1:
            self.request._datara_upload_error = "too_many_files"
            raise StopUpload(connection_reset=False)
        self._buffer = bytearray()

    def receive_data_chunk(self, raw_data, start):
        if len(self._buffer) + len(raw_data) > MAX_FILE_BYTES:
            self.request._datara_upload_error = "file_too_large"
            self._buffer.clear()
            raise StopUpload(connection_reset=False)
        self._buffer.extend(raw_data)
        return None

    def file_complete(self, file_size):
        content = bytes(self._buffer)
        uploaded = InMemoryUploadedFile(
            BytesIO(content), self.field_name, self.file_name,
            self.content_type, len(content), self.charset, self.content_type_extra,
        )
        del content
        del self._buffer
        return uploaded
