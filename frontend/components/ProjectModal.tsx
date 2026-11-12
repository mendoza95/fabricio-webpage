'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { ProjectResponse, ProjectBase } from '@/types/portfolio';
import TextareaAutosize from 'react-textarea-autosize';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  projectToEdit?: ProjectResponse | null;
}

export default function ProjectModal({ isOpen, onClose, onSuccess, projectToEdit }: ProjectModalProps) {
  const [formLang, setFormLang] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [projectCustomId, setProjectCustomId] = useState('');
  const [image, setImage] = useState('');
  const [liveUrl, setLiveUrl] = useState('');
  const [githubUrls, setGithubUrls] = useState<string>('');
  const [technologies, setTechnologies] = useState<string>('');

  const [translations, setTranslations] = useState({
    es: { name: '', description: '', description_cv: '' },
    en: { name: '', description: '', description_cv: '' },
  });

  useEffect(() => {
    if (projectToEdit) {
      setProjectCustomId(projectToEdit.project_id || '');
      setImage(projectToEdit.image || '');
      setLiveUrl(projectToEdit.live_url || '');
      setGithubUrls(projectToEdit.github_urls ? projectToEdit.github_urls.join(', ') : '');
      setTechnologies(projectToEdit.technologies ? projectToEdit.technologies.join(', ') : '');

      setTranslations({
        es: {
          name: projectToEdit.translations?.es?.name || '',
          description: projectToEdit.translations?.es?.description || '',
          description_cv: projectToEdit.translations?.es?.description_cv?.join('\n') || '',
        },
        en: {
          name: projectToEdit.translations?.en?.name || '',
          description: projectToEdit.translations?.en?.description || '',
          description_cv: projectToEdit.translations?.en?.description_cv?.join('\n') || '',
        },
      });
    } else {
      setProjectCustomId('');
      setImage('');
      setLiveUrl('');
      setGithubUrls('');
      setTechnologies('');
      setTranslations({
        es: { name: '', description: '', description_cv: '' },
        en: { name: '', description: '', description_cv: '' },
      });
    }
  }, [projectToEdit, isOpen]);

  if (!isOpen) return null;

  const handleTranslationChange = (field: 'name' | 'description' | 'description_cv', value: string) => {
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

    const payload: ProjectBase = {
      project_id: projectCustomId || null,
      image,
      live_url: liveUrl || null,
      technologies: technologies.split(',').map((tech) => tech.trim()).filter(Boolean),
      github_urls: githubUrls.split(',').map((url) => url.trim()).filter(Boolean),
      translations: {
        es: {
          name: translations.es.name,
          description: translations.es.description,
          description_cv: translations.es.description_cv.split('\n').filter(Boolean),
        },
        en: {
          name: translations.en.name,
          description: translations.en.description,
          description_cv: translations.en.description_cv.split('\n').filter(Boolean),
        },
      },
    };

    try {
      if (projectToEdit && projectToEdit.id) {
        await api.put(`/portfolio/projects/${projectToEdit.id}`, payload);
      } else {
        await api.post('/portfolio/projects', payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error("Error al guardar el proyecto:", err);
      setError(err.response?.data?.detail || 'Error al guardar el registro');
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
            {projectToEdit ? 'Editar Proyecto' : 'Nuevo Proyecto'}
          </h2>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white font-bold text-xl px-2"
          >
            ✕
          </button>
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
                value={projectCustomId}
                onChange={(e) => setProjectCustomId(e.target.value)}
                placeholder="ej: my-project-id"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Ruta/URL de Imagen</label>
              <input
                type="text"
                value={image}
                onChange={(e) => setImage(e.target.value)}
                placeholder="/uploads/project1.png"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Tecnologías (Separadas por comas)</label>
              <input
                type="text"
                value={technologies}
                onChange={(e) => setTechnologies(e.target.value)}
                placeholder="React, FastAPI, MongoDB"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">URL En Vivo (Live Demo)</label>
              <input
                type="url"
                value={liveUrl}
                onChange={(e) => setLiveUrl(e.target.value)}
                placeholder="https://mi-proyecto.com"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Repositorios GitHub (Separados por comas)</label>
            <input
              type="text"
              value={githubUrls}
              onChange={(e) => setGithubUrls(e.target.value)}
              placeholder="https://github.com/user/repo1, https://github.com/user/repo2"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* SECCIÓN MULTILINGÜE */}
          <div className="border border-slate-800 rounded-2xl p-4 bg-slate-950/40 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-sm font-bold text-indigo-400">Traducción del Contenido</span>
              
              <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                <button
                  type="button"
                  onClick={() => setFormLang('es')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'es' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Español (ES)
                </button>
                <button
                  type="button"
                  onClick={() => setFormLang('en')}
                  className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                    formLang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Inglés (EN)
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Nombre del Proyecto ({formLang.toUpperCase()})
                </label>
                <input
                  type="text"
                  required={formLang === 'es'}
                  value={translations[formLang].name}
                  onChange={(e) => handleTranslationChange('name', e.target.value)}
                  placeholder={formLang === 'es' ? 'Mi Proyecto Genial' : 'My Awesome Project'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Descripción Principal ({formLang.toUpperCase()})
                </label>
                <TextareaAutosize
                  minRows={3}
                  value={translations[formLang].description}
                  onChange={(e) => handleTranslationChange('description', e.target.value)}
                  placeholder={formLang === 'es' ? 'Descripción del proyecto...' : 'Project description...'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none block overflow-x-auto"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Puntos para CV ({formLang.toUpperCase()}) — Un punto por línea
                </label>
                <TextareaAutosize
                  minRows={2}
                  value={translations[formLang].description_cv}
                  onChange={(e) => handleTranslationChange('description_cv', e.target.value)}
                  placeholder={formLang === 'es' ? 'Desarrollo de API con FastAPI\nIntegración con MongoDB' : 'API development with FastAPI\nMongoDB integration'}
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
              {loading ? 'Guardando...' : projectToEdit ? 'Actualizar Proyecto' : 'Crear Proyecto'}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}