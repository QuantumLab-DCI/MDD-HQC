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

    # Lista de claves reservadas del sistema a ignorar OBLIGATORIAMENTE
    SYSTEM_KEYS = {
        "detail",
        "answers",
        "output_uvl",
        "uvl_content",
        "path",
        "missing",
        "questions",
    }

    if isinstance(answers, dict):
        # Si answers viene anidado como {"answers": {...}}, lo extraemos
        actual_answers = answers.get("answers", answers) if isinstance(answers.get("answers"), dict) else answers

        for question_id, selected_option in actual_answers.items():
            key_str = str(question_id).strip()
            
            # 1. Ignorar si es una clave del sistema (como 'detail')
            if key_str.lower() in SYSTEM_KEYS or not selected_option:
                continue

            selected_text = str(selected_option).strip()

            # 2. Ignorar valores vacíos, paths, JSONs o mensajes del sistema
            if (
                not selected_text
                or selected_text.lower() in ("none", "null")
                or selected_text.startswith("/")
                or selected_text.startswith("{")
                or selected_text.startswith("[")
                or "features" in selected_text
                or "Respuestas recibidas" in selected_text
            ):
                continue

            # 3. Formatear el Título (ej. "q_programming" -> "Programming")
            raw_title = key_str.replace("q_", "")
            card_title = raw_title[0].upper() + raw_title[1:] if raw_title else key_str

            # 4. Sanitizar la opción seleccionada para el snippet UVL
            feature_option = (
                selected_text.replace(" ", "")
                .replace("-", "_")
                .replace("+", "Plus")
                .replace("#", "Sharp")
            )

            # 5. Construir snippet individual identado
            uvl_snippet = (
                f"  {card_title}\n"
                f"    mandatory\n"
                f"      {feature_option}\n"
                f"        {{\n"
                f'          kind "implementation"\n'
                f'          provider "{selected_text}"\n'
                f"        }}"
            )

            # Agregamos cada tarjeta individual a la lista
            proposals.append({
                "id": f"prop_{key_str}",
                "title": card_title,       # "Programming", "Integration_model", etc.
                "snippet": uvl_snippet,    # Código UVL individual
                "provider": selected_text, # "Qiskit", "API REST", etc.
            })

    base_uvl_content = ""
    try:
        if hasattr(uvl, "create_file_content"):
            base_uvl_content = uvl.create_file_content()
        elif hasattr(uvl, "FILE_NAME") and getattr(uvl, "FILE_NAME", None) and uvl.FILE_NAME.exists():
            base_uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")
    except Exception:
        base_uvl_content = ""

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
