from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from Powers import LOGGER as log

DB_URI = "postgres://u3cf4evmcicphe:p62d2c021e1ff71dd5d335e57a84db7a2f0ef6506647a8cfd34594a91948a3d44@c7u1tn6bvvsodf.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d9k6e1julog4bj"


if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

def start() -> scoped_session:
    engine = create_engine(DB_URI, client_encoding="utf8")
    log.info("[PostgreSQL] Connecting to database......")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
try:
    SESSION = start()
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit()

log.info("[PostgreSQL] Connection successful, session started.")
