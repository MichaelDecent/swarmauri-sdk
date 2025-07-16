![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/autoapi/">
        <img src="https://img.shields.io/pypi/dm/autoapi" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/autoapi/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/autoapi.svg"/>
    </a>
    <a href="https://pypi.org/project/autoapi/">
        <img src="https://img.shields.io/pypi/pyversions/autoapi" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/autoapi/">
        <img src="https://img.shields.io/pypi/l/autoapi" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/autoapi/">
        <img src="https://img.shields.io/pypi/v/autoapi?label=autoapi&color=green" alt="PyPI - autoapi"/>
    </a>
</p>

---

# AutoAPI

Automatic REST and JSON-RPC route generation for SQLAlchemy models.

## AutoAPI class

`AutoAPI` scans the supplied SQLAlchemy base and creates CRUD endpoints for each model. Those handlers are also exposed as JSON-RPC methods. Additional RPC functions can be registered manually via the `rpc` dictionary.

```python
from autoapi import AutoAPI
from peagen.orm import Base, UserModel
from sqlalchemy.orm import Session

# example session provider
from myproject.db import SessionLocal

def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api = AutoAPI(
    base=Base,                 # SQLAlchemy declarative base
    get_db=get_session,        # callable returning a Session
    include={UserModel},       # expose only selected models
    authorise=None,            # optional RPC authorisation hook
    prefix="/api",            # router prefix
)
```

Parameters

- `base` – Declarative base containing your models (e.g. `peagen.orm.Base`).
- `get_db` – Session provider used by REST handlers and the RPC gateway.
- `include` – Optional set of models to expose. Defaults to all models registered on `base`.
- `authorise` – Callable to authorise RPC requests: `authorise(method, request)` should return `True` to allow execution.
- `prefix` – Prefix applied to the generated `APIRouter`.

## FastAPI integration

```python
from fastapi import FastAPI
from peagen.orm import Base, UserModel
from autoapi import AutoAPI
from myproject.db import SessionLocal

# session dependency
def get_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api = AutoAPI(base=Base, get_db=get_session, include={UserModel}, prefix="/api")

app = FastAPI()
app.include_router(api.router)
```

## Register CRUD and RPC routes

The `api` instance automatically exposes CRUD routes for every included model. For `UserModel` the following endpoints become available under `/api/users`:

- `POST /api/users` – create
- `GET /api/users/{id}` – read
- `PATCH /api/users/{id}` – update
- `DELETE /api/users/{id}` – delete
- `GET /api/users` – list

You can also register custom RPC handlers. They receive the RPC parameters and an active `Session`:

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

# RPC handler
def greet(user_id: str, db: Session) -> dict[str, str]:
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404)
    return {"message": f"Hello {user.username}"}

api.rpc["users.greet"] = greet
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
