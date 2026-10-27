"""Explicit administrator CLI; never auto-enrol a user based on browser claims."""

import argparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_engine
from app.models import Membership, School, User


def main():
    parser = argparse.ArgumentParser(description="Provision a school and a Cognito user membership")
    parser.add_argument("--school-name", required=True)
    parser.add_argument("--school-id", help="Existing school UUID; omit to create a school")
    parser.add_argument("--subject", required=True, help="Verified Cognito user sub")
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", choices=["teacher", "admin"], default="teacher")
    args = parser.parse_args()
    with Session(get_engine()) as db:
        if args.school_id:
            school = db.get(School, args.school_id)
            if not school:
                parser.error("School does not exist")
        else:
            school = School(name=args.school_name)
            db.add(school)
            db.flush()
        user = db.scalar(select(User).where(User.subject == args.subject))
        if not user:
            user = User(subject=args.subject, name=args.name)
            db.add(user)
            db.flush()
        membership = db.get(Membership, (user.id, school.id))
        if membership:
            membership.role = args.role
        else:
            db.add(Membership(user_id=user.id, school_id=school.id, role=args.role))
        db.commit()
        print(f"Membership ready. School ID: {school.id}")


if __name__ == "__main__":
    main()
