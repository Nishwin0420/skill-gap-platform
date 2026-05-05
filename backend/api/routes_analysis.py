"""
Analysis API Routes
====================
Core analysis endpoints for skill gap detection, employability prediction,
and full analysis pipeline.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
import json

from backend.nlp.skill_extractor import extract_skills, extract_skills_with_details
from backend.nlp.skill_normalizer import get_normalizer
from backend.nlp.tfidf_engine import get_tfidf_engine
from backend.nlp.resume_parser import extract_text_from_pdf, parse_resume_sections, extract_years_of_experience
from backend.models.skill_gap_engine import get_gap_engine
from backend.models.employability_predictor import get_predictor
from backend.models.learning_path_generator import get_path_generator
from backend.models.coding_platform_analyzer import get_platform_analyzer
from backend.models.skill_decay_analyzer import get_decay_analyzer
from backend.models.resume_optimizer import get_resume_optimizer
from backend.xai.explainer import get_explainer
from backend.database.db_setup import SessionLocal
from backend.database.crud import save_analysis, get_cohort_scores

router = APIRouter(prefix="/api", tags=["Analysis"])


# ====================================
# REQUEST MODELS
# ====================================
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Resume or input text")
    target_skills: List[str] = Field(..., min_length=1, description="Target role skills")
    experience: float = Field(default=0, ge=0, le=50)
    target_role: Optional[str] = None
    use_semantic: bool = False


class SkillExtractionRequest(BaseModel):
    text: str = Field(..., min_length=5)
    use_semantic: bool = False


class LearningPathRequest(BaseModel):
    missing_skills: List[str]
    user_skills: List[str] = []
    target_role: Optional[str] = None


class PlatformProfileRequest(BaseModel):
    resume_skills: List[str] = Field(..., description="Skills extracted from resume")
    leetcode: Optional[str] = Field(None, description="LeetCode username")
    codechef: Optional[str] = Field(None, description="CodeChef username")
    hackerrank: Optional[str] = Field(None, description="HackerRank username")
    codeforces: Optional[str] = Field(None, description="Codeforces username")
    github: Optional[str] = Field(None, description="GitHub username")


# ====================================
# CORE ANALYSIS ENDPOINT
# ====================================
@router.post("/analyze")
def analyze_user(data: AnalyzeRequest):
    """
    Full AI-powered analysis pipeline:
    1. NLP Skill Extraction
    2. Skill Normalization (O*NET + ESCO)
    3. Skill Gap Detection (weighted)
    4. ML Employability Prediction
    5. Learning Path Generation (DAG)
    6. XAI Explanations
    """
    try:
        normalizer = get_normalizer()
        gap_engine = get_gap_engine()
        predictor = get_predictor()
        path_gen = get_path_generator()
        explainer = get_explainer()
        tfidf = get_tfidf_engine()

        # Step 1: Extract skills from user text using NLP pipeline
        raw_user_skills = extract_skills(data.text, use_semantic=data.use_semantic)

        # Step 2: Normalize skills using ontology
        normalized_user = normalizer.normalize_skills(raw_user_skills)
        user_skills = [n["canonical"] for n in normalized_user]

        normalized_job = normalizer.normalize_skills(data.target_skills)
        job_skills = [n["canonical"] for n in normalized_job]

        if not user_skills:
            raise HTTPException(status_code=400, detail="No skills detected from input text")

        # Step 3: Skill Gap Analysis
        gap_analysis = gap_engine.analyze_gap(user_skills, job_skills)

        # Step 4: ML Employability Prediction
        prediction = predictor.generate_detailed_report(
            user_skills, job_skills, data.experience, gap_analysis
        )

        # Step 5: Learning Path Generation
        learning_path = path_gen.generate_path(
            gap_analysis["missing_skills"],
            user_skills=user_skills,
            target_role=data.target_role
        )
        path_summary = path_gen.get_path_summary(learning_path)
        timeline = path_gen.generate_timeline(learning_path)

        # Step 6: XAI Explanations
        explanation = explainer.explain_prediction(
            prediction, gap_analysis, user_skills, job_skills
        )

        # Step 7: TF-IDF Document Similarity
        jd_text = " ".join(data.target_skills)
        doc_similarity = tfidf.compute_similarity(data.text, jd_text)

        # Step 8: Skill Clustering
        clusters = gap_engine.cluster_skill_gaps(gap_analysis["missing_skills"])

        # Save to database
        try:
            db = SessionLocal()
            save_analysis(
                db,
                resume_skills=user_skills,
                job_skills=job_skills,
                result={
                    "match_percentage": gap_analysis["match_percentage"],
                    "employability_score": prediction.get("employability_score", 0),
                    "readiness_level": prediction.get("readiness_level", ""),
                    "gap_severity": gap_analysis["gap_severity"],
                    "missing_skills": gap_analysis["missing_skills"],
                    "target_role": data.target_role or ""
                }
            )
            db.close()
        except Exception:
            pass

        # Final Response
        return {
            "input_summary": {
                "experience": data.experience,
                "target_role": data.target_role,
                "skills_extraction_method": "multi-method NLP (PhraseMatcher + Regex + NER + TF-IDF)"
            },
            "extracted_skills": {
                "raw": raw_user_skills,
                "normalized": normalized_user,
                "count": len(user_skills)
            },
            "job_skills": {
                "raw": data.target_skills,
                "normalized": normalized_job,
                "count": len(job_skills)
            },
            "gap_analysis": gap_analysis,
            "employability": prediction,
            "learning_path": {
                "steps": learning_path,
                "summary": path_summary,
                "timeline": timeline
            },
            "skill_clusters": clusters,
            "document_similarity": doc_similarity,
            "explanation": explanation,
            "metadata": {
                "models_used": [
                    "spaCy NER + PhraseMatcher",
                    "TF-IDF Vectorizer",
                    "Random Forest Classifier",
                    "XGBoost Regressor",
                    "KNN",
                    "K-Means Clustering",
                    "networkx DAG"
                ],
                "data_sources": ["O*NET Taxonomy", "ESCO Framework", "Simulated Job Market"],
                "api_version": "2.0.0"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================
# FILE UPLOAD ANALYSIS
# ====================================
@router.post("/analyze-full")
async def analyze_full(
    resume: UploadFile = File(None),
    jd_file: UploadFile = File(None),
    job_description: str = Form(""),
    experience: float = Form(1),
    target_role: str = Form(""),
    # Optional coding platform usernames
    leetcode_username: str = Form(""),
    codechef_username: str = Form(""),
    hackerrank_username: str = Form(""),
    codeforces_username: str = Form(""),
    github_username: str = Form(""),
):
    """
    Full analysis with PDF file upload support.
    Accepts resume PDF + job description PDF/text.
    """
    try:
        normalizer = get_normalizer()
        gap_engine = get_gap_engine()
        predictor = get_predictor()
        path_gen = get_path_generator()
        explainer = get_explainer()

        resume_text = ""
        jd_text = ""

        # Parse resume PDF
        if resume:
            resume_text = extract_text_from_pdf(resume.file)

        # Parse JD PDF
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file.file)

        # Combine JD inputs
        final_jd_text = jd_text if jd_text else job_description

        if not resume_text:
            raise HTTPException(status_code=400, detail="No resume text extracted")
        if not final_jd_text:
            raise HTTPException(status_code=400, detail="No job description provided")

        # Extract and normalize skills
        user_skills_raw = extract_skills(resume_text)
        job_skills_raw = extract_skills(final_jd_text)

        user_normalized = normalizer.normalize_skills(user_skills_raw)
        job_normalized = normalizer.normalize_skills(job_skills_raw)

        user_skills = [n["canonical"] for n in user_normalized]
        job_skills = [n["canonical"] for n in job_normalized]

        # Auto-extract experience from resume
        if experience <= 0:
            experience = extract_years_of_experience(resume_text)

        # Full analysis pipeline
        gap_analysis = gap_engine.analyze_gap(user_skills, job_skills)
        prediction = predictor.generate_detailed_report(
            user_skills, job_skills, experience, gap_analysis
        )
        learning_path = path_gen.generate_path(
            gap_analysis["missing_skills"], user_skills, target_role
        )
        path_summary = path_gen.get_path_summary(learning_path)
        explanation = explainer.explain_prediction(
            prediction, gap_analysis, user_skills, job_skills
        )

        # Resume sections parsing
        resume_sections = parse_resume_sections(resume_text)

        # Save to database for history tracking
        try:
            db = SessionLocal()
            save_analysis(
                db,
                resume_skills=user_skills,
                job_skills=job_skills,
                result={
                    "match_percentage": gap_analysis["match_percentage"],
                    "employability_score": prediction.get("employability_score", 0),
                    "readiness_level": prediction.get("readiness_level", ""),
                    "gap_severity": gap_analysis["gap_severity"],
                    "missing_skills": gap_analysis["missing_skills"],
                    "target_role": target_role
                }
            )
            db.close()
        except Exception:
            pass

        # Optional: Coding platform proficiency
        skill_proficiency = None
        has_platforms = any([
            leetcode_username, codechef_username,
            hackerrank_username, codeforces_username, github_username
        ])
        if has_platforms:
            try:
                platform_analyzer = get_platform_analyzer()
                platform_result = platform_analyzer.analyze_profiles(
                    resume_skills=user_skills,
                    leetcode=leetcode_username or None,
                    codechef=codechef_username or None,
                    hackerrank=hackerrank_username or None,
                    codeforces=codeforces_username or None,
                    github=github_username or None,
                )
                skill_proficiency = platform_result
            except Exception:
                pass

        response = {
            "resume_skills": user_skills,
            "job_skills": job_skills,
            "experience_detected": experience,
            "resume_sections": {
                k: v[:200] for k, v in resume_sections.items() if k != "full_text"
            },
            "gap_analysis": gap_analysis,
            "employability": prediction,
            "learning_path": {
                "steps": learning_path,
                "summary": path_summary
            },
            "explanation": explanation,
        }
        if skill_proficiency:
            response["skill_proficiency"] = skill_proficiency

        # ──────────────────────────────────────────────────
        # FEATURE 1: Skill Decay & Freshness Modeling
        # ──────────────────────────────────────────────────
        try:
            decay_analyzer = get_decay_analyzer()
            matched_skills = gap_analysis.get("matched_skills", [])
            if matched_skills:
                decay_result = decay_analyzer.analyze(
                    matched_skills=matched_skills,
                    experience_text=resume_sections.get("experience", ""),
                    projects_text=resume_sections.get("projects", ""),
                )
                response["skill_decay"] = decay_result
        except Exception:
            pass

        # ──────────────────────────────────────────────────
        # FEATURE 2: Peer Cohort Benchmarking
        # ──────────────────────────────────────────────────
        try:
            current_score = prediction.get("employability_score", 0)
            db2 = SessionLocal()
            cohort_scores = get_cohort_scores(db2, target_role=target_role or None)
            db2.close()

            # Exclude current score if it was already saved
            cohort_size = len(cohort_scores)

            if cohort_size >= 1:
                # Percentile: percentage of scores strictly below current
                scores_below = sum(1 for s in cohort_scores if s < current_score)
                percentile = round((scores_below / cohort_size) * 100, 1)
                avg_cohort = round(sum(cohort_scores) / cohort_size, 1)
                top_score = max(cohort_scores)

                response["cohort_benchmarking"] = {
                    "percentile": percentile,
                    "cohort_size": cohort_size,
                    "avg_cohort_score": avg_cohort,
                    "top_score": top_score,
                    "your_score": round(current_score, 1),
                    "target_role": target_role or "General",
                    "rank_label": (
                        "Top Performer" if percentile >= 80
                        else "Above Average" if percentile >= 60
                        else "Average" if percentile >= 40
                        else "Below Average"
                    ),
                }
            else:
                response["cohort_benchmarking"] = {
                    "percentile": None,
                    "cohort_size": 0,
                    "message": "You're among the first to analyze this role! Run more analyses to unlock benchmarking.",
                    "your_score": round(current_score, 1),
                    "target_role": target_role or "General",
                }
        except Exception:
            pass

        # ──────────────────────────────────────────────────
        # FEATURE 3: ATS Resume Optimizer
        # ──────────────────────────────────────────────────
        try:
            optimizer = get_resume_optimizer()
            matched_skills_for_ats = gap_analysis.get("matched_skills", [])
            if matched_skills_for_ats:
                # Build skill -> category map from normalizer for better verb selection
                normalizer_ref = get_normalizer()
                skill_cat_map = {
                    s: normalizer_ref.get_skill_category(s)
                    for s in matched_skills_for_ats
                }
                ats_result = optimizer.optimize(
                    matched_skills=matched_skills_for_ats,
                    resume_sections=resume_sections,
                    jd_text=final_jd_text,
                    skill_categories=skill_cat_map,
                )
                response["ats_optimization"] = ats_result
        except Exception:
            pass

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================
# SKILL EXTRACTION ENDPOINT
# ====================================
@router.post("/extract-skills")
def extract_skills_endpoint(data: SkillExtractionRequest):
    """Extract and normalize skills from text using NLP pipeline."""
    normalizer = get_normalizer()

    raw_skills = extract_skills(data.text, use_semantic=data.use_semantic)
    detailed = extract_skills_with_details(data.text, use_semantic=data.use_semantic)
    normalized = normalizer.normalize_skills(raw_skills)

    return {
        "extracted_skills": raw_skills,
        "detailed_extraction": detailed,
        "normalized_skills": normalized,
        "total_found": len(raw_skills)
    }


# ====================================
# CODING PLATFORM PROFICIENCY ENDPOINT
# ====================================
@router.post("/skill-proficiency")
def analyze_skill_proficiency(data: PlatformProfileRequest):
    """
    Analyze coding platform profiles to determine per-skill proficiency.
    Accepts optional usernames for LeetCode, CodeChef, HackerRank,
    Codeforces and GitHub.  Returns strength (0-100), level, and evidence
    for every resume skill.
    """
    try:
        analyzer = get_platform_analyzer()
        result = analyzer.analyze_profiles(
            resume_skills=data.resume_skills,
            leetcode=data.leetcode,
            codechef=data.codechef,
            hackerrank=data.hackerrank,
            codeforces=data.codeforces,
            github=data.github,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================
# SKILL ONTOLOGY ENDPOINT
# ====================================
@router.get("/skill-ontology")
def get_skill_ontology():
    """Get the complete skill taxonomy (O*NET + ESCO)."""
    normalizer = get_normalizer()
    categories = {}

    for cat_key, cat_data in normalizer.ontology.get("categories", {}).items():
        skills = []
        for skill_info in cat_data.get("skills", {}).values():
            skills.append({
                "name": skill_info["canonical"],
                "difficulty": skill_info.get("difficulty", "intermediate"),
                "market_weight": skill_info.get("market_weight", 5),
                "category": cat_key
            })
        categories[cat_key] = {
            "display_name": cat_data.get("display_name", cat_key),
            "skills": skills,
            "count": len(skills)
        }

    return {
        "total_skills": sum(len(c["skills"]) for c in categories.values()),
        "total_categories": len(categories),
        "categories": categories
    }


# ====================================
# LEARNING PATH ENDPOINT
# ====================================
@router.post("/generate-learning-path")
def generate_learning_path(data: LearningPathRequest):
    """Generate a personalized learning path for missing skills."""
    path_gen = get_path_generator()

    path = path_gen.generate_path(
        data.missing_skills,
        user_skills=data.user_skills,
        target_role=data.target_role
    )
    summary = path_gen.get_path_summary(path)
    timeline = path_gen.generate_timeline(path)

    return {
        "learning_path": path,
        "summary": summary,
        "timeline": timeline
    }


# ====================================
# XAI EXPLANATION ENDPOINT
# ====================================
@router.get("/xai/explain/{analysis_id}")
def get_xai_explanation(analysis_id: int):
    """Get XAI explanations for a past analysis."""
    from backend.database.crud import get_analysis_by_id

    db = SessionLocal()
    analysis = get_analysis_by_id(db, analysis_id)
    db.close()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        result = json.loads(analysis.analysis_result) if analysis.analysis_result else {}
        return {
            "analysis_id": analysis_id,
            "match_percentage": analysis.match_percentage,
            "employability_score": analysis.employability_score,
            "readiness_level": analysis.readiness_level,
            "gap_severity": analysis.gap_severity,
            "created_at": str(analysis.created_at)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
