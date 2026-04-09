"""
Database Seed Data Module
==========================
Seeds the database with initial data from the skill ontology
and job market datasets.
"""

import json
from pathlib import Path
from backend.database.db_setup import SessionLocal, Skill, SkillCategory, init_db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def seed_skills():
    """Seed the skills table from ontology JSON."""
    ontology_path = DATA_DIR / "skill_ontology.json"
    if not ontology_path.exists():
        print("⚠️ skill_ontology.json not found")
        return

    with open(ontology_path, "r", encoding="utf-8") as f:
        ontology = json.load(f)

    db = SessionLocal()

    try:
        # Seed categories
        for cat_key, cat_data in ontology.get("categories", {}).items():
            existing = db.query(SkillCategory).filter(
                SkillCategory.name == cat_key
            ).first()

            if not existing:
                category = SkillCategory(
                    name=cat_key,
                    display_name=cat_data.get("display_name", cat_key),
                    skill_count=len(cat_data.get("skills", {}))
                )
                db.add(category)

            # Seed skills
            for skill_key, skill_info in cat_data.get("skills", {}).items():
                existing_skill = db.query(Skill).filter(
                    Skill.canonical_name == skill_info.get("canonical", skill_key)
                ).first()

                if not existing_skill:
                    skill = Skill(
                        canonical_name=skill_info.get("canonical", skill_key),
                        category=cat_key,
                        subcategory=skill_info.get("subcategory", ""),
                        difficulty=skill_info.get("difficulty", "intermediate"),
                        market_weight=skill_info.get("market_weight", 5),
                        estimated_hours=skill_info.get("estimated_hours", 40),
                        onet_code=skill_info.get("onet_code", "")
                    )
                    db.add(skill)

        db.commit()
        skill_count = db.query(Skill).count()
        cat_count = db.query(SkillCategory).count()
        print(f"✅ Seeded {skill_count} skills across {cat_count} categories")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
    finally:
        db.close()


def seed_all():
    """Run all seeding operations."""
    init_db()
    seed_skills()
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    seed_all()
