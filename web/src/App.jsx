import React, { useState } from 'react';
import Header from './components/Header';
import ClinicalNoteInput from './components/ClinicalNoteInput';
import PatientProfile from './components/PatientProfile';
import MatchedTrials from './components/MatchedTrials';
import { matchTrials } from './services/api';
import { Sparkles, Activity, FileText, Share2, Search } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleMatch = async (clinicalNote, maxTrials) => {
    setLoading(true);
    setError(null);
    try {
      const data = await matchTrials(clinicalNote, maxTrials);
      setResults(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to process matching. Check if backend is running on port 8001.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8 min-h-screen">
      <Header />

      <main className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in">
        {/* Left Column: Input & Profile */}
        <div className="lg:col-span-5 space-y-6">
          <section className="glass-panel p-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Clinical Data</h2>
            </div>
            <ClinicalNoteInput onMatch={handleMatch} loading={loading} />
          </section>

          {results?.patient_profile && (
            <div className="animate-slide-up">
              <PatientProfile profile={results.patient_profile} />
            </div>
          )}
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-7 space-y-6">
          {!results && !loading ? (
            <div className="h-full min-h-[400px] glass-panel p-12 flex flex-col items-center justify-center text-center space-y-4 border-dashed">
              <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-2">
                <Search className="w-8 h-8 text-secondary" />
              </div>
              <h3 className="text-2xl font-display font-medium text-white/50">Ready to start matching</h3>
              <p className="text-secondary max-w-sm">
                Enter a clinical note or select a demo case to find the most relevant trials using AI reasoning.
              </p>
            </div>
          ) : null}

          {loading && (
            <div className="glass-panel p-12 flex flex-col items-center justify-center space-y-6 text-center animate-pulse-slow">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                <Sparkles className="w-8 h-8 text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-medium text-white">AI Reasoning in Progress...</h3>
                <p className="text-secondary max-w-xs mx-auto">
                  Gemini is extracting biomarkers and evaluating {results?.total_matched || 'eligibility'} criteria.
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="glass-panel p-6 bg-error/10 border-error/20 flex gap-4 items-start">
              <div className="p-2 bg-error/20 rounded-lg">
                <Activity className="w-5 h-5 text-error" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-error">Matching Error</h3>
                <p className="text-sm text-error/80">{error}</p>
              </div>
            </div>
          )}

          {results?.trials && !loading && (
            <div className="animate-slide-up">
              <MatchedTrials
                trials={results.trials}
                summary={results.patient_summary}
                fhir={results.fhir_bundle}
              />
            </div>
          )}
        </div>
      </main>

      <footer className="text-center pt-12 pb-6 text-secondary text-sm">
        <p>© 2026 TrialNav · Built for MedGemma HAI-DEF Hackathon</p>
      </footer>
    </div>
  );
}

export default App;
