'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { AboutMeResponse } from '@/types/portfolio';
import TextareaAutosize from 'react-textarea-autosize';
import { abortOnSynchronousPlatformIOAccess } from 'next/dist/server/app-render/dynamic-rendering';

interface AboutMeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  aboutMeData: AboutMeResponse | null;
}

export default function AboutMeModal({ isOpen, onClose, onSuccess, aboutMeData }: AboutMeModalProps) {
  const [formLang, setFormLang] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // General Fields
  const [profileImage, setProfileImage] = useState('');
  const [cvFilename, setCvFilename] = useState('');

  // Profile Image Alt Translations
  const [profileImageAlt, setProfileImageAlt] = useState({ es: '', en: '' });

  // Main Content Translations
  const [translations, setTranslations] = useState({
    es: { title: '', intro: '', cv_title: '', cv_button: '', cv_intro: '' },
    en: { title: '', intro: '', cv_title: '', cv_button: '', cv_intro: '' },
  });

  useEffect(() => {
    if (aboutMeData) {
      setProfileImage(aboutMeData.profile_image || '');
      setCvFilename(aboutMeData.cv_filename || '');

      setProfileImageAlt({
        es: aboutMeData.profile_image_alt?.es || '',
        en: aboutMeData.profile_image_alt?.en || '',
      });

      setTranslations({
        es: {
          title: aboutMeData.translations?.es?.title || '',
          intro: aboutMeData.translations?.es?.intro?.join('\n\n') || '',
          cv_title: aboutMeData.translations?.es?.cv_title || '',
          cv_button: aboutMeData.translations?.es?.cv_button || '',
          cv_intro: aboutMeData.translations?.es?.cv_intro?.join('\n\n') || '',
        },
        en: {
          title: aboutMeData.translations?.en?.title || '',
          intro: aboutMeData.translations?.en?.intro?.join('\n\n') || '',
          cv_title: aboutMeData.translations?.en?.cv_title || '',
          cv_button: aboutMeData.translations?.en?.cv_button || '',
          cv_intro: aboutMeData.translations?.en?.cv_intro?.join('\n\n') || '',
        },
      });
    }
  }, [aboutMeData, isOpen]);

  if (!isOpen) return null;

  const handleTranslationChange = (field: keyof typeof translations['es'], value: string) => {
    setTranslations((prev) => ({
      ...prev,
      [formLang]: {
        ...prev[formLang],
        [field]: value,
      },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload = {
      profile_image: profileImage,
      cv_filename: cvFilename,
      profile_image_alt: profileImageAlt,
      languages: aboutMeData?.languages || [],
      translations: {
        es: {
          title: translations.es.title,
          intro: translations.es.intro.split('\n\n').filter(Boolean),
          cv_title: translations.es.cv_title,
          cv_button: translations.es.cv_button,
          cv_intro: translations.es.cv_intro.split('\n\n').filter(Boolean),
        },
        en: {
          title: translations.en.title,
          intro: translations.en.intro.split('\n\n').filter(Boolean),
          cv_title: translations.en.cv_title,
          cv_button: translations.en.cv_button,
          cv_intro: translations.en.cv_intro.split('\n\n').filter(Boolean),
        },
      },
    };

    //console.log("Objeto aboutMe actual:", aboutMeData);
    const aboutMeId = aboutMeData?.id;

    try {
      await api.put(`/portfolio/about_me/${aboutMeId}`, payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Error updating About Me section');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      {/* Contenedor principal con soporte de desplazamiento horizontal y vertical */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl p-6 md:p-8 flex flex-col max-h-[90vh] shadow-2xl my-auto overflow-x-auto">
        
        {/* Encabezado Fijo */}
        <div className="flex justify-between items-center border-b border-slate-800 pb-4 shrink-0 min-w-full">
          <h2 className="text-2xl font-bold text-white">Edit About Me</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-bold text-xl px-2">✕</button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-sm text-center shrink-0">
            {error}
          </div>
        )}

        {/* Formulario con Scroll Interno Vertical y Horizontal */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto overflow-x-auto space-y-6 pt-4 pr-1 min-w-full">
          
          {/* Configuración de imágenes y archivos */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Profile Image Path / URL</label>
              <input
                type="text"
                value={profileImage}
                onChange={(e) => setProfileImage(e.target.value)}
                placeholder="/uploads/profile.png"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">CV Filename</label>
              <input
                type="text"
                value={cvFilename}
                onChange={(e) => setCvFilename(e.target.value)}
                placeholder="resume_2026.pdf"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Textos alternativos de imagen */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Image Alt Text (ES)</label>
              <input
                type="text"
                value={profileImageAlt.es}
                onChange={(e) => setProfileImageAlt((prev) => ({ ...prev, es: e.target.value }))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Image Alt Text (EN)</label>
              <input
                type="text"
                value={profileImageAlt.en}
                onChange={(e) => setProfileImageAlt((prev) => ({ ...prev, en: e.target.value }))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Sección multilingüe */}
          <div className="border border-slate-800 rounded-2xl p-4 bg-slate-950/40 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-sm font-bold text-indigo-400">Content Translations</span>
              <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                <button
                  type="button"
                  onClick={() => setFormLang('es')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'es' ? 'bg-indigo-600 text-white' : 'text-slate-400'
                  }`}
                >
                  Spanish (ES)
                </button>
                <button
                  type="button"
                  onClick={() => setFormLang('en')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400'
                  }`}
                >
                  English (EN)
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Headline / Title ({formLang.toUpperCase()})
                </label>
                <input
                  type="text"
                  required={formLang === 'es'}
                  value={translations[formLang].title}
                  onChange={(e) => handleTranslationChange('title', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* 👈 Campo de Introducción con autoajuste completo de altura */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Intro Paragraphs ({formLang.toUpperCase()}) — Separate paragraphs with double enter
                </label>
                <TextareaAutosize
                  minRows={4}
                  value={translations[formLang].intro}
                  onChange={(e) => handleTranslationChange('intro', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">
                    CV Title ({formLang.toUpperCase()})
                  </label>
                  <input
                    type="text"
                    value={translations[formLang].cv_title}
                    onChange={(e) => handleTranslationChange('cv_title', e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">
                    CV Button Label ({formLang.toUpperCase()})
                  </label>
                  <input
                    type="text"
                    value={translations[formLang].cv_button}
                    onChange={(e) => handleTranslationChange('cv_button', e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  CV Intro Text ({formLang.toUpperCase()})
                </label>
                <TextareaAutosize
                  minRows={2}
                  value={translations[formLang].cv_intro}
                  onChange={(e) => handleTranslationChange('cv_intro', e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto"
                />
              </div>
            </div>
          </div>

          {/* Acciones fijas */}
          <div className="sticky bottom-0 bg-slate-900 pt-4 pb-1 border-t border-slate-800 flex justify-end gap-3 min-w-full">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-sm rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}