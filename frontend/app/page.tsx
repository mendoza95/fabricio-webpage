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
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [loading, setLoading] = useState(true);

  // URLs del entorno
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  // Estados para cada sección
  const [aboutMe, setAboutMe] = useState<AboutMeResponse | null>(null);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [experiences, setExperiences] = useState<ExperienceResponse[]>([]);
  const [educations, setEducations] = useState<EducationResponse[]>([]);
  const [publications, setPublications] = useState<PublicationResponse[]>([]);
  const [globalData, setGlobalData] = useState<PortfolioGlobalResponse | null>(null);
  const [uiTranslations, setUiTranslations] = useState<UiTranslationsResponse | null>(null);

  useEffect(() => {
    // Cargar preferencia de tema guardada o usar 'dark' por defecto
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | null;
    if (savedTheme) {
      setTheme(savedTheme);
      if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } else {
      document.documentElement.classList.add('dark');
    }

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

  // Función para alternar entre modo oscuro y claro
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center text-slate-900 dark:text-white transition-colors">
        <p className="text-xl animate-pulse font-medium">Cargando portafolio...</p>
      </div>
    );
  }

  // Traducción UI actual (fallback a títulos por defecto si no existen en la BD)
  const ui = uiTranslations?.translations?.[language];
  const aboutMeTranslation = aboutMe?.translations?.[language];

  // Enlaces dinámicos para el Navigation Bar
  const navLinks = [
    { href: '#about', label: language === 'es' ? 'Sobre mí' : 'About' },
    { href: '#experience', label: ui?.experience_title || (language === 'es' ? 'Experiencia' : 'Experience') },
    { href: '#education', label: ui?.education_title || (language === 'es' ? 'Educación' : 'Education') },
    { href: '#projects', label: ui?.projects_title || (language === 'es' ? 'Proyectos' : 'Projects') },
    ...(publications.length > 0 
      ? [{ href: '#publications', label: ui?.publications_title || (language === 'es' ? 'Publicaciones' : 'Publications') }] 
      : []),
    ...(globalData?.skills && globalData.skills.length > 0 
      ? [{ href: '#skills', label: ui?.skills_cv || (language === 'es' ? 'Habilidades' : 'Skills') }] 
      : []),
    { href: '#contact', label: ui?.contact_title || (language === 'es' ? 'Contacto' : 'Contact') },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 flex flex-col scroll-smooth transition-colors duration-300">
      
      {/* 🧭 NAVBAR FIJO / STICKY CON LAS SECCIONES DE LA PÁGINA */}
      <header className="sticky top-0 z-50 bg-white/85 dark:bg-slate-950/85 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-6 md:px-16 py-4 transition-colors">
        <div className="max-w-5xl mx-auto flex justify-between items-center gap-4">
          
          {/* Enlaces a las secciones */}
          <nav className="flex gap-5 items-center overflow-x-auto py-1 no-scrollbar">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 text-sm font-medium transition whitespace-nowrap"
              >
                {link.label}
              </a>
            ))}

            {/* Enlace discreto al Admin */}
            <a
              href="/admin/login"
              className="text-xs text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition ml-2 pl-4 border-l border-slate-200 dark:border-slate-800 whitespace-nowrap"
            >
              Admin ⚙️
            </a>
          </nav>

          {/* Controles: Tema e Idioma */}
          <div className="flex items-center gap-3 shrink-0">
            {/* Botón de Alternar Modo Oscuro / Claro */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-slate-200 dark:bg-slate-900 text-slate-800 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-800 transition shadow-sm"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            {/* Selector de Idioma */}
            <div className="flex gap-1 bg-slate-200 dark:bg-slate-900 p-1 rounded-xl border border-slate-300 dark:border-slate-800">
              <button 
                onClick={() => setLanguage('es')} 
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  language === 'es' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                ES
              </button>
              <button 
                onClick={() => setLanguage('en')} 
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  language === 'en' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                EN
              </button>
            </div>
          </div>

        </div>
      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="flex-1 p-6 md:p-16">
        <div className="max-w-5xl mx-auto space-y-20">
          
          {/* 1. SECCIÓN ABOUT ME */}
          {aboutMe && aboutMeTranslation && (
            <section id="about" className="scroll-mt-24 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 p-8 md:p-10 rounded-3xl shadow-xl backdrop-blur-sm transition-colors">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                {aboutMe.profile_image && (
                  <img 
                    src={
                      aboutMe.profile_image.startsWith('http') 
                        ? aboutMe.profile_image 
                        : `${backendUrl}${aboutMe.profile_image.startsWith('/static/images/') ? '' : '/static/images/'}${aboutMe.profile_image}`
                    }
                    alt={aboutMe.profile_image_alt?.[language] || "Profile"} 
                    className="w-60 h-130 md:w-60 md:h-130 rounded-2xl object-cover border-2 border-indigo-500/30 shadow-md"
                  />
                )}
                <div className="space-y-4 flex-1">
                  <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-cyan-600 dark:from-indigo-400 dark:to-cyan-400">
                    {aboutMeTranslation.title}
                  </h1>
                  <div className="space-y-3 text-slate-600 dark:text-slate-300 text-base leading-relaxed">
                    {aboutMeTranslation.intro.map((paragraph, index) => (
                      <p key={index}>{paragraph}</p>
                    ))}
                  </div>
                </div>
              </div>

              {aboutMeTranslation.cv_button && (
                <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">{aboutMeTranslation.cv_title}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{aboutMeTranslation.cv_intro?.[0]}</p>
                  </div>
                  <a 
                    href={`${apiUrl}/cv/pdf/${language}`} 
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
          <section id="experience" className="scroll-mt-24 space-y-6">
            <h2 className="text-2xl md:text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {ui?.experience_title || (language === 'es' ? 'Experiencia Laboral' : 'Work Experience')}
            </h2>
            <div className="space-y-4">
              {experiences.map((exp, idx) => {
                const trans = exp.translations?.[language];
                return (
                  <div key={exp.id || idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row justify-between gap-4 shadow-sm transition-colors">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                      {exp.company_logo && (
                        <div className="w-20 h-12 shrink-0 overflow-hidden rounded-lg border border-slate-200 dark:border-slate-800 bg-dark p-1 flex items-center justify-center">
                          <img 
                            src={
                              exp.company_logo.startsWith('http') 
                                ? exp.company_logo 
                                : `${backendUrl}${exp.company_logo.startsWith('/static/images/') ? '' : '/static/images/'}${exp.company_logo}`
                            } 
                            alt={trans?.company} 
                            className="w-full h-full object-contain" 
                          />
                        </div>
                      )}
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white">{trans?.role}</h3>
                    </div>
                      <p className="text-indigo-600 dark:text-indigo-300 font-medium text-sm">{trans?.company} • {trans?.location}</p>
                      <p className="text-slate-600 dark:text-slate-300 text-sm">{trans?.description}</p>
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 font-mono whitespace-nowrap">
                      {exp.start_date} - {exp.end_date}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* 3. SECCIÓN EDUCACIÓN */}
          <section id="education" className="scroll-mt-24 space-y-6">
            <h2 className="text-2xl md:text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {ui?.education_title || (language === 'es' ? 'Educación' : 'Education')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {educations.map((edu, idx) => {
                const trans = edu.translations?.[language];
                return (
                  <div key={edu.id || idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm transition-colors">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{trans?.degree}</h3>
                    <p className="text-indigo-600 dark:text-indigo-300 text-sm mt-1">{trans?.institution}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">{edu.start_year} - {edu.end_year}</p>
                  </div>
                );
              })}
            </div>
          </section>

          {/* 4. SECCIÓN PROYECTOS */}
          <section id="projects" className="scroll-mt-24 space-y-6">
            <h2 className="text-2xl md:text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {ui?.projects_title || (language === 'es' ? 'Proyectos' : 'Projects')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {projects.map((project, idx) => {
                const trans = project.translations?.[language];
                return (
                  <div key={project.id || idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-300 dark:hover:border-slate-700 transition shadow-sm">
                    <div className="space-y-4">
                      {/*{project.image && (
                        <img 
                          src={
                            project.image.startsWith('http') 
                              ? project.image 
                              : `${backendUrl}${project.image.startsWith('/static/images/') ? '' : '/static/images/'}${project.image}`
                          } 
                          alt={trans?.name} 
                          className="w-full h-48 object-cover rounded-xl" 
                        />
                      )} */}
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white">{trans?.name}</h3>
                      <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">{trans?.description}</p>
                      
                      {/* Tecnologías */}
                      <div className="flex flex-wrap gap-2 pt-2">
                        {project.technologies.map((tech, i) => (
                          <span key={i} className="px-2.5 py-1 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/50 text-xs rounded-md font-medium">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Links del Proyecto */}
                    <div className="flex gap-4 mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 text-sm">
                      {project.live_url && (
                        <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium">
                          {ui?.live_demo_button || 'Live Demo'}
                        </a>
                      )}
                      {project.github_urls.map((url, i) => (
                        <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition">
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
            <section id="publications" className="scroll-mt-24 space-y-6">
              <h2 className="text-2xl md:text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {ui?.publications_title || (language === 'es' ? 'Publicaciones' : 'Publications')}
              </h2>
              <div className="space-y-4">
                {publications.map((pub, idx) => {
                  const trans = pub.translations?.[language];
                  return (
                    <div key={pub.id || idx} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm transition-colors">
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white">{trans?.title}</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{pub.authors} ({pub.year})</p>
                      <p className="text-xs text-indigo-600 dark:text-indigo-300 italic mt-1">{trans?.journal}</p>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* 6. HABILIDADES Y PORTAFOLIO GLOBAL */}
          {globalData?.skills && globalData.skills.length > 0 && (
            <section id="skills" className="scroll-mt-24 bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 p-8 rounded-3xl space-y-4 shadow-sm transition-colors">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {ui?.skills_cv || (language === 'es' ? 'Habilidades' : 'Skills')}
              </h2>
              <div className="flex flex-wrap gap-2">
                {globalData.skills.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-sm rounded-lg border border-slate-200 dark:border-slate-700">
                    {skill[language]}
                  </span>
                ))}
              </div>
            </section>
          )}

        </div>
      </main>

      {/* 📬 SECCIÓN DE CONTACTOS AL FINAL DE LA PÁGINA */}
      <footer id="contact" className="bg-slate-100 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 mt-20 py-12 px-6 md:px-16 transition-colors">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6 text-center md:text-left">
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">
              {ui?.contact_title || (language === 'es' ? '¡Conectemos!' : "Let's Connect!")}
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md">
              {language === 'es' 
                ? '¿Interesado en colaborar o tienes alguna pregunta? Encuéntrame en mis redes profesionales.' 
                : 'Interested in collaborating or have any questions? Find me on my professional networks.'}
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {globalData?.social_media.map((social, idx) => (
              <a
                key={idx}
                href={social.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2.5 bg-white dark:bg-slate-950 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-800 text-slate-800 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white rounded-xl text-sm font-medium transition shadow-sm"
              >
                {social.name} {social.username ? `(${social.username})` : ''}
              </a>
            ))}
          </div>
        </div>
      </footer>

    </div>
  );
}