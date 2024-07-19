
### Getting Started

You will need to [install redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/).  I chose to [install from source](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-from-source/) on my MacBook Pro (Apple M1) running OS 14.5.

There are fixtures available for sample `Condition` (condition.json) and `Group` (group.json) data.  But you will need to use the Django Admin to manually add `School`/`User` records.  You should also associate any "School" or "Student" `User` accounts with the appropriate "School" or "Student" `Group`, respectively.

```
# Start the development server
python manage.py runserver

# Run unittests
python manage.py test
```

Django Admin @ https://127.0.0.1:8000/admin/

GraphiQL for manually testing queries @ http://127.0.0.1:8000/graphql/

### Sample GraphQL Queries (for use within the GraphiQL interface)

Use the tokenAuth mutation to obtain a JWT that you can use when accessing restricted endpoints.

```
# Query
mutation TokenAuth($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
    payload
    refreshExpiresIn
  }
}

# Variables
{
  "username": "...",
  "password": "...",
}
```

Be sure to set the following in the Headers pane when calling any of the endpoints in the rules schema.
```
{
  "Authorization": "JWT insert-token-returned-by-tokenAuth-mutation"
}
```







