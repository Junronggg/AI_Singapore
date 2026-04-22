from typing import Dict, List


class DecisionSupportAgent:
    def recommend(self, diagnosis_result: Dict, predictive_result: Dict) -> Dict:
        risk_level = predictive_result["risk_level"]
        likely_root_cause = diagnosis_result.get("likely_root_cause")
        top_features = diagnosis_result.get("top_contributing_features", [])

        affected = [item["feature"] for item in top_features]

        if risk_level == "HIGH":
            action = (
                f"Immediate inspection recommended. Prioritize components related to "
                f"{likely_root_cause}. Escalate to operator and isolate affected section if needed."
            )
        elif risk_level == "MEDIUM":
            action = (
                f"Schedule near-term inspection. Monitor features related to "
                f"{likely_root_cause} closely and verify abnormal sensor behavior."
            )
        else:
            action = (
                f"No immediate maintenance required. Continue monitoring, especially around "
                f"{likely_root_cause}."
            )

        return {
            "recommended_action": action,
            "affected_components": affected,
            "risk_level": risk_level,
        }