import { useState, useMemo, useEffect } from "react"
import { ArrowRight, GitCompare, X } from "lucide-react"

/**
 * Visual scaffold and interactive diff engine for model integration.
 */
const ModelIntegrationDiffModal = ({
  isOpen,
  onClose,
  finalUvlModel = "",
  proposals = [],
  onSaveIntegratedModel,
}) => {
  // Estado para registrar las decisiones: { [proposal_id]: 'accepted' | 'rejected' }
  const [decisions, setDecisions] = useState({})

  // Reiniciar estado cada vez que se abra el modal con nuevas propuestas
  useEffect(() => {
    if (isOpen) {
      setDecisions({})
    }
  }, [isOpen, proposals])

  const totalProposals = proposals.length
  const processedCount = Object.keys(decisions).length

  // El estado cambia a READY únicamente cuando se han procesado TODAS las propuestas
  const isReady = totalProposals > 0 && processedCount === totalProposals

  const handleAccept = (id) => {
    setDecisions((prev) => ({ ...prev, [id]: "accepted" }))
  }

  const handleReject = (id) => {
    setDecisions((prev) => ({ ...prev, [id]: "rejected" }))
  }

  // Genera el UVL final concatenando dinámicamente solo las propuestas ACEPTADAS
  const updatedRightUvl = useMemo(() => {
  let base = finalUvlModel

  // Filtramos los snippets de las propuestas aceptadas
  const acceptedSnippets = proposals
    .filter((prop) => decisions[prop.id] === "accepted")
    .map((prop) => prop.snippet)
    .join("\n\n")

  if (!acceptedSnippets) return base

  // Si el modelo base ya tiene un bloque 'mandatory', inyectamos las propuestas dentro
  if (base.includes("mandatory")) {
    return base.replace("mandatory", `mandatory\n${acceptedSnippets}`)
  }

  // Si no existe, lo agregamos como un nuevo bloque mandatory
  return `${base}\n\nmandatory\n${acceptedSnippets}`
}, [finalUvlModel, proposals, decisions])

  const handleIntegrateModel = () => {
    if (isReady && onSaveIntegratedModel) {
      onSaveIntegratedModel(updatedRightUvl)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/75 p-3 backdrop-blur-sm sm:p-4">
      <div className="flex max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-xl border border-ctp-surface1 bg-ctp-mantle shadow-2xl">
        <header className="flex flex-col items-stretch justify-between gap-4 border-b border-ctp-surface1 bg-ctp-crust px-4 py-4 sm:px-6 lg:flex-row lg:items-center">
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="rounded-lg bg-ctp-mauve/20 p-3 text-ctp-mauve">
              <GitCompare className="h-6 w-6" />
            </div>

            <div>
              <h2 className="text-lg font-bold uppercase tracking-wide text-ctp-text">
                Model Integration
              </h2>
              <p className="text-sm text-ctp-subtext0">
                Map design decisions to the UVL structure
              </p>
            </div>
          </div>

          <div className="grid w-full grid-cols-2 items-stretch gap-3 lg:w-auto lg:grid-cols-[10rem_10rem_11.5rem_3.5rem]">
            {/* STATUS: PENDING -> READY */}
            <div className="flex h-14 w-full flex-col justify-center rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4">
              <p className="text-[10px] font-bold uppercase leading-none text-ctp-subtext0">
                Status
              </p>
              <p
                className={`mt-1.5 text-sm font-bold leading-none ${
                  isReady ? "text-ctp-green" : "text-ctp-yellow"
                }`}
              >
                ● {isReady ? "Ready" : "Pending"}
              </p>
            </div>

            {/* INTEGRATION PROGRESS: X / N */}
            <div className="flex h-14 w-full flex-col justify-center rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4">
              <p className="whitespace-nowrap text-[10px] font-bold uppercase leading-none text-ctp-subtext0">
                Integration Progress
              </p>
              <p className="mt-1.5 text-sm font-bold leading-none text-ctp-text">
                <span className="text-ctp-mauve">{processedCount}</span> / {totalProposals}
              </p>
            </div>

            {/* BOTÓN INTEGRATE MODEL */}
            <button
              type="button"
              disabled={!isReady}
              onClick={handleIntegrateModel}
              className={`h-14 w-full rounded-lg px-5 text-sm font-bold uppercase transition-all ${
                isReady
                  ? "bg-ctp-mauve text-ctp-base shadow-lg hover:bg-ctp-pink cursor-pointer"
                  : "cursor-not-allowed bg-ctp-surface1 text-ctp-overlay0 opacity-60"
              }`}
            >
              Integrate Model
            </button>

            {/* BOTÓN CANCELAR */}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close model integration"
              title="Cancel model integration"
              className="flex h-14 w-14 items-center justify-center justify-self-end rounded-lg border border-ctp-red/50 bg-ctp-red/15 text-ctp-red transition-colors hover:bg-ctp-red hover:text-ctp-base lg:w-full"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </header>

        <main className="grid min-h-0 flex-1 overflow-auto lg:grid-cols-2 lg:overflow-hidden">
          {/* PANEL IZQUIERDO: PROPOSED CHANGES */}
          <section className="flex min-h-[420px] min-w-0 flex-col border-b border-ctp-surface1 lg:border-b-0 lg:border-r">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                1. Proposed Changes
              </h3>
            </div>

            <div className="themed-scrollbar relative flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto bg-ctp-mantle p-4">

              {/* Renderizado dinámico de tarjetas por cada propuesta */}
              {proposals.map((proposal) => {
                const decision = decisions[proposal.id]

                return (
                  <div
                    key={proposal.id}
                    className={`relative rounded-lg border-l-4 p-4 transition-all ${
                      decision === "accepted"
                        ? "border-ctp-mauve/40 bg-ctp-surface0/30 opacity-40"
                        : decision === "rejected"
                        ? "border-ctp-red/40 bg-ctp-surface0/20 opacity-30"
                        : "border-ctp-green bg-ctp-surface0/90 shadow-xl"
                    }`}
                  >
                    <div className="mb-2 flex items-center justify-between border-b border-ctp-surface1/50 pb-2">
                      <span className="text-xs font-bold text-ctp-green">
                        {proposal.title}
                      </span>

                      {!decision && (
                        <div className="flex gap-1.5">
                          {/* Aceptar (Verde -> Flecha) */}
                          <button
                            type="button"
                            onClick={() => handleAccept(proposal.id)}
                            className="flex h-7 w-7 items-center justify-center rounded-md bg-ctp-green text-ctp-base transition-transform hover:scale-110 active:scale-95"
                            title="Accept proposal"
                          >
                            <ArrowRight className="h-4 w-4" />
                          </button>
                          {/* Rechazar (Rojo -> Cruz) */}
                          <button
                            type="button"
                            onClick={() => handleReject(proposal.id)}
                            className="flex h-7 w-7 items-center justify-center rounded-md bg-ctp-red text-ctp-base transition-transform hover:scale-110 active:scale-95"
                            title="Reject proposal"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </div>

                    <pre className="overflow-x-auto font-mono text-[12px] leading-4 text-ctp-text">
                      {proposal.snippet}
                    </pre>
                  </div>
                )
              })}
            </div>
          </section>

          {/* PANEL DERECHO: FINAL UVL MODEL */}
          <section className="flex min-h-[420px] min-w-0 flex-col">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                2. Final UVL Model
              </h3>
            </div>

            <div className="flex min-h-0 flex-1 bg-ctp-mantle p-4">
              <pre className="themed-scrollbar h-full min-h-0 w-full overflow-auto whitespace-pre-wrap rounded-lg bg-ctp-base p-4 font-mono text-[13px] leading-5 text-ctp-text">
                {updatedRightUvl || "// Cargando Modelo UVL..."}
              </pre>
            </div>
          </section>
        </main>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-ctp-surface1 bg-ctp-crust px-4 py-3">
          <div className="flex flex-wrap gap-4 text-xs sm:gap-6">
            <span className="text-ctp-green">● Pending proposals</span>
            <span className="text-ctp-mauve">● Integrated blocks</span>
          </div>

          <p className="text-xs italic text-ctp-subtext0">
            Click arrows to move suggested blocks into the target model.
          </p>
        </footer>
      </div>
    </div>
  )
}

export default ModelIntegrationDiffModal