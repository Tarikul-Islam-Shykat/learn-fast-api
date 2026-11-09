# Section 5 — Authorization: What Can This User Do?

> **The rule:** a valid login identifies the caller; every protected database operation must still check whether that user owns the record or has the required role.

Section 4 created users, hashed passwords, and bearer tokens. Section 5 uses `get_current_user` to protect Todos, enforce ownership, and add admin-only operations.

## 1. Authentication versus authorization

```text
Authentication: Is this token valid, and which user does it identify?
Authorization: Is this user allowed to perform this action on this record?
```

A valid JWT alone does not mean a user can access every Todo. The route must include an ownership or role check.

## 2. Protect a route with `get_current_user`

The dependency decodes the bearer token and returns the matching user from the database. A protected route asks FastAPI to inject that user:

```python
@router.get("/todos")
def get_my_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ...
```

The client sends the token in this header:

```http
Authorization: Bearer <access_token>
```

If the token is missing, invalid, or expired, the request should fail with `401 Unauthorized` before the route's database operation runs.

## 3. Assign ownership when creating a Todo

The API should assign the owner from the authenticated user, not trust an `owner_id` sent by the client.

```python
todo = models.Todo(
    title=todo_request.title,
    description=todo_request.description,
    priority=todo_request.priority,
    owner_id=current_user.id,
)
db.add(todo)
db.commit()
db.refresh(todo)
```

This prevents a caller from creating a Todo under another user's ID by changing request JSON.

## 4. Filter every user's Todo queries by ownership

### Get only the current user's Todos

```python
todos = (
    db.query(models.Todo)
    .filter(models.Todo.owner_id == current_user.id)
    .all()
)
```

### Get one Todo only if it belongs to the current user

```python
todo = (
    db.query(models.Todo)
    .filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == current_user.id,
    )
    .first()
)
```

Apply the same two conditions when updating or deleting: match both the Todo ID and the current user's ID. If no owned row matches, return `404 Not Found`. This keeps one user from reading, changing, or deleting another user's Todo.

```text
Valid bearer token
  -> get_current_user returns the user
  -> query by both todo_id and owner_id
       -> match: read / update / delete
       -> no match: 404 Not Found
```

## 5. Protect update and delete operations

For **PUT**, first find the row using both `todo_id` and `current_user.id`. If found, copy the editable request fields onto it and commit. If no row matches, return 404. The update body should not be allowed to change `owner_id`.

For **DELETE**, use the same ownership-filtered lookup. If found, call `db.delete(todo)` and `db.commit()`, then return `204 No Content`. If no owned row matches, return 404.

These checks are authorization: the API knows the caller's identity and enforces what records they can act on.

## 6. Admin router and role-based access

An admin route can list all Todos or delete any Todo, but it must check the authenticated user's role first.

```text
valid token -> get_current_user -> role == "admin"? -> allow / reject
```

Use a reusable dependency such as `get_current_admin_user` that:

1. Depends on `get_current_user`.
2. Checks `current_user.role`.
3. Raises `403 Forbidden` when the user is authenticated but not an admin.
4. Returns the user when the role check succeeds.

Then inject that dependency into the admin router. Authentication failure is `401`; a logged-in user lacking permission is `403`.

```text
Bearer token
  -> authenticate user
       -> invalid token: 401 Unauthorized
       -> valid token: check role
            -> admin: allow admin operation
            -> not admin: 403 Forbidden
```

Do not let public registration choose its own role. Assign a normal role by default; create or promote admins through a trusted process.

## 7. User profile and password change assignment

The assignment adds endpoints for the authenticated user:

- **Get my user data:** return the current user's public fields, not their password hash.
- **Change my password:** verify the submitted current password against the stored hash; if valid, hash the new password, save it, and commit. Do not store or return plaintext passwords.

The current user must come from `get_current_user`, not an ID supplied by the caller. That way a user can only read or change their own account.

## 8. Try the protected API

First request a token from `/auth/token` using the username and password form fields. Then send the returned token with protected requests:

```bash
TOKEN="paste-access-token-here"

curl -i http://127.0.0.1:8000/todos \
  -H "Authorization: Bearer $TOKEN"
```

To check ownership, use two different users: create Todos as each user, then try to read or change the other user's Todo ID. The protected query should not return another user's row.

## Section 5 checkpoint

Try to explain these without looking above:

1. Why doesn't a valid token grant access to every Todo?
2. Why should the server set `owner_id` from `current_user.id`?
3. Which two conditions should an ordinary user's Todo lookup check?
4. What is the difference between `401` for invalid credentials and `403` for insufficient permissions?
5. Why should an admin check be a reusable dependency?
6. What steps happen when a user changes their password?

## Official references

- [FastAPI OAuth2, password hashing, and bearer JWTs](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [FastAPI dependency injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519.html)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725.html)

## Related keywords

- **Current user (`current_user`):** the database user identified by the verified bearer token.
- **Ownership check:** the query condition that requires both the requested Todo ID and the owner's user ID to match.
- **Data isolation:** keeping one user's records separate from another user's records.
- **IDOR:** Insecure Direct Object Reference; a flaw where changing an ID lets a user access someone else's record.
- **Role-based access control (RBAC):** granting actions based on a role such as `admin`.
- **Least privilege:** give each account only the permissions it needs; normal registration must not grant admin rights.
- **401 Unauthorized:** the caller is not authenticated with valid credentials.
- **403 Forbidden:** the caller is authenticated but lacks permission for the action.
- **404 Not Found:** no matching record is available to this user; ownership-aware queries can avoid exposing another user's record.
- **204 No Content:** successful update or delete response with no body.

## Questions you can ask while learning

- Why must the server set `owner_id` from `current_user.id` instead of trusting the request body?
- Why should a user's read, update, and delete queries filter by both `todo_id` and `owner_id`?
- How does an ownership filter prevent an IDOR flaw?
- When should a route return 401, 403, 404, or 204?
- Why should admin access use a separate reusable role-check dependency?
- Which fields are safe to return from a user profile, and why must `hashed_password` stay private?
