# ADR-001: Backend and Database Selection

## Status

Accepted

## Context

NovaFab needs a backend capable of:

- Managing factory-related data
- Exposing APIs to the frontend
- Handling authentication and authorization
- Running analytical queries
- Connecting machine learning and AI services
- Supporting future deployment as a web application

The system also requires a relational database because factory data contains
relationships between entities such as machines, production records,
maintenance events, quality inspections, and alerts.

---

## Decision

NovaFab will use:

- Django as the backend framework
- Django REST Framework for API development
- PostgreSQL as the primary relational database

---

## Why Django?

Django was selected because NovaFab requires more than a simple API.

The application will eventually need:

- Authentication
- Authorization
- Database models
- Database migrations
- Admin capabilities
- API endpoints
- Validation
- Security features
- Integration with machine learning services

Django provides these capabilities within one mature backend ecosystem.

The project also benefits from Django's ORM because factory entities have
many relationships that need to be represented clearly.

---

## Why PostgreSQL?

PostgreSQL was selected because NovaFab contains structured relational data.

Examples include:

- Factory → Machines
- Machines → Sensor Records
- Machines → Maintenance Records
- Production Runs → Quality Inspections
- Quality Inspections → Defects
- Machines → Alerts

PostgreSQL provides:

- Strong relational integrity
- Primary keys and foreign keys
- Constraints
- Transactions
- Aggregation and analytical SQL
- Indexing
- Good support for large structured datasets

These capabilities are important for both application development and
data analysis.

---

## Alternatives Considered

### FastAPI

FastAPI is an excellent framework for API-focused applications.

However, NovaFab also requires authentication, administration, ORM-based
data management, migrations, and a full web application.

Django provides these capabilities as part of a larger integrated framework.

FastAPI could still be useful later for an isolated ML inference service
if the architecture requires it.

---

### Flask

Flask is lightweight and flexible.

However, many capabilities that NovaFab requires would need to be assembled
through additional libraries and project-specific configuration.

Django provides a more integrated foundation for the current application.

---

### MongoDB

MongoDB could store flexible document-oriented data.

However, the core NovaFab data model contains many structured relationships
between entities.

A relational database provides stronger integrity guarantees and makes
relationship-based analytical queries more natural.

MongoDB may still be considered for specific unstructured or document
storage requirements if a future requirement justifies it.

---

### SQLite

SQLite is useful for local development and small applications.

However, NovaFab is designed around PostgreSQL because the project needs
a production-style relational database environment and more realistic
database capabilities.

---

## Trade-offs

### Advantages

- Integrated Django ecosystem
- Strong relational data modeling
- Built-in migrations
- Authentication and authorization support
- Powerful SQL analytics
- Good foundation for deployment
- Clear separation between application and data layers

### Limitations

- Django can be heavier than a minimal API framework
- PostgreSQL requires a running database service
- The application needs careful database indexing as data volume grows
- ML inference workloads may eventually need separate services

---

## Consequence

NovaFab will initially use a single Django application connected to
PostgreSQL.

Additional services will only be introduced when a real requirement
justifies them.

The architecture will avoid adding technologies simply for complexity
or resume value.