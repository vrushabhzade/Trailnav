import React from 'react';
import { User, Cpu, ClipboardCheck, History } from 'lucide-react';

const PatientProfile = ({ profile }) => {
    if (!profile) return null;

    return (
        <section className="glass-panel p-6 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
                <User className="w-32 h-32" />
            </div>

            <div className="flex items-center gap-2 mb-4">
                <Cpu className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">AI Extracted Profile</h2>
            </div>

            <div className="grid grid-cols-1 gap-4">
                <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <span className="section-label">Diagnosis</span>
                    <p className="text-white font-medium">{profile.diagnosis || 'Unknown'}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                        <span className="section-label">Biomarkers</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                            {Array.isArray(profile.biomarkers) && profile.biomarkers.length > 0 ? (
                                profile.biomarkers.map((b, i) => (
                                    <span key={i} className="px-2 py-0.5 bg-primary/20 text-primary text-[10px] font-bold rounded uppercase">
                                        {b}
                                    </span>
                                ))
                            ) : (
                                <span className="text-secondary text-xs">None identified</span>
                            )}
                        </div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                        <span className="section-label">ECOG Status</span>
                        <div className="flex items-center gap-2">
                            <span className="text-2xl font-bold text-white">{profile.ecog || '—'}</span>
                            <span className="text-[10px] text-secondary leading-tight">Performance<br />Status</span>
                        </div>
                    </div>
                </div>

                <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <span className="section-label">Prior Treatments</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                        {Array.isArray(profile.prior_treatments) && profile.prior_treatments.length > 0 ? (
                            profile.prior_treatments.map((t, i) => (
                                <div key={i} className="flex items-center gap-1.5 text-sm text-white/80">
                                    <div className="w-1 h-1 rounded-full bg-primary"></div>
                                    {t}
                                </div>
                            ))
                        ) : (
                            <span className="text-secondary text-xs">None identified</span>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default PatientProfile;
