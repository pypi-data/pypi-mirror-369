import requests

from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.exceptions import ClientError


class RayClientMixin(BaseClient):
    def get_job(self, pk):
        path = f'jobs/{pk}/'
        return self._get(path)

    def list_jobs(self):
        path = 'jobs/'
        return self._get(path)

    def list_job_logs(self, pk):
        path = f'jobs/{pk}/logs/'
        return self._get(path)

    def tail_job_logs(self, pk, stream_timeout=10):
        if self.long_poll_handler:
            raise ClientError(400, '"tail_job_logs" does not support long polling')

        path = f'jobs/{pk}/tail_logs/'
        url = self._get_url(path)
        headers = self._get_headers()

        try:
            # Use shorter timeout for streaming to prevent hanging
            response = self.requests_session.get(
                url, headers=headers, stream=True, timeout=(self.timeout['connect'], stream_timeout)
            )
            response.raise_for_status()

            # Set up streaming with timeout handling
            try:
                for line in response.iter_lines(decode_unicode=True, chunk_size=1024):
                    if line:
                        yield f'{line}\n'
            except requests.exceptions.ChunkedEncodingError:
                # Connection was interrupted during streaming
                raise ClientError(503, f'Log stream for job {pk} was interrupted')
            except requests.exceptions.ReadTimeout:
                # Read timeout during streaming
                raise ClientError(408, f'Log stream for job {pk} timed out after {stream_timeout}s')

        except requests.exceptions.ConnectTimeout:
            raise ClientError(
                408, f'Failed to connect to log stream for job {pk} (timeout: {self.timeout["connect"]}s)'
            )
        except requests.exceptions.ReadTimeout:
            raise ClientError(408, f'Log stream for job {pk} read timeout ({stream_timeout}s)')
        except requests.exceptions.ConnectionError as e:
            if 'Connection refused' in str(e):
                raise ClientError(503, f'Agent connection refused for job {pk}')
            else:
                raise ClientError(503, f'Agent connection error for job {pk}: {str(e)[:100]}')
        except requests.exceptions.HTTPError as e:
            raise ClientError(e.response.status_code, f'HTTP error streaming logs for job {pk}: {e}')
        except Exception as e:
            raise ClientError(500, f'Unexpected error streaming logs for job {pk}: {str(e)[:100]}')

    def get_node(self, pk):
        path = f'nodes/{pk}/'
        return self._get(path)

    def list_nodes(self):
        path = 'nodes/'
        return self._get(path)

    def get_task(self, pk):
        path = f'tasks/{pk}/'
        return self._get(path)

    def list_tasks(self):
        path = 'tasks/'
        return self._get(path)

    def get_serve_application(self, pk):
        path = f'serve_applications/{pk}/'
        return self._get(path)

    def list_serve_applications(self):
        path = 'serve_applications/'
        return self._get(path)

    def delete_serve_application(self, pk):
        path = f'serve_applications/{pk}/'
        return self._delete(path)
