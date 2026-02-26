import React from 'react';
import { Microscope, Activity, ShieldCheck } from 'lucide-react';

const Header = () => {
    return (
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-4 border-b border-white/5">
            <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
                    <Microscope className="w-7 h-7 text-background" />
                </div>
                <div>
                    <h1 className="text-2xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                        TrialNav
                    </h1>
                    <div className="flex items-center gap-2 text-xs font-medium text-secondary">
                        <span className="flex items-center gap-1">
                            <Activity className="w-3 h-3 text-primary" /> Gemini 2.0 Flash
                        </span>
                        <span className="w-1 h-1 rounded-full bg-white/10"></span>
                        <span className="flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3 text-success" /> HIPAA Ready
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="hidden sm:flex items-center bg-white/5 rounded-full px-4 py-1.5 border border-white/10">
                    <span className="flex items-center gap-2 text-xs font-semibold text-secondary">
                        <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
                        BACKEND CONNECTED
                    </span>
                </div>
                <button className="btn-secondary text-xs">Settings</button>
            </div>
        </header>
    );
};

export default Header;
