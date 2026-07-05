# EventHub

A backend API for a simplified event ticketing platform built with Django and Django REST Framework.

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

## Authentication

Register a new user:

```json
POST /api/register/
{
    "email": "user@example.com",
    "password": "yourpassword"
}
```

Login to get a token:

```json
POST /api/login/
{
    "username": "user@example.com",
    "password": "yourpassword"
}
```

Include the token in all authenticated requests:

```
Authorization: Token <your_token>
```

## API Endpoints

### Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/events/` | No | List all events |
| POST | `/api/events/` | Yes | Create an event |
| GET | `/api/events/{id}/` | No | Retrieve an event |
| PUT | `/api/events/{id}/` | Yes | Update an event |
| PATCH | `/api/events/{id}/` | Yes | Partial update an event |
| DELETE | `/api/events/{id}/` | Yes | Delete an event |

**Query Parameters:**
- `?status=upcoming` — filter by status (upcoming, ongoing, completed, cancelled)
- `?venue=NIMHANS` — filter by venue (case-insensitive partial match)

### Reservations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reservations/` | Yes | List your reservations |
| POST | `/api/reservations/` | Yes | Create a reservation (deducts seats) |
| GET | `/api/reservations/{id}/` | Yes | Retrieve a reservation |
| PUT | `/api/reservations/{id}/` | Yes | Update a reservation |
| PATCH | `/api/reservations/{id}/` | Yes | Partial update a reservation |
| DELETE | `/api/reservations/{id}/` | Yes | Delete a reservation |
| POST | `/api/reservations/{id}/cancel/` | Yes | Cancel a reservation (restores seats) |

**Query Parameters:**
- `?event_id=1` — filter reservations by event

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register a new user (returns token) |
| POST | `/api/login/` | Login with credentials (returns token) |

## Constraints

- A user can only have **one active event** (upcoming or ongoing) at a time.
- A user can only have **one confirmed reservation per event**.
- Overbooking is prevented — reservation fails if seats are insufficient.

## Design Decisions

### User authentication with token-based auth
I used Django REST Framework's `TokenAuthentication` to keep auth simple and stateless. When a user registers, a token is created and returned immediately so they can start using the API without a separate login step. The `created_by` field on Event and `user` field on Reservation link each resource to its owner, enabling per-user filtering and permission checks.
