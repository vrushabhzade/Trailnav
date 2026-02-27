import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8001'),
    timeout: 300000, // Matching the backend timeout for Gemini
});

export const matchTrials = async (clinicalNote, maxTrials = 5) => {
    try {
        const response = await api.post('/api/match', {
            clinical_note: clinicalNote,
            max_trials: maxTrials,
            generate_summary: true,
            export_fhir: true
        });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

export const getHealth = async () => {
    const response = await api.get('/health');
    return response.data;
};

export default api;
