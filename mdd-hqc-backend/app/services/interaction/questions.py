"""Helpers that turn structured LLM findings into guided questions."""
import logging
from typing import List, Dict, Any
from app.services.interaction.contracts import InteractionQuestion

logger = logging.getLogger(__name__)

def parse_llm_questions(raw_questions: List[Dict[str, Any]]) -> List[InteractionQuestion]:
    """Converts raw JSON question objects from LLM into InteractionQuestion objects."""
    questions: List[InteractionQuestion] = []
    
    for idx, q in enumerate(raw_questions):
        questions.append(
            InteractionQuestion(
                id=q.get("id", f"q_{idx}"),
                text=q.get("text", "Please provide design details for this missing component."),
                scope=q.get("scope", "missing_information"),
                options=q.get("options", [])
            )
        )
    return questions

def build_questions_from_missing(missing_blocks: List[str]) -> List[InteractionQuestion]:
    """Fallback generator in case LLM output did not include dynamic questions."""
    return [
        InteractionQuestion(
            id=f"q_{block.lower()}",
            text=f"Which design decision or options should be configured for '{block}'?",
            scope="missing_information",
            options=[]
        )
        for block in missing_blocks
    ]

def generate_pim_to_psm_questions(analysis: Dict) -> List[InteractionQuestion]:

    questions: List[InteractionQuestion] = []

    if "Relations" in analysis.get("missing", []):
        questions.append(
            InteractionQuestion(
                id="relation_validation",
                text="¿Esta relación entre componentes implica dependencia funcional?",
                scope="consistency_check",
                options=["Sí (A requires B)", "No", "No estoy seguro"],
                answers=[]
            )
        )

    if "Attributes" in analysis.get("missing", []):
        questions.append(
            InteractionQuestion(
                id="attribute_type",
                text="Atributo X: ¿Qué tipo de dato debería tener?",
                scope="missing_information",
                options=["Número", "Texto", "Booleano", "Lista", "Otro"],
                answers=[]
            )
        )

    if "Constraints" in analysis.get("missing", []):
        questions.append(
            InteractionQuestion(
                id="constraint_application",
                text="Restricción 'shots/qubits/depth': ¿Aplica a qué componente?",
                scope="classification_disambiguation",
                options=["Componente Cuántico", "Driver clásico", "Ambos"],
                answers=[]
            )
        )

    return questions