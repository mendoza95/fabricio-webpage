'use client';

import { useEffect, useState } from 'react';
import api from '@/services/api';
import { 
  AboutMeResponse, 
  ProjectResponse, 
  ExperienceResponse, 
  EducationResponse, 
  PublicationResponse, 
  PortfolioGlobalResponse, 
  UiTranslationsResponse 
} from '@/types/portfolio';

export default function Home() {
  const [language, setLanguage] = useState<'es' | 'en'>('es');
  const [loading, setLoading] = useState(true);

  // Estados para cada sección
  const [aboutMe, setAboutMe] = useState<AboutMeResponse | null>(null);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [experiences, setExperiences] = useState<ExperienceResponse[]>([]);
  const [educations, setEducations] = useState<EducationResponse[]>([]);
  const [publications, setPublications] = useState<PublicationResponse[]>([]);
  const [globalData, setGlobalData] = useState<PortfolioGlobalResponse | null>(null);
  const [uiTranslations, setUiTranslations] = useState<UiTranslationsResponse | null>(null);

  useEffect(() => {
    async function fetchPortfolioData() {
      try {
        const [
          aboutRes,
          projectsRes,
          expRes,
          eduRes,
          pubRes,
          globalRes,
          uiRes
        ] = await Promise.all([
          api.get('/portfolio/about_me').catch(() => ({ data: null })),
          api.get('/portfolio/projects').catch(() => ({ data: [] })),
          api.get('/portfolio/experience').catch(() => ({ data: [] })),
          api.get('/portfolio/education').catch(() => ({ data: [] })),
          api.get('/portfolio/publications').catch(() => ({ data: [] })),
          api.get('/portfolio/global').catch(() => ({ data: null })),
          api.get('/portfolio/ui_translations').catch(() => ({ data: null }))
        ]);

        setAboutMe(aboutRes.data);
        setProjects(Array.isArray(projectsRes.data) ? projectsRes.data : []);
        setExperiences(Array.isArray(expRes.data) ? expRes.data : []);
        setEducations(Array.isArray(eduRes.data) ? eduRes.data : []);
        setPublications(Array.isArray(pubRes.data) ? pubRes.data : []);
        setGlobalData(globalRes.data);
        setUiTranslations(uiRes.data);
      } catch (err) {
        console.error("Error al cargar los datos del portafolio:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchPortfolioData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
        <p className="text-xl animate-pulse font-medium">Cargando portafolio...</p>
      </div>
    );
  }

  // Traducción UI actual (fallback a títulos por defecto si no existen en la BD)
  const ui = uiTranslations?.translations?.[language];
  const aboutMeTranslation = aboutMe?.translations?.[language];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-16">
      <div className="max-w-5xl mx-auto space-y-16">
        
        {/* Navbar / Selector de Idioma */}
        {/* Navbar / Selector de Idioma */}
    <header className="flex justify-between items-center pb-4 border-b border-slate-800">
      <div className="flex gap-4 items-center">
        {globalData?.social_media.map((social, idx) => (
          <a
            key={idx}
            href={social.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-indigo-400 text-sm transition"
          >
            {social.name}
          </a>
        ))}

        {/* 👈 NUEVO: Enlace discreto para ir al Login de Administración */}
        <a
          href="/admin/login"
          className="text-xs text-slate-500 hover:text-indigo-400 transition ml-4 pl-4 border-l border-slate-800"
        >
          Admin ⚙️
        </a>
      </div>

      <div className="flex gap-2">
        <button 
          onClick={() => setLanguage('es')} 
          className={`px-3.5 py-1.5 rounded-lg text-sm font-semibold transition ${
            language === 'es' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-slate-900 text-slate-400 hover:bg-slate-800'
          }`}
        >
          ES
        </button>
        <button 
          onClick={() => setLanguage('en')} 
          className={`px-3.5 py-1.5 rounded-lg text-sm font-semibold transition ${
            language === 'en' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-slate-900 text-slate-400 hover:bg-slate-800'
          }`}
        >
          EN
        </button>
      </div>
    </header>

        {/* 1. SECCIÓN ABOUT ME */}
        {aboutMe && aboutMeTranslation && (
          <section className="bg-slate-900/80 border border-slate-800 p-8 md:p-10 rounded-3xl shadow-2xl backdrop-blur-sm">
            <div className="flex flex-col md:flex-row gap-8 items-center">
              {aboutMe.profile_image && (
                <img 
                  src={aboutMe.profile_image} 
                  alt={aboutMe.profile_image_alt?.[language] || "Profile"} 
                  className="w-36 h-36 md:w-44 md:h-44 rounded-2xl object-cover border-2 border-indigo-500/30 shadow-md"
                />
              )}
              <div className="space-y-4 flex-1">
                <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
                  {aboutMeTranslation.title}
                </h1>
                <div className="space-y-3 text-slate-300 text-base leading-relaxed">
                  {aboutMeTranslation.intro.map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            </div>

            {aboutMeTranslation.cv_button && (
              <div className="mt-8 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-white">{aboutMeTranslation.cv_title}</h3>
                  <p className="text-sm text-slate-400">{aboutMeTranslation.cv_intro?.[0]}</p>
                </div>
                <a 
                  href={`/cv/${aboutMe.cv_filename}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition shadow-lg shadow-indigo-600/20 text-center"
                >
                  {aboutMeTranslation.cv_button}
                </a>
              </div>
            )}
          </section>
        )}

        {/* 2. SECCIÓN EXPERIENCIA */}
        <section className="space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold text-indigo-400">
            {ui?.experience_title || (language === 'es' ? 'Experiencia Laboral' : 'Work Experience')}
          </h2>
          <div className="space-y-4">
            {experiences.map((exp, idx) => {
              const trans = exp.translations?.[language];
              return (
                <div key={exp.id || idx} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      {exp.company_logo && <img src={exp.company_logo} alt={trans?.company} className="w-8 h-8 rounded" />}
                      <h3 className="text-xl font-bold text-white">{trans?.role}</h3>
                    </div>
                    <p className="text-indigo-300 font-medium text-sm">{trans?.company} • {trans?.location}</p>
                    <p className="text-slate-300 text-sm">{trans?.description}</p>
                  </div>
                  <div className="text-xs text-slate-400 font-mono whitespace-nowrap">
                    {exp.start_date} - {exp.end_date}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* 3. SECCIÓN EDUCACIÓN */}
        <section className="space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold text-indigo-400">
            {ui?.education_title || (language === 'es' ? 'Educación' : 'Education')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {educations.map((edu, idx) => {
              const trans = edu.translations?.[language];
              return (
                <div key={edu.id || idx} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                  <h3 className="text-lg font-bold text-white">{trans?.degree}</h3>
                  <p className="text-indigo-300 text-sm mt-1">{trans?.institution}</p>
                  <p className="text-xs text-slate-400 mt-2">{edu.start_year} - {edu.end_year}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* 4. SECCIÓN PROYECTOS */}
        <section className="space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold text-indigo-400">
            {ui?.projects_title || (language === 'es' ? 'Proyectos' : 'Projects')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {projects.map((project, idx) => {
              const trans = project.translations?.[language];
              return (
                <div key={project.id || idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition">
                  <div className="space-y-4">
                    {project.image && (
                      <img src={project.image} alt={trans?.name} className="w-full h-48 object-cover rounded-xl" />
                    )}
                    <h3 className="text-xl font-bold text-white">{trans?.name}</h3>
                    <p className="text-slate-300 text-sm leading-relaxed">{trans?.description}</p>
                    
                    {/* Tecnologías */}
                    <div className="flex flex-wrap gap-2 pt-2">
                      {project.technologies.map((tech, i) => (
                        <span key={i} className="px-2.5 py-1 bg-indigo-950/60 text-indigo-300 border border-indigo-800/50 text-xs rounded-md font-medium">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Links del Proyecto */}
                  <div className="flex gap-4 mt-6 pt-4 border-t border-slate-800 text-sm">
                    {project.live_url && (
                      <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline font-medium">
                        {ui?.live_demo_button || 'Live Demo'}
                      </a>
                    )}
                    {project.github_urls.map((url, i) => (
                      <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white transition">
                        {ui?.github_repo_button || 'GitHub'} {project.github_urls.length > 1 ? `#${i+1}` : ''}
                      </a>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* 5. SECCIÓN PUBLICACIONES */}
        {publications.length > 0 && (
          <section className="space-y-6">
            <h2 className="text-2xl md:text-3xl font-bold text-indigo-400">
              {ui?.publications_title || (language === 'es' ? 'Publicaciones' : 'Publications')}
            </h2>
            <div className="space-y-4">
              {publications.map((pub, idx) => {
                const trans = pub.translations?.[language];
                return (
                  <div key={pub.id || idx} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <h3 className="text-lg font-bold text-white">{trans?.title}</h3>
                    <p className="text-sm text-slate-300 mt-1">{pub.authors} ({pub.year})</p>
                    <p className="text-xs text-indigo-300 italic mt-1">{trans?.journal}</p>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* 6. HABILIDADES Y PORTAFOLIO GLOBAL */}
        {globalData?.skills && globalData.skills.length > 0 && (
          <section className="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl space-y-4">
            <h2 className="text-xl font-bold text-white">
              {ui?.skills_cv || (language === 'es' ? 'Habilidades' : 'Skills')}
            </h2>
            <div className="flex flex-wrap gap-2">
              {globalData.skills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1 bg-slate-800 text-slate-200 text-sm rounded-lg border border-slate-700">
                  {skill[language]}
                </span>
              ))}
            </div>
          </section>
        )}

      </div>
    </main>
  );
}