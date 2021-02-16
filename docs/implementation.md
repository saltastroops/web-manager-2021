# Implementation

## Authentication

The Web Manager and the API use OAuth 2, as described in the FastAPI documentation. However, in addition to the OAuth 2 authentication with an Authorization header, the user can also authenticate with an Authorization cookie. In both cases the header or cookie value must be of the bearer format,

```shell
Bearer some_token_value
```

If both an Authorization header and cookie are present, the header is taken, irrespective of whether it's value is valid. To achieve this dual authentication functionality, FastAPI's `OAuth2PasswordBearer` is extended. See the `app.util.auth` module for the extension, `OAuth2TokenOrCookiePasswordBearer`.

## Error handling

The default FastAPI error handler for HTTP exceptions is overridden. For Authorization (status code 401) errors on a web page a redirection response to the login page (with the currently requested page as a Base64 encoded string as a `redirect` query parameter). For other errors on a web page an error page is returned. In both cases the status code of the error is used in the response.

For errors raised during an API call a JSON object with a `detail` property is returned. Again the error's status code is used.

The error handler distinguishes between web pages and API calls by checking the request path. It assumes that a request is an API call if and only if the path starts with `api/` or `/api/`.
