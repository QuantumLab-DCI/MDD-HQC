"""Service helpers that run optional LLM-backed interaction analysis on generated UVL."""

import logging
from contextvars import ContextVar
from threading import Event
from typing import Dict, Optional, Any

from app.services.interaction.contracts import InteractionInput, InteractionReport
from app.models.uvl import UVL
from app.services.interaction.analyzers.uvl_completeness import UvlCompletenessAnalyzer
from app.services.interaction.providers.factory import get_provider
from app.services.interaction.questions import build_questions_from_missing, generate_pim_to_psm_questions, parse_llm_questions
from app.services.interaction.analyzers.pim_to_psm_consistency import PimToPsmConsistencyAnalyzer


logger = logging.getLogger(__name__)

cancellation_context: ContextVar[Event | None] = ContextVar(
    "cancellation_context", default=None
)


def run_interaction(
    payload: InteractionInput, provider: Optional[str] = None
) -> InteractionReport:
    """Runs the UVL interaction analysis with the selected provider and returns its report."""
    
    cancellation_event = cancellation_context.get()
    if cancellation_event and cancellation_event.is_set():
        raise RuntimeError("Operation cancelled by user.")

    llm_provider = get_provider(provider)
    analyzer = UvlCompletenessAnalyzer(llm_provider)
    analysis = analyzer.analyze(payload)

    if cancellation_event and cancellation_event.is_set():
        raise RuntimeError("Operation cancelled by user.")

    # 1. Intentar obtener las preguntas generadas dinámicamente por la IA
    raw_questions = analysis.get("questions", [])
    if raw_questions:
        questions = parse_llm_questions(raw_questions)
    else:
        # Fallback de respaldo en caso de que la respuesta del LLM venga sin el campo 'questions'
        questions = build_questions_from_missing(analysis.get("missing", []))

    logger.debug("Interaction analysis result: %s", analysis)
    logger.info(
        "Interaction questions generated: provider=%s, question_count=%s",
        provider or "configured-default",
        len(questions),
    )

    return InteractionReport(questions=questions, proposals=[])

def run_pim_to_psm_interaction(payload: InteractionInput, provider: Optional[str] = None) -> InteractionReport:
    llm_provider = get_provider(provider)
    analyzer = PimToPsmConsistencyAnalyzer(llm_provider)
    analysis = analyzer.analyze_psm(payload)

    # Generar preguntas guiadas en base a los faltantes
    questions = generate_pim_to_psm_questions(analysis)

    return InteractionReport(
        analysis=analysis,
        questions=questions,
        provider=provider or "default"
    )

def apply_user_answers(uvl: UVL, answers: Dict[str, Any]) -> Dict[str, Any]:
    proposals: List[Dict[str, str]] = []

    if isinstance(answers, dict):
        for question_id, selected_option in answers.items():
            # 1. Ignorar si la clave no es una pregunta (ej. si vienen claves como 'path', 'detail', 'uvl_content')
            key_str = str(question_id).lower()
            if key_str in ("path", "detail", "uvl_content", "output_uvl") or not selected_option:
                continue

            selected_text = str(selected_option).strip()

            # 2. Ignorar si el valor es un diccionario, un path, o código UVL completo
            if (
                not selected_text 
                or selected_text.lower() == "none"
                or selected_text.startswith("/") 
                or selected_text.startswith("{") 
                or "features" in selected_text 
                or "mandatory" in selected_text
            ):
                continue

            # 3. Sanitización limpia del nombre de la característica UVL
            feature_name = (
                selected_text.replace(" ", "")
                .replace("-", "_")
                .replace("+", "Plus")
                .replace("#", "Sharp")
            )

            # Snippet identado sin duplicar la palabra 'mandatory'
            uvl_snippet = (
                f"  {feature_name}\n"
                f"    {{\n"
                f'      kind "implementation"\n'
                f'      provider "{selected_text}"\n'
                f"    }}"
            )

            proposals.append({
                "id": f"prop_{question_id}",
                "title": feature_name,
                "snippet": uvl_snippet,
                "provider": selected_text,
            })

    base_uvl_content = ""
    if hasattr(uvl, "create_file_content"):
        base_uvl_content = uvl.create_file_content()
    elif hasattr(uvl, "FILE_NAME") and uvl.FILE_NAME.exists():
        base_uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

    return {
        "final_uvl": base_uvl_content,
        "proposals": proposals
    }


def apply_psm_answers(path: str, answers: dict) -> dict:
    """Mock temporal para la fase PIM->PSM que simula la recepción exitosa de respuestas."""
    logger.info("Respuestas PIM->PSM recibidas para %s: %s", path, answers)
    return {
        "status": "success",
        "message": "Answers accepted temporarily without modifying the model",
        "path": path,
        "answers": answers
    }
