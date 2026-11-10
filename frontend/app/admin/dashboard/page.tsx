'use client';

import { UserResponse } from '@/types/auth';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/services/api';
import { 
  ProjectResponse, 
  AboutMeResponse, 
  ExperienceResponse, 
  EducationResponse, 
  PublicationResponse 
} from '@/types/portfolio';
import ProjectModal from '@/components/ProjectModal';
import ExperienceModal from '@/components/ExperienceModal';
import EducationModal from '@/components/EducationModal';

type ActiveTab = 'aboutme' | 'projects' | 'experience' | 'education' | 'publications';

export default function AdminDashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<ActiveTab>('projects');
  const [authorized, setAuthorized] = useState(false);
  const [loading, setLoading] = useState(true);

  // Estados de datos
  const [aboutMe, setAboutMe] = useState<AboutMeResponse | null>(null);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [experiences, setExperiences] = useState<ExperienceResponse[]>([]);
  const [educations, setEducations] = useState<EducationResponse[]>([]);
  const [publications, setPublications] = useState<PublicationResponse[]>([]);

  // Estados de Modales
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<ProjectResponse | null>(null);

  const [isExpModalOpen, setIsExpModalOpen] = useState(false);
  const [selectedExperience, setSelectedExperience] = useState<ExperienceResponse | null>(null);

  const [isEduModalOpen, setIsEduModalOpen] = useState(false);
  const [selectedEducation, setSelectedEducation] = useState<EducationResponse | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/admin/login');
    } else {
      setAuthorized(true);
      fetchAllData();
    }
  }, [router]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [aboutRes, projRes, expRes, eduRes, pubRes] = await Promise.all([
        api.get('/portfolio/about_me').catch(() => ({ data: null })),
        api.get('/portfolio/projects').catch(() => ({ data: [] })),
        api.get('/portfolio/experience').catch(() => ({ data: [] })),
        api.get('/portfolio/education').catch(() => ({ data: [] })),
        api.get('/portfolio/publications').catch(() => ({ data: [] }))
      ]);

      setAboutMe(aboutRes.data);
      setProjects(Array.isArray(projRes.data) ? projRes.data : []);
      setExperiences(Array.isArray(expRes.data) ? expRes.data : []);
      setEducations(Array.isArray(eduRes.data) ? eduRes.data : []);
      setPublications(Array.isArray(pubRes.data) ? pubRes.data : []);
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        router.push('/admin/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/admin/login');
  };

  const handleDelete = async (endpoint: string, id?: string) => {
    if (!id || !confirm('¿Estás seguro de que deseas eliminar este elemento?')) return;
    try {
      await api.delete(`/portfolio/${endpoint}/${id}`);
      fetchAllData();
    } catch (err) {
      console.error(`Error al eliminar de ${endpoint}:`, err);
      alert('Error al eliminar el registro.');
    }
  };

  if (!authorized) return null;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-3xl font-extrabold text-white">Panel de Control General</h1>
            <p className="text-slate-400 text-sm mt-1">Gestiona de forma multilingüe el contenido de tu portafolio</p>
          </div>
          <div className="flex gap-3">
            <a 
              href="/" 
              target="_blank" 
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-sm font-medium transition"
            >
              Ver Web Pública ↗
            </a>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30 rounded-xl text-sm font-medium transition"
            >
              Cerrar Sesión
            </button>
          </div>
        </header>

        {/* Pestañas de navegación */}
        <div className="flex gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
          {[
            { id: 'projects', label: `Proyectos (${projects.length})` },
            { id: 'experience', label: `Experiencia (${experiences.length})` },
            { id: 'education', label: `Educación (${educations.length})` },
            { id: 'publications', label: `Publicaciones (${publications.length})` },
            { id: 'aboutme', label: 'About Me' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ActiveTab)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition whitespace-nowrap ${
                activeTab === tab.id ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'bg-slate-900 text-slate-400 hover:bg-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-center py-12 text-slate-400 animate-pulse">Cargando datos del servidor...</p>
        ) : (
          <>
            {/* 1. PROYECTOS */}
            {activeTab === 'projects' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold text-white">Proyectos</h2>
                  <button 
                    onClick={() => { setSelectedProject(null); setIsProjectModalOpen(true); }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition"
                  >
                    + Nuevo Proyecto
                  </button>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-4">Título</th>
                        <th className="p-4">Tecnologías</th>
                        <th className="p-4 text-right">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {projects.map((proj) => (
                        <tr key={proj.id} className="hover:bg-slate-800/40">
                          <td className="p-4 font-semibold text-white">{proj.translations?.es?.name || proj.translations?.en?.name}</td>
                          <td className="p-4">{proj.technologies?.join(', ')}</td>
                          <td className="p-4 text-right space-x-2">
                            <button onClick={() => { setSelectedProject(proj); setIsProjectModalOpen(true); }} className="px-3 py-1 bg-slate-800 text-xs rounded text-slate-200 hover:bg-slate-700">Editar</button>
                            <button onClick={() => handleDelete('projects', proj.id)} className="px-3 py-1 bg-red-600/20 text-red-400 text-xs rounded hover:bg-red-600/30">Eliminar</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 2. EXPERIENCIA */}
            {activeTab === 'experience' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold text-white">Experiencia Laboral</h2>
                  <button 
                    onClick={() => { setSelectedExperience(null); setIsExpModalOpen(true); }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition"
                  >
                    + Nueva Experiencia
                  </button>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-4">Rol / Empresa</th>
                        <th className="p-4">Periodo</th>
                        <th className="p-4 text-right">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {experiences.map((exp) => (
                        <tr key={exp.id} className="hover:bg-slate-800/40">
                          <td className="p-4 font-semibold text-white">{exp.translations?.es?.role} en {exp.translations?.es?.company}</td>
                          <td className="p-4">{exp.start_date} - {exp.end_date}</td>
                          <td className="p-4 text-right space-x-2">
                            <button onClick={() => { setSelectedExperience(exp); setIsExpModalOpen(true); }} className="px-3 py-1 bg-slate-800 text-xs rounded text-slate-200">Editar</button>
                            <button onClick={() => handleDelete('experience', exp.id)} className="px-3 py-1 bg-red-600/20 text-red-400 text-xs rounded">Eliminar</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 3. EDUCACIÓN */}
            {activeTab === 'education' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold text-white">Educación</h2>
                  <button 
                    onClick={() => { setSelectedEducation(null); setIsEduModalOpen(true); }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition"
                  >
                    + Nueva Educación
                  </button>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-4">Título / Institución</th>
                        <th className="p-4">Años</th>
                        <th className="p-4 text-right">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {educations.map((edu) => (
                        <tr key={edu.id} className="hover:bg-slate-800/40">
                          <td className="p-4 font-semibold text-white">{edu.translations?.es?.degree} ({edu.translations?.es?.institution})</td>
                          <td className="p-4">{edu.start_year} - {edu.end_year}</td>
                          <td className="p-4 text-right space-x-2">
                            <button onClick={() => { setSelectedEducation(edu); setIsEduModalOpen(true); }} className="px-3 py-1 bg-slate-800 text-xs rounded text-slate-200">Editar</button>
                            <button onClick={() => handleDelete('education', edu.id)} className="px-3 py-1 bg-red-600/20 text-red-400 text-xs rounded">Eliminar</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 4. PUBLICACIONES */}
            {activeTab === 'publications' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold text-white">Publicaciones</h2>
                  <button 
                    onClick={() => alert('Modal de publicaciones pendiente')}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition"
                  >
                    + Nueva Publicación
                  </button>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-4">Título</th>
                        <th className="p-4">Año</th>
                        <th className="p-4 text-right">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {publications.map((pub) => (
                        <tr key={pub.id} className="hover:bg-slate-800/40">
                          <td className="p-4 font-semibold text-white">{pub.translations?.es?.title}</td>
                          <td className="p-4">{pub.year}</td>
                          <td className="p-4 text-right space-x-2">
                            <button onClick={() => handleDelete('publications', pub.id)} className="px-3 py-1 bg-red-600/20 text-red-400 text-xs rounded">Eliminar</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 5. ABOUT ME */}
            {activeTab === 'aboutme' && (
              <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl space-y-4">
                <h2 className="text-xl font-bold text-white">Información General (About Me)</h2>
                <p className="text-sm text-slate-400">Biografía actual cargada desde el servidor.</p>
                <div className="bg-slate-950 p-4 rounded-xl text-sm text-slate-300 border border-slate-800">
                  <p><strong>Título ES:</strong> {aboutMe?.translations?.es?.title || 'No registrado'}</p>
                  <p><strong>Título EN:</strong> {aboutMe?.translations?.en?.title || 'No registrado'}</p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modales */}
      <ProjectModal 
        isOpen={isProjectModalOpen}
        onClose={() => setIsProjectModalOpen(false)}
        onSuccess={fetchAllData}
        projectToEdit={selectedProject}
      />

      <ExperienceModal 
        isOpen={isExpModalOpen}
        onClose={() => setIsExpModalOpen(false)}
        onSuccess={fetchAllData}
        experienceToEdit={selectedExperience}
      />

      <EducationModal 
        isOpen={isEduModalOpen}
        onClose={() => setIsEduModalOpen(false)}
        onSuccess={fetchAllData}
        educationToEdit={selectedEducation}
      />
    </main>
  );
}