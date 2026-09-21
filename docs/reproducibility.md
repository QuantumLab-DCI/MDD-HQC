# Reproducing the Illustrative Cases

This guide applies to **MDD-HQC v1.4.1** and assumes that the platform has already been installed and started by following the [main README](../README.md).

## Available Materials

During execution, the prototype writes the latest generated models to the backend `data/` directory:

```text
mdd-hqc-backend/data/model.uvl
mdd-hqc-backend/data/model.puml
```

These runtime files can be overwritten by subsequent transformations. Therefore, stable copies of the inputs, generated outputs, and manual refinements used in the illustrative cases are preserved under `artifacts/cases/` for reproducibility and artifact-level traceability:

```text
artifacts/cases/
├── chileespres/
│   ├── input-cim.xml
│   ├── generated-pim.uvl
│   └── generated-psm.puml
└── q-tradex/
    ├── input-cim.xml
    ├── generated-pim.uvl
    ├── refined-pim.uvl
    ├── generated-psm.puml
    └── refined-psm.puml
```

The `input-cim.xml` files are copies of the built-in examples loaded by the user interface. The `generated-*` files preserve the outputs produced by the deterministic transformation rules, while the `refined-*` files preserve the manual refinements used for the Q-TradeX case in the accompanying paper.

## Running the Cases

The same procedure applies to ChileEsPres and Q-TradeX:

1. Open the MDD-HQC interface at http://localhost:3000.
2. Select the case from the **Examples** section.
3. Execute the **CIM–PIM** transformation.
4. Inspect the generated UVL model.
5. Execute the **PIM–PSM** transformation.
6. Inspect the generated UML class diagram.
7. Compare the results with the corresponding `generated-*` files under `artifacts/cases/`.

> [!WARNING]
> Runtime outputs in the backend `data/` directory are overwritten by subsequent transformations. The files under `artifacts/cases/` are preserved reference copies and are not generated automatically in that location.

## Q-TradeX Manual Refinement

For Q-TradeX, the deterministic outputs are preserved as:

```text
artifacts/cases/q-tradex/generated-pim.uvl
artifacts/cases/q-tradex/generated-psm.puml
```

The models shown after manual refinement in the accompanying paper are preserved as:

```text
artifacts/cases/q-tradex/refined-pim.uvl
artifacts/cases/q-tradex/refined-psm.puml
```

The UVL refinement was informed by the predefined guided questions presented after the LLM-assisted completeness analysis. The user selected the relevant decisions and manually incorporated them into the model. The PlantUML model was also refined manually from its corresponding deterministic output.

The current prototype does not automatically apply or trace these refinements.

## Continuing from a Refined PIM

The current interface does not support loading a manually refined PIM. To generate a PSM from `refined-pim.uvl`, place the file in a path accessible to the backend:

```bash
cp artifacts/cases/q-tradex/refined-pim.uvl \
  mdd-hqc-backend/data/refined-pim.uvl
```

When using Docker Compose, ensure that the file is visible inside the backend container under the corresponding `data/` directory.

Then invoke the PIM–PSM endpoint:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"path":"data/refined-pim.uvl"}' \
  http://localhost:8000/transformations/pim-to-psm
```

The resulting PlantUML model is returned by the API and written to:

```text
mdd-hqc-backend/data/model.puml
```

This endpoint applies the deterministic PIM–PSM rules to the refined UVL model. Any additional changes contained in `refined-psm.puml` were introduced manually.
