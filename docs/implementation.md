# Implementation

## Authentication

The Web Manager and the API use OAuth 2, as described in the FastAPI documentation. However, in addition to the OAuth 2 authentication with an Authorization header, the user can also authenticate with an Authorization cookie. In both cases the header or cookie value must be of the bearer format,

```shell
Bearer some_token_value
```

If both an Authorization header and cookie are present, the header is taken, irrespective of whether it's value is valid. To achieve this dual authentication functionality, FastAPI's `OAuth2PasswordBearer` is extended. See the `app.util.auth` module for the extension, `OAuth2TokenOrCookiePasswordBearer`.
