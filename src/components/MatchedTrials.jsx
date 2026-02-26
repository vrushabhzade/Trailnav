import React, { useState } from 'react';
import { Microscope, Activity, ChevronRight, ExternalLink, Info, Copy, FileJson, CheckCircle2 } from 'lucide-react';

const TrialCard = ({ trial }) => {
    const [expanded, setExpanded] = useState(false);

    const getVerdictStyle = (verdict) => {
        switch (verdict) {
            case 'ELIGIBLE': return 'bg-success/20 text-success border-success/30';
            case 'LIKELY_ELIGIBLE': return 'bg-primary/20 text-primary border-primary/30';
            case 'BORDERLINE': return 'bg-warning/20 text-warning border-warning/30';
            default: return 'bg-error/20 text-error border-error/30';
        }
    };

    return (
        <div className="glass-card p-5 group">
            <div className="flex items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getVerdictStyle(trial.overall_verdict)}`}>
                            {trial.overall_verdict?.replace('_', ' ')}
                        </span>
                        <span className="text-xs font-medium text-secondary">{trial.nct_id}</span>
                        <span className="text-xs font-medium text-primary/40">• Phase {trial.phase || 'N/A'}</span>
                    </div>
                    <h3 className="line-clamp-2 text-base font-semibold text-white group-hover:text-primary transition-colors leading-tight">
                        {trial.title}
                    </h3>
                </div>
                <div className="flex flex-col items-end gap-1">
                    <div className="text-2xl font-display font-bold text-white">{trial.match_score}%</div>
                    <div className="text-[10px] uppercase tracking-wider font-bold text-secondary">Match Score</div>
                </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
                <p className="text-xs text-secondary line-clamp-1 flex-1 pr-4">
                    <span className="font-semibold text-white/50">Sponsor:</span> {trial.sponsor}
                </p>
                <div className="flex items-center gap-2">
                    <a
                        href={trial.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-secondary hover:text-white"
                    >
                        <ExternalLink className="w-4 h-4" />
                    </a>
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="flex items-center gap-1 px-2 py-1 bg-white/5 hover:bg-white/10 rounded-md text-[10px] font-bold uppercase transition-all"
                    >
                        {expanded ? 'Hide Reason' : 'Why Match?'}
                        <ChevronRight className={`w-3 h-3 transition-transform ${expanded ? 'rotate-90' : ''}`} />
                    </button>
                </div>
            </div>

            {expanded && (
                <div className="mt-4 p-4 bg-background/50 rounded-xl border border-white/5 animate-fade-in">
                    <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                        <div className="space-y-4">
                            <div className="space-y-1">
                                <span className="text-[10px] font-bold uppercase text-secondary">AI Reasoning (Chain-of-Thought)</span>
                                <p className="text-xs text-white/80 leading-relaxed font-light italic">
                                    "{trial.reason}"
                                </p>
                            </div>
                            {/* Optional: Add reasoning steps if we parse them from backend in future */}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const MatchedTrials = ({ trials, summary, fhir }) => {
    const [activeTab, setActiveTab] = useState('trials');

    if (!trials || trials.length === 0) return null;

    return (
        <div className="space-y-6">
            <div className="flex border-b border-white/10">
                {[
                    { id: 'trials', label: 'Matched Trials', icon: Microscope },
                    { id: 'summary', label: 'Patient Summary', icon: CheckCircle2 },
                    { id: 'fhir', label: 'FHIR Export', icon: FileJson }
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-6 py-3 text-sm font-semibold transition-all relative ${activeTab === tab.id ? 'text-primary' : 'text-secondary hover:text-white'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                        {activeTab === tab.id && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
                        )}
                    </button>
                ))}
            </div>

            <div className="min-h-[400px]">
                {activeTab === 'trials' && (
                    <div className="space-y-4 animate-fade-in">
                        {trials.map((t, i) => (
                            <TrialCard key={i} trial={t} />
                        ))}
                    </div>
                )}

                {activeTab === 'summary' && (
                    <div className="glass-panel p-8 animate-fade-in space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold">Clinician Summary</h3>
                            <button className="flex items-center gap-1 text-[10px] font-bold text-primary hover:text-primary-hover uppercase">
                                <Copy className="w-3 h-3" /> Copy Text
                            </button>
                        </div>
                        <div className="prose prose-invert max-w-none">
                            <p className="text-white/80 leading-relaxed whitespace-pre-wrap font-light">
                                {summary || "No summary generated. Try matching again with 'Generate Summary' enabled."}
                            </p>
                        </div>
                    </div>
                )}

                {activeTab === 'fhir' && (
                    <div className="glass-panel p-0 overflow-hidden animate-fade-in relative group">
                        <div className="p-4 bg-white/5 border-b border-white/5 flex items-center justify-between">
                            <span className="text-xs font-mono text-secondary">FHIR R4 ResearchStudy Bundle</span>
                            <button className="flex items-center gap-1 text-[10px] font-bold text-primary hover:text-primary-hover uppercase">
                                Download JSON
                            </button>
                        </div>
                        <pre className="p-6 text-[11px] font-mono text-primary/80 overflow-auto max-h-[600px] scrollbar-thin">
                            {JSON.stringify(fhir, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MatchedTrials;
