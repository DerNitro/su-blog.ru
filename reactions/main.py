from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
import os
import hashlib

# Configure logging in DEBUG mode as requested
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("reactions-service")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/reactions.db")
logger.info(f"Using database URL: {DATABASE_URL}")

os.makedirs("/app/data", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ReactionModel(Base):
    __tablename__ = "reactions"

    slug = Column(String, primary_key=True, index=True)
    likes = Column(Integer, default=0)
    heart = Column(Integer, default=0)
    fire = Column(Integer, default=0)
    clap = Column(Integer, default=0)
    poop = Column(Integer, default=0)
    views = Column(Integer, default=0)


class UserReactionModel(Base):
    __tablename__ = "user_reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, index=True)
    client_id = Column(String, index=True)
    reaction_type = Column(String, index=True)


class UserViewModel(Base):
    __tablename__ = "user_views"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, index=True)
    client_id = Column(String, index=True)


Base.metadata.create_all(bind=engine)
try:
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(reactions)"))
        columns = [row[1] for row in result.fetchall()]
        if columns and "views" not in columns:
            logger.info("Migrating database: adding missing 'views' column...")
            conn.execute(text("ALTER TABLE reactions ADD COLUMN views INTEGER DEFAULT 0"))
            conn.commit()
            logger.info("Column 'views' successfully added to reactions table.")

        result_ur = conn.execute(text("PRAGMA table_info(user_reactions)"))
        columns_ur = [row[1] for row in result_ur.fetchall()]
        if columns_ur and "reaction_type" not in columns_ur:
            logger.info("Migrating database: adding missing 'reaction_type' column to user_reactions...")
            conn.execute(text("ALTER TABLE user_reactions ADD COLUMN reaction_type VARCHAR"))
            conn.commit()
            logger.info("Column 'reaction_type' successfully added to user_reactions table.")
except Exception as e:
    logger.error(f"Migration error: {e}", exc_info=True)

logger.info("Database tables initialized successfully.")

app = FastAPI(title="Su-Blog Reactions & Views API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Completed request: {request.method} {request.url} -> Status: {response.status_code}")
    return response


class ReactionRequest(BaseModel):
    type: str


def get_client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0] if forwarded else (request.client.host if request.client else "unknown")
    user_agent = request.headers.get("user-agent", "")
    return hashlib.sha256(f"{client_ip}:{user_agent}".encode()).hexdigest()


@app.get("/api/reactions")
def get_reactions(slug: str, request: Request):
    logger.info(f"DEBUG: Fetching stats for slug: {slug}")
    db = SessionLocal()
    try:
        client_id = get_client_id(request)
        user_vote = db.query(UserReactionModel).filter(
            UserReactionModel.slug == slug,
            UserReactionModel.client_id == client_id
        ).first()
        user_reaction = user_vote.reaction_type if user_vote else None
        user_voted = user_vote is not None

        reaction = db.query(ReactionModel).filter(ReactionModel.slug == slug).first()
        if not reaction:
            logger.debug(f"DEBUG: No stats found in DB for slug: {slug}")
            return {
                "slug": slug,
                "likes": 0,
                "heart": 0,
                "fire": 0,
                "clap": 0,
                "poop": 0,
                "views": 0,
                "user_reacted": user_voted,
                "user_reaction": user_reaction
            }
        logger.debug(f"DEBUG: Found stats in DB for slug {slug}: likes={reaction.likes}, heart={reaction.heart}, fire={reaction.fire}, clap={reaction.clap}, poop={reaction.poop}, views={reaction.views}, user_reaction={user_reaction}")
        return {
            "slug": reaction.slug,
            "likes": reaction.likes,
            "heart": reaction.heart,
            "fire": reaction.fire,
            "clap": reaction.clap,
            "poop": reaction.poop,
            "views": reaction.views,
            "user_reacted": user_voted,
            "user_reaction": user_reaction,
        }
    except Exception as e:
        logger.error(f"ERROR querying DB for slug {slug}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/stats")
def get_stats():
    logger.info("DEBUG: Fetching global statistics for all articles")
    db = SessionLocal()
    try:
        reactions = db.query(ReactionModel).all()
        result = []
        for r in reactions:
            total_reactions = r.likes + r.heart + r.fire + r.clap + r.poop
            result.append({
                "slug": r.slug,
                "likes": r.likes,
                "heart": r.heart,
                "fire": r.fire,
                "clap": r.clap,
                "poop": r.poop,
                "views": r.views,
                "total_reactions": total_reactions
            })
        result.sort(key=lambda x: (x["views"], x["total_reactions"]), reverse=True)
        return result
    except Exception as e:
        logger.error(f"ERROR fetching global stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/views")
def increment_view(slug: str, request: Request):
    logger.info(f"DEBUG: Incrementing view count for slug: {slug}")
    db = SessionLocal()
    try:
        client_id = get_client_id(request)
        existing_view = db.query(UserViewModel).filter(
            UserViewModel.slug == slug,
            UserViewModel.client_id == client_id
        ).first()

        reaction = db.query(ReactionModel).filter(ReactionModel.slug == slug).first()
        if not reaction:
            logger.debug(f"DEBUG: Creating new record for slug {slug} with 0 views")
            reaction = ReactionModel(slug=slug, likes=0, heart=0, fire=0, clap=0, poop=0, views=0)
            db.add(reaction)
            db.commit()
            db.refresh(reaction)

        if not existing_view:
            user_view = UserViewModel(slug=slug, client_id=client_id)
            db.add(user_view)
            reaction.views += 1
            db.commit()
            db.refresh(reaction)
            logger.info(f"DEBUG: Successfully incremented view for {slug}, total views: {reaction.views}")
        else:
            logger.debug(f"DEBUG: Client {client_id} already viewed slug {slug}. View count not incremented.")

        return {"slug": reaction.slug, "views": reaction.views}
    except Exception as e:
        db.rollback()
        logger.error(f"ERROR updating views for slug {slug}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/reactions")
def add_reaction(slug: str, body: ReactionRequest, request: Request):
    logger.info(f"DEBUG: Adding/toggling reaction type '{body.type}' for slug: {slug}")
    if body.type not in ["likes", "heart", "fire", "clap", "poop"]:
        logger.warning(f"WARNING: Invalid reaction type requested: {body.type}")
        raise HTTPException(status_code=400, detail="Invalid reaction type")

    db = SessionLocal()
    try:
        client_id = get_client_id(request)
        existing_vote = db.query(UserReactionModel).filter(
            UserReactionModel.slug == slug,
            UserReactionModel.client_id == client_id
        ).first()

        reaction = db.query(ReactionModel).filter(ReactionModel.slug == slug).first()
        if not reaction:
            logger.debug(f"DEBUG: Creating new record for slug {slug} for reaction")
            reaction = ReactionModel(slug=slug, likes=0, heart=0, fire=0, clap=0, poop=0, views=0)
            db.add(reaction)
            db.commit()
            db.refresh(reaction)

        user_reaction_result = None

        if existing_vote:
            if existing_vote.reaction_type == body.type:
                # Toggle off (remove reaction)
                logger.info(f"DEBUG: Removing existing reaction '{body.type}' for client {client_id} on slug {slug}")
                if body.type == "likes":
                    reaction.likes = max(0, reaction.likes - 1)
                elif body.type == "heart":
                    reaction.heart = max(0, reaction.heart - 1)
                elif body.type == "fire":
                    reaction.fire = max(0, reaction.fire - 1)
                elif body.type == "clap":
                    reaction.clap = max(0, reaction.clap - 1)
                elif body.type == "poop":
                    reaction.poop = max(0, reaction.poop - 1)

                db.delete(existing_vote)
                db.commit()
                db.refresh(reaction)
                user_reaction_result = None
            else:
                # Switch reaction
                old_type = existing_vote.reaction_type
                logger.info(f"DEBUG: Switching reaction from '{old_type}' to '{body.type}' for client {client_id} on slug {slug}")
                
                # Decrement old
                if old_type == "likes":
                    reaction.likes = max(0, reaction.likes - 1)
                elif old_type == "heart":
                    reaction.heart = max(0, reaction.heart - 1)
                elif old_type == "fire":
                    reaction.fire = max(0, reaction.fire - 1)
                elif old_type == "clap":
                    reaction.clap = max(0, reaction.clap - 1)
                elif old_type == "poop":
                    reaction.poop = max(0, reaction.poop - 1)

                # Increment new
                if body.type == "likes":
                    reaction.likes += 1
                elif body.type == "heart":
                    reaction.heart += 1
                elif body.type == "fire":
                    reaction.fire += 1
                elif body.type == "clap":
                    reaction.clap += 1
                elif body.type == "poop":
                    reaction.poop += 1

                existing_vote.reaction_type = body.type
                db.commit()
                db.refresh(reaction)
                user_reaction_result = body.type
        else:
            # Add new reaction
            logger.info(f"DEBUG: Adding new reaction '{body.type}' for client {client_id} on slug {slug}")
            if body.type == "likes":
                reaction.likes += 1
            elif body.type == "heart":
                reaction.heart += 1
            elif body.type == "fire":
                reaction.fire += 1
            elif body.type == "clap":
                reaction.clap += 1
            elif body.type == "poop":
                reaction.poop += 1

            user_reaction = UserReactionModel(slug=slug, client_id=client_id, reaction_type=body.type)
            db.add(user_reaction)
            db.commit()
            db.refresh(reaction)
            user_reaction_result = body.type

        logger.info(
            f"DEBUG: Successfully processed reaction for {slug}. New counts: likes={reaction.likes}, heart={reaction.heart}, fire={reaction.fire}, clap={reaction.clap}, poop={reaction.poop}, user_reaction={user_reaction_result}"
        )
        return {
            "slug": reaction.slug,
            "likes": reaction.likes,
            "heart": reaction.heart,
            "fire": reaction.fire,
            "clap": reaction.clap,
            "poop": reaction.poop,
            "views": reaction.views,
            "user_reacted": user_reaction_result is not None,
            "user_reaction": user_reaction_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"ERROR processing reaction '{body.type}' for slug {slug}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
