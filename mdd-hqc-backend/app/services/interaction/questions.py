"""Helpers that turn structured LLM findings into guided questions."""

from typing import List
from typing import Dict

from app.services.interaction.contracts import InteractionQuestion


def build_questions_from_missing(missing_blocks: List[str]) -> List[InteractionQuestion]:
    """Builds the guided questions associated with one missing-group analysis result."""

    questions: List[InteractionQuestion] = []
    for missing in missing_blocks:
        if missing == "Algorithm":
            questions.append(
                InteractionQuestion(
                    id="q_algorithm",
                    text="What type of algorithm will be used?",
                    scope="missing_information",
                    options=[
                        "Greedy",
                        "Dynamic Programming",
                        "Quantum Search",
                        "Other",
                    ],
                )
            )
        elif missing == "Programming":
            questions.append(
                InteractionQuestion(
                    id="q_programming",
                    text="Which framework/language will be used for development?",
                    scope="missing_information",
                    options=["Python", "Rust", "Q#", "Other"],
                )
            )
        elif missing == "Integration_model":
            questions.append(
                InteractionQuestion(
                    id="q_integration",
                    text="Which integration model will be used? (SOA, middleware, etc.)",
                    scope="missing_information",
                    options=["Middleware/API", "Microservices", "Quantum-SOA"],
                )
            )
        elif missing == "Quantum_HW_constraint":
            questions.append(
                InteractionQuestion(
                    id="q_hw",
                    text="Which hardware constraint is the most relevant?",
                    scope="missing_information",
                    options=[
                        "Qubits",
                        "Shots",
                        "Circuit depth",
                        "Error rate",
                        "Connectivity",
                        "Other",
                    ],
                )
            )
        elif missing == "Functionality":
            questions.append(
                InteractionQuestion(
                    id="q_functionality",
                    text="What main functionality should the system cover?",
                    scope="missing_information",
                )
            )
    return questions

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