# Transformation Rules

MDD-HQC uses explicit transformation rules to connect the CIM, PIM, and PSM modeling levels. This document provides a compact reference to the currently defined rules. The complete rationale behind each mapping is described in the MDD-HQC TLISC 2026 paper.

## CIM-to-PIM Rules

The CIM-to-PIM rules transform intentional elements represented in iStar 2.0 into features, attributes, constraints, comments, and variability groups represented in UVL.

| ID      | Source                            | Target                        | Summary                                                                                                                                                                                                                      |
| ------- | --------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CP1** | Actor                             | UVL comment                   | Preserves the actor associated with each decision as origin metadata.                                                                                                                                                        |
| **CP2** | Goal or task                      | Feature with `kind` attribute | Transforms goals and tasks into features identified as `goal` or `task`. Their placement in the HQC variability subtree may require analyst input.                                                                           |
| **CP3** | Quality                           | Feature attribute             | Represents a quality as an attribute of the goal, task, or resource that it qualifies.                                                                                                                                       |
| **CP4** | Resource                          | Mandatory resource feature    | Transforms a resource into a mandatory subfeature of its associated task and identifies it with `kind "resource"`.                                                                                                           |
| **CP5** | Social dependency                 | `requires` constraint         | Represents the depender-dependum-dependee relationship as a cross-tree constraint in UVL.                                                                                                                                    |
| **CP6** | Link between intentional elements | UVL relation or metadata      | Maps iStar links according to their semantics: `needed-by` links become mandatory relations, qualification links become feature attributes, contributions become comments, and AND/OR refinements become variability groups. |

## PIM-to-PSM Rules

The PIM-to-PSM rules transform the supported elements of the UVL variability model into a preliminary UML class diagram enriched with QuantumUML stereotypes.

| ID      | Source                          | Target                             | Summary                                                                                                                              |
| ------- | ------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **PP1** | Actor and contribution comments | UML note                           | Preserves actor origin and contribution information as notes associated with classes or operations.                                  |
| **PP2** | Feature with `kind` attribute   | Class, method, or attribute        | Goals become classes, tasks become methods, and resources become attributes. Tasks without a parent goal may produce helper classes. |
| **PP3** | `Algorithm` feature             | UML class                          | Classical algorithms become regular classes, while quantum algorithms use the `<<Quantum>>` stereotype.                              |
| **PP4** | `Integration_model` feature     | UML class with `<<QuantumDriver>>` | Represents the orchestration mechanism between classical and quantum components.                                                     |
| **PP5** | `Quantum_HW_constraint` feature | UML note                           | Associates quantum hardware constraints with the corresponding quantum or integration elements.                                      |
| **PP6** | `requires` constraint           | UML dependency                     | Transforms a cross-tree requirement into a dependency between the corresponding classes.                                             |
| **PP7** | Feature attribute               | UML attribute                      | Transfers feature attributes to the class generated from the associated feature.                                                     |
| **PP8** | Mandatory or OR group           | UML note                           | Preserves variability-group information as notes associated with the corresponding UML elements.                                     |

## Current Boundaries

* The rules cover the currently supported iStar, UVL, and QuantumUML elements; they do not provide complete semantic coverage of the three languages.
* Some CIM decisions, particularly the classification of goals and tasks within the HQC variability model, require analyst input.
* Non-structural information is preserved mainly through comments, attributes, and UML notes.
* Vertical traceability is partial and depends on the metadata propagated by the applicable rules.
* Generated PIM and PSM models may require manual refinement when the source model does not contain enough information.

## Implementation

The current implementations are located at:

```text
mdd-hqc-backend/app/services/transformations/cim_to_pim.py
mdd-hqc-backend/app/services/transformations/pim_to_psm.py
```

The conceptual rule identifiers do not necessarily correspond one-to-one with individual functions. Some implementation functions group several related mappings, particularly those defined under **CP6**.
