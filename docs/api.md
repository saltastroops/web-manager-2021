In addition to the Web Manager website, there is an API for interacting with SALT data more programmatically.

## Authentication

Most of the API functionality is only accessible if you are authenticated. This requires you to include an authentication token in the API request. You can request such a token from the `/api/token` route.

```shell
curl -X POST -F "username=john" -F "password=doe" /api/token
```

The username and password (`john` and `doe` in this example) are the same username and password you'd use for logging into the Web Manager website.

!!! note
    As shown in the example, the username and password must be submitted as form data, not as a JSON object. This is required by the OAuth2 standard.

The token is returned as a JSON object of the form `{"access_token": "some_token_value", "token_type": "bearer"}`, and yiu can get the token value from the `access_token` property. Once you have the token value (`abcd1234`, say), you can use it by passing it in an HTTP header.

```shell
curl -H "Authorization: Bearer abcd1234" /api/secret/resource
```

Remember that an authentication token effectively is a password - store it safely, and don't share it.

!!! warning
    The token has a finite lifetime; it expires 24 hours after being issued.
