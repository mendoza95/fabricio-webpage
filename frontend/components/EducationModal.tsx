'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { EducationResponse, EducationBase } from '@/types/portfolio';
import TextareaAutosize from 'react-textarea-autosize';

interface EducationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  educationToEdit?: EducationResponse | null;
}

export default function EducationModal({ isOpen, onClose, onSuccess, educationToEdit }: EducationModalProps) {
  const [formLang, setFormLang] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [institutionLogo, setInstitutionLogo] = useState('');
  const [institutionUrl, setInstitutionUrl] = useState('');
  const [startYear, setStartYear] = useState<string | number>('');
  const [endYear, setEndYear] = useState<string | number>('');

  const [translations, setTranslations] = useState({
    es: { degree: '', institution: '', location: '', description: '', description_cv: '' },
    en: { degree: '', institution: '', location: '', description: '', description_cv: '' },
  });

  useEffect(() => {
    if (educationToEdit) {
      setInstitutionLogo(educationToEdit.institution_logo || '');
      setInstitutionUrl(educationToEdit.institution_url || '');
      setStartYear(educationToEdit.start_year ?? '');
      setEndYear(educationToEdit.end_year ?? '');

      setTranslations({
        es: {
          degree: educationToEdit.translations?.es?.degree || '',
          institution: educationToEdit.translations?.es?.institution || '',
          location: educationToEdit.translations?.es?.location || '',
          description: educationToEdit.translations?.es?.description || '',
          description_cv: educationToEdit.translations?.es?.description_cv?.join('\n') || '',
        },
        en: {
          degree: educationToEdit.translations?.en?.degree || '',
          institution: educationToEdit.translations?.en?.institution || '',
          location: educationToEdit.translations?.en?.location || '',
          description: educationToEdit.translations?.en?.description || '',
          description_cv: educationToEdit.translations?.en?.description_cv?.join('\n') || '',
        },
      });
    } else {
      setInstitutionLogo('');
      setInstitutionUrl('');
      setStartYear('');
      setEndYear('');
      setTranslations({
        es: { degree: '', institution: '', location: '', description: '', description_cv: '' },
        en: { degree: '', institution: '', location: '', description: '', description_cv: '' },
      });
    }
  }, [educationToEdit, isOpen]);

  if (!isOpen) return null;

  const handleTranslationChange = (field: 'degree' | 'institution' | 'location' | 'description' | 'description_cv', value: string) => {
    setTranslations((prev) => ({
      ...prev,
      [formLang]: { ...prev[formLang], [field]: value },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload: EducationBase = {
      institution_logo: institutionLogo,
      institution_url: institutionUrl,
      start_year: startYear,
      end_year: endYear,
      translations: {
        es: {
          degree: translations.es.degree,
          institution: translations.es.institution,
          location: translations.es.location,
          description: translations.es.description,
          description_cv: translations.es.description_cv.split('\n').filter(Boolean),
        },
        en: {
          degree: translations.en.degree,
          institution: translations.en.institution,
          location: translations.en.location,
          description: translations.en.description,
          description_cv: translations.en.description_cv.split('\n').filter(Boolean),
        },
      },
    };

    try {
      if (educationToEdit && educationToEdit.id) {
        await api.put(`/portfolio/education/${educationToEdit.id}`, payload);
      } else {
        await api.post('/portfolio/education', payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Error al guardar educación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl p-6 md:p-8 flex flex-col max-h-[90vh] shadow-2xl my-auto overflow-x-auto">
        
        {/* Encabezado Fijo */}
        <div className="flex justify-between items-center border-b border-slate-800 pb-4 shrink-0 min-w-full">
          <h2 className="text-2xl font-bold text-white">{educationToEdit ? 'Editar Educación' : 'Nueva Educación'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-bold text-xl px-2">✕</button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-sm text-center shrink-0">
            {error}
          </div>
        )}

        {/* Formulario con Scroll Interno */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto overflow-x-auto space-y-6 pt-4 pr-1 min-w-full">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Año de Inicio</label>
              <input type="text" value={startYear} onChange={(e) => setStartYear(e.target.value)} required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Año de Fin</label>
              <input type="text" value={endYear} onChange={(e) => setEndYear(e.target.value)} required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
          </div>

          <div className="border border-slate-800 rounded-2xl p-4 bg-slate-950/40 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-sm font-bold text-indigo-400">Traducción de Educación</span>
              <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                <button type="button" onClick={() => setFormLang('es')} className={`px-3 py-1 rounded-md text-xs font-semibold transition ${formLang === 'es' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>ES</button>
                <button type="button" onClick={() => setFormLang('en')} className={`px-3 py-1 rounded-md text-xs font-semibold transition ${formLang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>EN</button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Título / Grado ({formLang.toUpperCase()})</label>
                <input type="text" value={translations[formLang].degree} onChange={(e) => handleTranslationChange('degree', e.target.value)} required={formLang === 'es'} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Institución ({formLang.toUpperCase()})</label>
                <input type="text" value={translations[formLang].institution} onChange={(e) => handleTranslationChange('institution', e.target.value)} required={formLang === 'es'} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Descripción ({formLang.toUpperCase()})</label>
                <TextareaAutosize minRows={3} value={translations[formLang].description} onChange={(e) => handleTranslationChange('description', e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto" />
              </div>
            </div>
          </div>

          {/* ACCIONES FIJAS */}
          <div className="sticky bottom-0 bg-slate-900 pt-4 pb-1 border-t border-slate-800 flex justify-end gap-3 min-w-full">
            <button type="button" onClick={onClose} className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-sm rounded-xl transition">Cancelar</button>
            <button type="submit" disabled={loading} className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20 disabled:opacity-50">{loading ? 'Guardando...' : 'Guardar'}</button>
          </div>

        </form>
      </div>
    </div>
  );
}