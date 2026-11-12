'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { PublicationResponse, PublicationBase } from '@/types/portfolio';
import TextareaAutosize from 'react-textarea-autosize';

interface PublicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  publicationToEdit?: PublicationResponse | null;
}

export default function PublicationModal({ isOpen, onClose, onSuccess, publicationToEdit }: PublicationModalProps) {
  const [formLang, setFormLang] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Campos comunes basados en PublicationBase
  const [publicationCustomId, setPublicationCustomId] = useState('');
  const [authors, setAuthors] = useState('');
  const [year, setYear] = useState<string | number>('');
  const [urls, setUrls] = useState<string>('');

  // Campos traducibles basados en PublicationTranslation
  const [translations, setTranslations] = useState({
    es: { title: '', journal: '', journal_cv: '' },
    en: { title: '', journal: '', journal_cv: '' },
  });

  useEffect(() => {
    if (publicationToEdit) {
      setPublicationCustomId(publicationToEdit.publication_id || '');
      setAuthors(publicationToEdit.authors || '');
      setYear(publicationToEdit.year ?? '');
      setUrls(publicationToEdit.urls ? publicationToEdit.urls.join(', ') : '');

      setTranslations({
        es: {
          title: publicationToEdit.translations?.es?.title || '',
          journal: publicationToEdit.translations?.es?.journal || '',
          journal_cv: publicationToEdit.translations?.es?.journal_cv || '',
        },
        en: {
          title: publicationToEdit.translations?.en?.title || '',
          journal: publicationToEdit.translations?.en?.journal || '',
          journal_cv: publicationToEdit.translations?.en?.journal_cv || '',
        },
      });
    } else {
      setPublicationCustomId('');
      setAuthors('');
      setYear('');
      setUrls('');
      setTranslations({
        es: { title: '', journal: '', journal_cv: '' },
        en: { title: '', journal: '', journal_cv: '' },
      });
    }
  }, [publicationToEdit, isOpen]);

  if (!isOpen) return null;

  const handleTranslationChange = (field: 'title' | 'journal' | 'journal_cv', value: string) => {
    setTranslations((prev) => ({
      ...prev,
      [formLang]: { ...prev[formLang], [field]: value },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload: PublicationBase = {
      publication_id: publicationCustomId || null,
      authors,
      year,
      urls: urls.split(',').map((u) => u.trim()).filter(Boolean),
      translations: {
        es: {
          title: translations.es.title,
          journal: translations.es.journal,
          journal_cv: translations.es.journal_cv,
        },
        en: {
          title: translations.en.title,
          journal: translations.en.journal,
          journal_cv: translations.en.journal_cv,
        },
      },
    };

    try {
      if (publicationToEdit && publicationToEdit.id) {
        await api.put(`/portfolio/publications/${publicationToEdit.id}`, payload);
      } else {
        await api.post('/portfolio/publications', payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Error al guardar publicación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl p-6 md:p-8 flex flex-col max-h-[90vh] shadow-2xl my-auto overflow-x-auto">
        
        {/* Encabezado Fijo */}
        <div className="flex justify-between items-center border-b border-slate-800 pb-4 shrink-0 min-w-full">
          <h2 className="text-2xl font-bold text-white">
            {publicationToEdit ? 'Editar Publicación' : 'Nueva Publicación'}
          </h2>
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
              <label className="block text-xs font-semibold text-slate-400 mb-1">ID Personalizado (Opcional)</label>
              <input
                type="text"
                value={publicationCustomId}
                onChange={(e) => setPublicationCustomId(e.target.value)}
                placeholder="ej: my-pub-id"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Año</label>
              <input
                type="text"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                required
                placeholder="2024"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Autores</label>
              <input
                type="text"
                value={authors}
                onChange={(e) => setAuthors(e.target.value)}
                required
                placeholder="John Doe, Jane Smith"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">URLs (Separadas por comas)</label>
              <input
                type="text"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                placeholder="https://doi.org/..., https://arxiv.org/..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="border border-slate-800 rounded-2xl p-4 bg-slate-950/40 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-sm font-bold text-indigo-400">Traducción de Publicación</span>
              <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                <button
                  type="button"
                  onClick={() => setFormLang('es')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'es' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  ES
                </button>
                <button
                  type="button"
                  onClick={() => setFormLang('en')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  EN
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Título ({formLang.toUpperCase()})
                </label>
                <input
                  type="text"
                  value={translations[formLang].title}
                  onChange={(e) => handleTranslationChange('title', e.target.value)}
                  required={formLang === 'es'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Revista / Journal ({formLang.toUpperCase()})
                </label>
                <input
                  type="text"
                  value={translations[formLang].journal}
                  onChange={(e) => handleTranslationChange('journal', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Journal CV / Resumen Breve para CV ({formLang.toUpperCase()})
                </label>
                <TextareaAutosize
                  minRows={2}
                  value={translations[formLang].journal_cv}
                  onChange={(e) => handleTranslationChange('journal_cv', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto"
                />
              </div>
            </div>
          </div>

          {/* ACCIONES FIJAS */}
          <div className="sticky bottom-0 bg-slate-900 pt-4 pb-1 border-t border-slate-800 flex justify-end gap-3 min-w-full">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-sm rounded-xl transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {loading ? 'Guardando...' : publicationToEdit ? 'Actualizar' : 'Guardar'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}