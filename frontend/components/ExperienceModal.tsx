'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { ExperienceResponse, ExperienceBase } from '@/types/portfolio';
import TextareaAutosize from 'react-textarea-autosize';

interface ExperienceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  experienceToEdit?: ExperienceResponse | null;
}

export default function ExperienceModal({ isOpen, onClose, onSuccess, experienceToEdit }: ExperienceModalProps) {
  const [formLang, setFormLang] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [experienceCustomId, setExperienceCustomId] = useState('');
  const [companyLogo, setCompanyLogo] = useState('');
  const [companyUrl, setCompanyUrl] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [translations, setTranslations] = useState({
    es: { role: '', company: '', location: '', description: '', description_cv: '' },
    en: { role: '', company: '', location: '', description: '', description_cv: '' },
  });

  useEffect(() => {
    if (experienceToEdit) {
      setExperienceCustomId(experienceToEdit.experience_id || '');
      setCompanyLogo(experienceToEdit.company_logo || '');
      setCompanyUrl(experienceToEdit.company_url || '');
      setStartDate(experienceToEdit.start_date || '');
      setEndDate(experienceToEdit.end_date || '');

      setTranslations({
        es: {
          role: experienceToEdit.translations?.es?.role || '',
          company: experienceToEdit.translations?.es?.company || '',
          location: experienceToEdit.translations?.es?.location || '',
          description: experienceToEdit.translations?.es?.description || '',
          description_cv: experienceToEdit.translations?.es?.description_cv?.join('\n') || '',
        },
        en: {
          role: experienceToEdit.translations?.en?.role || '',
          company: experienceToEdit.translations?.en?.company || '',
          location: experienceToEdit.translations?.en?.location || '',
          description: experienceToEdit.translations?.en?.description || '',
          description_cv: experienceToEdit.translations?.en?.description_cv?.join('\n') || '',
        },
      });
    } else {
      setExperienceCustomId('');
      setCompanyLogo('');
      setCompanyUrl('');
      setStartDate('');
      setEndDate('');
      setTranslations({
        es: { role: '', company: '', location: '', description: '', description_cv: '' },
        en: { role: '', company: '', location: '', description: '', description_cv: '' },
      });
    }
  }, [experienceToEdit, isOpen]);

  if (!isOpen) return null;

  const handleTranslationChange = (field: 'role' | 'company' | 'location' | 'description' | 'description_cv', value: string) => {
    setTranslations((prev) => ({
      ...prev,
      [formLang]: { ...prev[formLang], [field]: value },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload: ExperienceBase = {
      experience_id: experienceCustomId || null,
      company_logo: companyLogo,
      company_url: companyUrl,
      start_date: startDate,
      end_date: endDate,
      translations: {
        es: {
          role: translations.es.role,
          company: translations.es.company,
          location: translations.es.location,
          description: translations.es.description,
          description_cv: translations.es.description_cv.split('\n').filter(Boolean),
        },
        en: {
          role: translations.en.role,
          company: translations.en.company,
          location: translations.en.location,
          description: translations.en.description,
          description_cv: translations.en.description_cv.split('\n').filter(Boolean),
        },
      },
    };

    try {
      if (experienceToEdit) {
        const expId = experienceToEdit?.id;
        await api.put(`/portfolio/experience/${expId}`, payload);
      } else {
        await api.post('/portfolio/experience', payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Error al guardar experiencia');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl p-6 md:p-8 flex flex-col max-h-[90vh] shadow-2xl my-auto overflow-x-auto">
        
        {/* Encabezado Fijo */}
        <div className="flex justify-between items-center border-b border-slate-800 pb-4 shrink-0 min-w-full">
          <h2 className="text-2xl font-bold text-white">{experienceToEdit ? 'Editar Experiencia' : 'Nueva Experiencia'}</h2>
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
              <label className="block text-xs font-semibold text-slate-400 mb-1">Fecha de Inicio (ej. 2022)</label>
              <input type="text" value={startDate} onChange={(e) => setStartDate(e.target.value)} required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Fecha de Fin (ej. Presente)</label>
              <input type="text" value={endDate} onChange={(e) => setEndDate(e.target.value)} required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">URL del Logo de la Empresa</label>
              <input type="text" value={companyLogo} onChange={(e) => setCompanyLogo(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">URL Web de la Empresa</label>
              <input type="text" value={companyUrl} onChange={(e) => setCompanyUrl(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
            </div>
          </div>

          <div className="border border-slate-800 rounded-2xl p-4 bg-slate-950/40 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-sm font-bold text-indigo-400">Traducción de Experiencia</span>
              <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                <button type="button" onClick={() => setFormLang('es')} className={`px-3 py-1 rounded-md text-xs font-semibold transition ${formLang === 'es' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>ES</button>
                <button type="button" onClick={() => setFormLang('en')} className={`px-3 py-1 rounded-md text-xs font-semibold transition ${formLang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>EN</button>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Rol / Cargo ({formLang.toUpperCase()})</label>
                  <input type="text" value={translations[formLang].role} onChange={(e) => handleTranslationChange('role', e.target.value)} required={formLang === 'es'} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Empresa ({formLang.toUpperCase()})</label>
                  <input type="text" value={translations[formLang].company} onChange={(e) => handleTranslationChange('company', e.target.value)} required={formLang === 'es'} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Ubicación ({formLang.toUpperCase()})</label>
                <input type="text" value={translations[formLang].location} onChange={(e) => handleTranslationChange('location', e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Descripción ({formLang.toUpperCase()})</label>
                <TextareaAutosize minRows={3} value={translations[formLang].description} onChange={(e) => handleTranslationChange('description', e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Puntos CV ({formLang.toUpperCase()}) - Una línea por punto</label>
                <TextareaAutosize minRows={2} value={translations[formLang].description_cv} onChange={(e) => handleTranslationChange('description_cv', e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto" />
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