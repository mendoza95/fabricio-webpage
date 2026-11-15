import React from 'react';

// Define la interfaz para las propiedades que recibirá el modal
export interface PostDetail {
  slug: string;
  title: string;
  date: string;
  author: string;
  content_html: string;
}

interface PostModalProps {
  isOpen: boolean;
  post: PostDetail | null;
  onClose: () => void;
  language: string;
}

export const PostModal: React.FC<PostModalProps> = ({ isOpen, post, onClose, language }) => {
  if (!isOpen || !post) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 w-full max-w-3xl max-h-[85vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Cabecera del Modal */}
        <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
          <div className="text-xs text-slate-500 dark:text-slate-400 font-mono flex gap-3">
            <span>{post.date}</span>
            <span>•</span>
            <span>{post.author}</span>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 dark:hover:text-white p-1 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Contenido scrolleable del Post */}
        <div className="p-6 md:p-8 overflow-y-auto space-y-4">
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white">
            {post.title}
          </h2>
          
          <div 
            className="prose dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 leading-relaxed pt-4 space-y-4"
            dangerouslySetInnerHTML={{ __html: post.content_html }}
          />
        </div>

        {/* Pie del Modal */}
        <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-800 flex justify-end bg-slate-50 dark:bg-slate-900/50">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-sm font-medium rounded-xl transition"
          >
            {language === 'es' ? 'Cerrar' : 'Close'}
          </button>
        </div>

      </div>
    </div>
  );
};