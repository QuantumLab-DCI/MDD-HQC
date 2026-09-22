import json
import logging
import re
from typing import Dict

from app.services.interaction.contracts import InteractionInput
from app.services.interaction.providers.base import LLMProvider

logger = logging.getLogger(__name__)

PIM_PSM_FEATURE_MODEL = [
    "Attributes",
    "Relations",
    "Constraints",
    "HybridRoles",
]

PSM_PROMPT_TEMPLATE = """
Analiza el siguiente modelo UVL y responde SOLO con un JSON válido con las claves exactas:
Attributes, Relations, Constraints, HybridRoles, missing.

No uses otras claves como questions o proposals.
No incluyas explicaciones, comentarios ni texto adicional fuera del JSON.

Objetivo del análisis:
- Revisar la consistencia estructural del modelo PIM para construir el PSM.
- Determinar si el UVL contiene evidencia suficiente de:
  - Attributes: todos los atributos con tipo definido.
  - Relations: relaciones claras (dependencia vs contención).
  - Constraints: restricciones aplicadas a componentes específicos.
  - HybridRoles: roles de componentes híbridos/cuánticos.

Reglas de interpretación:
- Attributes=true si todos los atributos tienen tipo definido.
- Relations=true si las relaciones están claramente especificadas.
- Constraints=true si las restricciones tienen destino claro.
- HybridRoles=true si los roles de componentes híbridos/cuánticos están definidos.
- missing debe contener TODAS las claves anteriores que estén en false.

Formato de salida:
{{
  "Attributes": true|false,
  "Relations": true|false,
  "Constraints": true|false,
  "HybridRoles": true|false,
  "missing": ["..."]
}}

UVL a analizar:
{uvl_content}
""".strip()

class PimToPsmConsistencyAnalyzer:

    def __init__(self, provider: LLMProvider):
        self.provider = provider
    
    def analyze_psm(self, payload: InteractionInput) -> Dict:
        prompt = PSM_PROMPT_TEMPLATE.format(uvl_content=payload.output_uvl_content)
        raw_response = self.provider.generate(prompt)
        logger.debug("Raw PSM analysis response received from provider: %s", raw_response)
        return self._safe_parse_json(raw_response)

    def _safe_parse_json(self, raw: str) -> Dict:
        try:
            parsed = json.loads(raw)
            logger.debug("LLM response parsed directly as JSON: %s", parsed)
        except Exception:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                logger.warning("PSM analyzer could not find a JSON object in the LLM response.")
                return {}
            try:
                parsed = json.loads(match.group(0))
                logger.debug("LLM response parsed from extracted JSON block: %s", parsed)
            except Exception:
                logger.warning("PSM analyzer found a JSON-like block but could not parse it.")
                return {}

        if not self._contains_all_required_keys(parsed):
            logger.warning("PSM analyzer discarded LLM response because required keys were missing: %s", parsed)
            return {}

        result = self._build_boolean_result(parsed)
        missing = parsed.get("missing", [])
        result["missing"] = missing if isinstance(missing, list) else []
        if not result["missing"]:
            result["missing"] = self._collect_missing_groups(result)
        logger.debug("Normalized PSM consistency analysis result: %s", result)
        return result

    def _contains_all_required_keys(self, parsed: Dict) -> bool:
        for required_key in PIM_PSM_FEATURE_MODEL:
            if required_key not in parsed:
                return False
        return True

    def _build_boolean_result(self, parsed: Dict) -> Dict:
        result: Dict = {}
        for group_name in PIM_PSM_FEATURE_MODEL:
            result[group_name] = bool(parsed.get(group_name, False))
        return result

    def _collect_missing_groups(self, result: Dict) -> list[str]:
        missing_groups: list[str] = []
        for group_name in PIM_PSM_FEATURE_MODEL:
            if not result.get(group_name, False):
                missing_groups.append(group_name)
        return missing_groups
