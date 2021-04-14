# Implementation

## Authentication

The Web Manager and the API use OAuth 2, as described in the FastAPI documentation. However, in addition to the OAuth 2 authentication with an Authorization header, the user can also authenticate with an Authorization cookie. In both cases the header or cookie value must be of the bearer format,

```shell
Bearer some_token_value
```

If both an Authorization header and cookie are present, the header is taken, irrespective of whether it's value is valid. To achieve this dual authentication functionality, FastAPI's `OAuth2PasswordBearer` is extended. See the `app.util.auth` module for the extension, `OAuth2TokenOrCookiePasswordBearer`.

## Roles and permissions

In an ideal world, user roles could be defined as an enumeration, and a user would have a list of roles. Alas, in case of the Web Manager this is not possible; there are roles that depend on parameters other than user. An example is the role of "proposal owner", which clearly depends on the proposal.

We therefore represent a role as an instance of a class extending an abstract base class `Role`. `Role` defines a single method, `is_assigned_to`, which checks whether a user has the role, and which must be implemented by all child classes.

So, for example, to check whether a user is an investigator of the proposal 2020-1-SCI-019, we could do something like the following.

```python
from app.util.role import Investigator

investigator = Investigator("2020-1-SCI-019")
is_investigator = investigator.is_assigned_to(user)
```

With permissions we face the same issue as for roles: Defining them as an enumeration would be nice, but there are permissions that depend on some parameter. For example, the permission to view a proposal depends on the proposal.

Hence we define a permission as an instance of a class extending an abstract base class `Permission`. The `Permission` class defines a single method, `is_permitted_for`, which checks whether a user has the permission, and which must be implemented for all child classes.

For example, to check whether a user may view a proposal, we can do something like this.

```python
from app.util.permission import ViewProposal

view_proposal = ViewProposal("2020-1-SCI-019", db)
may_view_proposal = view_proposal.is_permitted_for(user)
```

While this works, it's not convenient from a testing perspective, as you'd end up having to mock out every role and permission. For this reason the `User` class includes two methods, `has_role_of` and `is_permitted_to`, for checking roles and permissions. So the above examples can be rewritten as follows.

```python
from app.util.permission import ViewProposal
from app.util.role import Investigator

investigator = Investigator("2020-1-SCI-019", db)
is_investigator = user.has_role_of(investigator)

view_proposal = ViewProposal("2020-1-SCI-019", db)
may_view_proposal = user.is_permitted_to(view_proposal)
```

In most cases more than one rule needs to be checked and the user is required to have at least one of a list of permissions. The `User` class therefore also has a method `has_any_role_of`. This method should be used rather than calling `has_role_of` multiple times.

```python
from app.util.role import Administrator, Investigator

administrator = Administrator(db)
investigator = Investigator("2020-1-SCI-019", db)
is_admin_or_investigator = user.has_any_role_of([administrator, investigator])
```

The following roles are defined.

| Role                  | Description                                   | Parameters                      |
| --------------------- | --------------------------------------------- | ------------------------------- |
| Administrator         | Site administrator.                           |
| Investigator          | Investigator on a proposal.                   | Proposal code.                  |
| MaskCutter            | Cuts (MOS) masks.                             |
| PartnerTacMember      | Member of the TAC for a partner.              | Partner code (such as `IUCAA`). |
| PartnerTacChair       | Chair of the TAC for a partner.               | Partner code (such as `IUCAA`). |
| PrincipalContact      | Principal Contact for a proposal.             | Proposal code.                  |
| PrincipalInvestigator | Principal Investigator for a proposal.        | Proposal code.                  |
| ProposalTacChair      | Chair of a TAC from which a proposal requests time.                | Proposal code.                  |
| ProposalTacMember     | Member of a TAC from which a proposal requests time.               | Proposal code.                  |
| SaltAstronomer        | SALT Astronomer.                              |
| SaltEngineer          | Member of the SALT Technical Operations Team. |
| SaltOperator          | SALT Operator.                                |

## Error handling

The default FastAPI error handler for HTTP exceptions is overridden. For Authorization (status code 401) errors on a web page a redirection response to the login page (with the currently requested page as a Base64 encoded string as a `redirect` query parameter). For other errors on a web page an error page is returned. In both cases the status code of the error is used in the response.

For errors raised during an API call a JSON object with a `detail` property is returned. Again the error's status code is used.

The error handler distinguishes between web pages and API calls by checking the request path. It assumes that a request is an API call if and only if the path starts with `api/` or `/api/`.
