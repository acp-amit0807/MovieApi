# MovieApi

A simple ASP.NET Core 8 REST API for filtering movies by various criteria.

## Architecture Diagram

```
+-----------------------+      +----------------------+
|    Client/Browser     |<---> |   MoviesController   |
+-----------------------+      +----------------------+ 
                                     |
                                     v
                            +-----------------------+
                            |     MovieService      |
                            +-----------------------+
                                     |
                          +--------------------------+
                          |    InMemory Data Store   |
                          +--------------------------+
```

## Components

- **MoviesController** – handles HTTP requests, parameter binding, and basic validation.
- **MovieService** – contains business logic for filtering movies using supplied criteria.
- **Models** – domain objects such as `Movie` and `MovieFilter` used across layers.
- **Program.cs** – configures services, middleware, and Swagger for API documentation.

## Data Flow

1. Client issues `GET /api/movies` with optional query parameters.
2. `MoviesController` binds query to `MovieFilter` and validates.
3. Controller invokes `MovieService.GetMovies(filter)`.
4. Service applies filters on an in-memory list and returns results.
5. Controller serialises result to JSON and returns `200 OK`.

## Security Considerations

- HTTPS redirection is enabled.
- No authentication/authorization yet—consider adding JWT or OAuth2.
- Input validation prevents basic injection and malformed data.

## Deployment Model

- Application can run natively on Docker or in Azure App Service.
- Configuration via `appsettings.json` and environment variables.
 
