# Repo convention and outline

## Outline
- adapter: handle adapter to third party service
- api: expose api
- config: environment we get from env var and will be config on deployment
- internal: service implement
- middleware: server middleware, currently handle context middleware and send notify to our slack in case any api error

## Convention

### DB
- For connection to db, always use next(get_db_session()), on api that need connection to db (use Depend(get_db_session)). We use get_db_session to ensure no connection is left open

### Middleware
- Slack middleware is put inside router due to starlette problem with request and body streaming problem, we cannot put them inside other middleware. For any further customize of router, split function that handle send slack error to another function and reuse it
- Context middleware handle a wrapper that could be reuse in api end point, but the best usage of it for inside functino should be a dictionary map string to object

### Coding
- Variable name should be lower snake case
- Constant name should be upper snake case
- Class name should be naming with camel case
- Private function or attribute should be prefix with _ or __
