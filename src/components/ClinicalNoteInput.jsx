import React, { useState } from 'react';
import { Play, RotateCcw, ChevronDown } from 'lucide-react';

const DEMO_CASES = [
    {
        name: "🫁 NSCLC (Post-Osimertinib)",
        note: "58-year-old female with stage IV non-small cell lung cancer (NSCLC). EGFR exon 19 deletion confirmed. Initially treated with Osimertinib for 14 months, now showing progression in the left lung and new liver metastases. ECOG PS 1. PD-L1 TPS 45%. Relevant history: Non-smoker, mild hypertension."
    },
    {
        name: "🎗️ Triple-Negative Breast Cancer",
        note: "42-year-old female with metastatic triple-negative breast cancer (TNBC). ER-, PR-, HER2-. Received AC-T chemotherapy in the neoadjuvant setting. Now presents with recurrence in chest wall and supraclavicular lymph nodes. No prior taxanes for metastatic disease. BRCA1/2 wild-type. PD-L1 CPS 15. ECOG 0."
    },
    {
        name: "🩸 CLL (Post-BTKi)",
        note: "65-year-old male with Chronic Lymphocytic Leukemia (CLL). Deletion 17p detected by FISH. Treated with Ibrutinib for 3 years, now showing rapid lymphocytosis and increasing lymphadenopathy consistent with progression. ECOG 0. Absolute Lymphocyte Count: 145,000/uL."
    },
    {
        name: "🧠 Glioblastoma (Recurrent)",
        note: "54-year-old male with recurrent glioblastoma multiforme (GBM), IDH wild-type, MGMT promoter unmethylated. Initially treated with temozolomide and radiation (Stupp protocol). MRI shows 2.8 cm enhancing lesion in the right frontal lobe at 8 months post-resection. KPS 80. No prior bevacizumab."
    },
    {
        name: "🫀 Pancreatic Adenocarcinoma",
        note: "67-year-old male with locally advanced pancreatic ductal adenocarcinoma (PDAC), KRAS G12D mutation detected. Borderline resectable. CA 19-9: 4,200 U/mL. Received 4 cycles of FOLFIRINOX with partial response. ECOG 1. No prior gemcitabine. Germline BRCA2 pathogenic variant detected."
    },
    {
        name: "🫘 Renal Cell Carcinoma (mRCC)",
        note: "60-year-old female with metastatic clear cell renal cell carcinoma (ccRCC). IMDC intermediate risk. Prior first-line nivolumab + ipilimumab for 6 months — best response SD, then progression (lung mets). No prior VEGFR TKI therapy. PDL1 expression 5%. Good ECOG performance status of 1."
    },
    {
        name: "🧬 AML (Relapsed/Refractory)",
        note: "49-year-old female with relapsed/refractory acute myeloid leukemia (AML). FLT3-ITD mutation positive, NPM1 wild-type. Second relapse after initial induction (7+3) and midostaurin maintenance. Bone marrow biopsy shows 38% blasts. No active CNS involvement. ECOG 1. Prior allo-SCT not performed."
    },
    {
        name: "🔬 Colorectal (MSI-H, mCRC)",
        note: "71-year-old male with metastatic colorectal cancer (mCRC), left-sided tumor, MSI-High / dMMR confirmed by IHC. KRAS/NRAS/BRAF wild-type. Liver and peritoneal metastases. Received first-line FOLFOX + bevacizumab for 6 months, now progressing. CEA: 88 ng/mL. ECOG 1. No prior immunotherapy."
    },
];

const ClinicalNoteInput = ({ onMatch, loading }) => {
    const [note, setNote] = useState("");
    const [maxTrials, setMaxTrials] = useState(5);

    const handleDemoCase = (caseNote) => {
        setNote(caseNote);
    };

    return (
        <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
                {DEMO_CASES.map((c, i) => (
                    <button
                        key={i}
                        onClick={() => handleDemoCase(c.note)}
                        className="text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-white/20 transition-all text-secondary hover:text-white"
                    >
                        {c.name}
                    </button>
                ))}
            </div>

            <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Paste clinical note or EHR text here..."
                className="input-field min-h-[220px] resize-none text-sm font-light leading-relaxed scrollbar-thin"
            />

            <div className="flex items-center justify-between gap-4 pt-2">
                <div className="flex flex-col">
                    <span className="section-label">Max Trials</span>
                    <select
                        value={maxTrials}
                        onChange={(e) => setMaxTrials(Number(e.target.value))}
                        className="bg-white/5 border border-white/10 rounded-md py-1 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                        <option value={3}>3 Trials</option>
                        <option value={5}>5 Trials</option>
                        <option value={10}>10 Trials</option>
                    </select>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setNote("")}
                        className="btn-secondary"
                        title="Clear Input"
                    >
                        <RotateCcw className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => onMatch(note, maxTrials)}
                        disabled={loading || !note}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Play className="w-4 h-4 fill-current" />
                        <span>Match Trials</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ClinicalNoteInput;
