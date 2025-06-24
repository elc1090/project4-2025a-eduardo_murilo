from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    create_engine,
    event,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from ai import generate_component_info

load_dotenv()

app = Flask(__name__)

CORS(app)

engine = create_engine("sqlite:///uinify.db", echo=False)
conn = engine.connect()

Session = sessionmaker(bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    description = Column(Text(), nullable=True)
    framework = Column(String(50), nullable=False)  # vue, react, html/css
    category = Column(
        String(50), nullable=False
    )  # ui, forms, navigation, cards, data, layout
    tags = Column(Text(), nullable=True)  # Separate tags with commas
    inputType = Column(String(50), nullable=False)  # html, vue
    includeTailwind = Column(Boolean, nullable=False, default=False)
    code = Column(Text(), nullable=False)  # actual content
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="components")

    def __repr__(self):
        return f"<Component(title='{self.title}', framework='{self.framework}', category='{self.category}')>"

    def to_dict(self):
        tags_list = []
        if self.tags:
            tags_list = [tag.strip() for tag in self.tags.split(",") if tag.strip()]

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "framework": self.framework,
            "category": self.category,
            "tags": tags_list,
            "inputType": self.inputType,
            "includeTailwind": self.includeTailwind,
            "code": self.code,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    components = relationship("Component", cascade="all, delete", back_populates="user")

    def __repr__(self):
        return f"<User(name='{self.username}', password='{self.password}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


Base.metadata.create_all(engine)


@app.route("/users", methods=["GET"])
def users_get():
    with Session() as session:
        try:
            users = session.query(User).all()
            return jsonify([user.to_dict() for user in users]), 200
        except Exception as e:
            return jsonify(error=str(e)), 500


@app.route("/login", methods=["POST"])
def login():
    r = request.get_json()

    for key in ["username", "password"]:
        if key not in r:
            return jsonify(error=f"Missing '{key}' key."), 400

    with Session() as session:
        try:
            existing_user = (
                session.query(User).filter_by(username=r["username"]).first()
            )

            if existing_user is None:
                new_user = User(username=r["username"], password=r["password"])
                session.add(new_user)
                session.commit()
                return jsonify(new_user.to_dict()), 200
            else:
                if existing_user.password == r["password"]:
                    return jsonify(existing_user.to_dict()), 200
                else:
                    return jsonify(error="Invalid password."), 401

        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/user", methods=["POST"])
def user_post():
    r = request.get_json()

    for key in ["username", "password"]:
        if key not in r:
            return jsonify(error=f"Missing '{key}' key."), 400

    with Session() as session:
        try:
            user = User(username=r["username"], password=r["password"])
            session.add(user)
            session.commit()
            return jsonify(user.to_dict()), 200
        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/user/<int:id>", methods=["GET"])
def user_get(id):
    with Session() as session:
        try:
            user = session.query(User).filter_by(id=id).first()
            if user is None:
                return jsonify(error=f"User '{id}' not found."), 404
            return user.to_dict(), 200
        except Exception as e:
            return jsonify(error=str(e)), 500


@app.route("/user/<int:id>", methods=["DELETE"])
def user_delete(id):
    with Session() as session:
        try:
            user = session.get(User, id)
            if user is None:
                return jsonify(error=f"User '{id}' not found."), 404
            session.delete(user)
            session.commit()
            return jsonify(user.to_dict()), 200
        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/user/<int:id>/components", methods=["GET"])
def user_components_get(id):
    with Session() as session:
        try:
            user = session.get(User, id)
            if user is None:
                return jsonify(error=f"User '{id}' not found."), 404
            return jsonify([component.to_dict() for component in user.components]), 200
        except Exception as e:
            return jsonify(error=str(e)), 500


@app.route("/components", methods=["GET"])
def components_get():
    with Session() as session:
        try:
            components_db = session.query(Component).all()
            components = [component_db.to_dict() for component_db in components_db]

            for component, component_db in zip(components, components_db):
                component["author"] = component_db.user.username

            return jsonify(components), 200
        except Exception as e:
            return jsonify(error=str(e)), 500


@app.route("/component", methods=["POST"])
def component_post():
    r = request.get_json()

    required_keys = ["user_id", "title", "framework", "category", "inputType", "code"]
    for key in required_keys:
        if key not in r:
            return jsonify(error=f"Missing '{key}' key."), 400

    with Session() as session:
        try:
            tags = r.get("tags", "")
            if isinstance(tags, list):
                tags = ", ".join(tags)

            component = Component(
                title=r["title"],
                description=r.get("description", ""),
                framework=r["framework"],
                category=r["category"],
                tags=tags,
                inputType=r["inputType"],
                includeTailwind=r.get("includeTailwind", False),
                code=r["code"],
                user_id=r["user_id"],
            )
            session.add(component)
            session.commit()
            return jsonify(component.to_dict()), 200
        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/component/<int:id>", methods=["GET"])
def component_get(id):
    with Session() as session:
        try:
            component = session.query(Component).filter_by(id=id).first()
            if component is None:
                return jsonify(error=f"Component '{id}' not found."), 404
            return jsonify(component.to_dict()), 200
        except Exception as e:
            return jsonify(error=str(e)), 500


@app.route("/component/<int:id>", methods=["PUT"])
def component_put(id):
    r = request.get_json()

    required_keys = ["title", "framework", "category", "inputType", "code"]
    for key in required_keys:
        if key not in r:
            return jsonify(error=f"Missing '{key}' key."), 400

    with Session() as session:
        try:
            component = session.get(Component, id)
            if component is None:
                return jsonify(error=f"Component '{id}' not found."), 404

            # Handle tags - convert list to comma-separated string if needed
            tags = r.get("tags", "")
            if isinstance(tags, list):
                tags = ", ".join(tags)

            # Update all fields
            component.title = r["title"]
            component.description = r.get("description", "")
            component.framework = r["framework"]
            component.category = r["category"]
            component.tags = tags
            component.inputType = r["inputType"]
            component.includeTailwind = r.get("includeTailwind", False)
            component.code = r["code"]

            session.commit()
            return jsonify(component.to_dict()), 200
        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/component/<int:id>", methods=["DELETE"])
def component_delete(id):
    with Session() as session:
        try:
            component = session.get(Component, id)
            if component is None:
                return jsonify(error=f"Component '{id}' not found."), 404
            session.delete(component)
            session.commit()
            return jsonify(component.to_dict()), 200
        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


@app.route("/component/info", methods=["POST"])
def component_info():
    r = request.get_json()
    info = generate_component_info(r["code"])
    return jsonify(info), 200


@app.route("/auth/google", methods=["POST"])
def google_auth():
    r = request.get_json()

    required_keys = ["email", "name", "google_id"]
    for key in required_keys:
        if key not in r:
            return jsonify(error=f"Missing '{key}' key."), 400

    with Session() as session:
        try:
            # Try to find existing user by email (Google users use email as username)
            existing_user = session.query(User).filter_by(username=r["email"]).first()

            if existing_user is None:
                # Create new user for Google authentication
                # Use email as username and a placeholder password (since Google handles auth)
                new_user = User(
                    username=r["email"],
                    password=f"google_auth_{r['google_id']}"  # Placeholder password
                )
                session.add(new_user)
                session.commit()

                user_data = new_user.to_dict()
                user_data["name"] = r["name"]  # Add Google name to response
                return jsonify(user_data), 200
            else:
                # Return existing user
                user_data = existing_user.to_dict()
                user_data["name"] = r["name"]  # Add Google name to response
                return jsonify(user_data), 200

        except Exception as e:
            session.rollback()
            return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
