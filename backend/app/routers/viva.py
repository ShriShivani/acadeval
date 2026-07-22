import uuid
from fastapi import APIRouter, HTTPException

from app.dependencies import DB, CurrentStudent, CurrentUser
from app.models.project import Project
from app.models.viva import VivaSession
from app.schemas.viva import VivaQuestion, VivaAnswerSubmit, VivaAnswerResult

router = APIRouter(tags=["Viva"])

# Phase 1 static question bank — Phase 2 replaces with Gemini generation
_STATIC_QUESTIONS: list[dict] = [
    {"questionId": "q1", "text": "What problem does your project solve and why is it important?", "category": "Problem Statement", "difficulty": "Easy"},
    {"questionId": "q2", "text": "Explain the overall system architecture of your project.", "category": "Architecture", "difficulty": "Medium"},
    {"questionId": "q3", "text": "What dataset did you use and how was it collected or prepared?", "category": "Data", "difficulty": "Medium"},
    {"questionId": "q4", "text": "Which algorithms or models did you use and why did you choose them?", "category": "Methodology", "difficulty": "Hard"},
    {"questionId": "q5", "text": "What were the key evaluation metrics and what results did you achieve?", "category": "Results", "difficulty": "Medium"},
    {"questionId": "q6", "text": "How does your project compare to existing solutions in this domain?", "category": "Literature", "difficulty": "Hard"},
    {"questionId": "q7", "text": "What are the main limitations of your current implementation?", "category": "Limitations", "difficulty": "Easy"},
    {"questionId": "q8", "text": "How would you scale this system to handle real-world deployment?", "category": "Scalability", "difficulty": "Hard"},
    {"questionId": "q9", "text": "What future improvements or research directions do you foresee?", "category": "Future Work", "difficulty": "Easy"},
    {"questionId": "q10", "text": "What was your specific contribution versus that of your team members?", "category": "Contribution", "difficulty": "Medium"},
]


@router.get("/viva/{project_id}/questions", response_model=list[VivaQuestion])
def get_viva_questions(project_id: str, current_user: CurrentStudent, db: DB):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.student_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create or return existing session
    session = (
        db.query(VivaSession)
        .filter(VivaSession.project_id == project.id)
        .order_by(VivaSession.created_at.desc())
        .first()
    )
    if not session:
        session = VivaSession(
            project_id=project.id,
            questions=_STATIC_QUESTIONS,
            answers=[],
            scores=[],
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return [VivaQuestion(**q) for q in session.questions]


@router.post("/viva/answer", response_model=VivaAnswerResult)
def submit_viva_answer(payload: VivaAnswerSubmit, current_user: CurrentStudent, db: DB):
    """
    Phase 1: Simple keyword-based scoring stub.
    Phase 2: Replace with Gemini-powered evaluation.
    """
    answer_lower = payload.answer.lower()
    word_count = len(answer_lower.split())

    # Simple heuristic scoring
    if word_count >= 80:
        score = 5
        feedback = "Excellent answer! Comprehensive coverage with strong technical depth."
    elif word_count >= 50:
        score = 4
        feedback = "Good answer. Could add more technical specifics or examples."
    elif word_count >= 30:
        score = 3
        feedback = "Adequate answer. Expand with more detail and concrete examples."
    elif word_count >= 15:
        score = 2
        feedback = "Partial answer. Missing key aspects — elaborate further."
    else:
        score = 1
        feedback = "Answer is too brief. Provide a detailed, structured response."

    return VivaAnswerResult(
        questionId=payload.questionId,
        score=score,
        maxScore=5,
        feedback=feedback,
        keyPoints=["Clarity of explanation", "Technical accuracy", "Real-world relevance"],
    )
