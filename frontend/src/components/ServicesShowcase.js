import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Globe, FileText, Users, CheckCircle, TrendingUp, Award } from 'lucide-react';

/**
 * Composant d'animation showcase des services d'immigration
 * Animation avec icônes et progression dynamique
 */
export default function ServicesShowcase() {
  const [activeService, setActiveService] = useState(0);

  const services = [
    {
      icon: Globe,
      emoji: '🌍',
      title: 'Consultation Personnalisée',
      description: 'Analyse approfondie de votre profil',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      icon: FileText,
      emoji: '📋',
      title: 'Préparation Dossiers',
      description: 'Constitution complète de vos documents',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    },
    {
      icon: Users,
      emoji: '👥',
      title: 'Accompagnement Expert',
      description: 'Suivi personnalisé par nos consultants',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30'
    },
    {
      icon: CheckCircle,
      emoji: '✅',
      title: 'Soumission & Suivi',
      description: 'Dépôt et suivi de votre demande',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30'
    },
    {
      icon: TrendingUp,
      emoji: '📈',
      title: 'Optimisation Profil',
      description: 'Maximisez vos chances de réussite',
      color: 'from-teal-500 to-teal-600',
      bgColor: 'bg-teal-500/10',
      borderColor: 'border-teal-500/30'
    },
    {
      icon: Award,
      emoji: '🏆',
      title: 'Réussite Garantie',
      description: 'Expertise reconnue depuis 2012',
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveService((prev) => (prev + 1) % services.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [services.length]);

  const IconComponent = services[activeService].icon;

  return (
    <div className="relative w-full bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#334155] rounded-2xl overflow-hidden border-2 border-orange-500/20 shadow-2xl">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      <div className="relative z-10 p-8 md:p-12">
        {/* Main service display */}
        <div className="flex flex-col md:flex-row items-center gap-8 mb-8">
          {/* Animated Icon */}
          <div className={`
            relative w-32 h-32 md:w-40 md:h-40 rounded-3xl 
            bg-gradient-to-br ${services[activeService].color}
            flex items-center justify-center
            shadow-2xl transform transition-all duration-700
            animate-float
          `}>
            <IconComponent className="w-16 h-16 md:w-20 md:h-20 text-white" />
            
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-3xl bg-white/20 animate-ping"></div>
            
            {/* Emoji overlay */}
            <div className="absolute -top-4 -right-4 text-4xl md:text-5xl animate-bounce">
              {services[activeService].emoji}
            </div>
          </div>

          {/* Service info */}
          <div className="flex-1 text-center md:text-left">
            <div className="inline-block px-4 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full mb-4">
              <span className="text-orange-400 font-semibold text-sm">
                Service {activeService + 1} / {services.length}
              </span>
            </div>
            <h3 className="text-3xl md:text-4xl font-bold text-white mb-3 leading-tight">
              {services[activeService].title}
            </h3>
            <p className="text-lg text-slate-300">
              {services[activeService].description}
            </p>
          </div>
        </div>

        {/* Service grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {services.map((service, index) => {
            const ServiceIcon = service.icon;
            const isActive = index === activeService;
            
            return (
              <button
                key={index}
                onClick={() => setActiveService(index)}
                className={`
                  relative p-4 rounded-xl transition-all duration-300
                  ${isActive 
                    ? `${service.bgColor} ${service.borderColor} border-2 scale-105` 
                    : 'bg-slate-800/50 border border-slate-700 hover:scale-105'
                  }
                `}
              >
                <div className="flex flex-col items-center gap-2">
                  <div className={`
                    w-12 h-12 rounded-xl flex items-center justify-center
                    ${isActive ? `bg-gradient-to-br ${service.color}` : 'bg-slate-700'}
                    transition-all duration-300
                  `}>
                    <ServiceIcon className={`w-6 h-6 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  </div>
                  <span className="text-xs font-medium text-center leading-tight">
                    <span className="text-lg">{service.emoji}</span>
                  </span>
                </div>
                
                {/* Active indicator */}
                {isActive && (
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="mt-8">
          <div className="flex justify-between text-sm text-slate-400 mb-2">
            <span>Progression du service</span>
            <span>{Math.round(((activeService + 1) / services.length) * 100)}%</span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-orange-500 via-yellow-500 to-green-500 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${((activeService + 1) / services.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-8">
          <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="text-2xl md:text-3xl font-bold text-orange-500">2000+</div>
            <div className="text-xs md:text-sm text-slate-400 mt-1">Clients Satisfaits</div>
          </div>
          <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="text-2xl md:text-3xl font-bold text-green-500">96%</div>
            <div className="text-xs md:text-sm text-slate-400 mt-1">Taux de Réussite</div>
          </div>
          <div className="text-center p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="text-2xl md:text-3xl font-bold text-blue-500">12+</div>
            <div className="text-xs md:text-sm text-slate-400 mt-1">Années d'Expertise</div>
          </div>
        </div>
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-float-slow"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.7}s`,
              animationDuration: `${5 + i}s`
            }}
          >
            <div className="w-2 h-2 bg-orange-500/30 rounded-full blur-sm"></div>
          </div>
        ))}
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-20px) rotate(5deg);
          }
        }
        @keyframes float-slow {
          0%, 100% {
            transform: translate(0, 0);
            opacity: 0.3;
          }
          50% {
            transform: translate(20px, -20px);
            opacity: 0.8;
          }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
        .animate-float-slow {
          animation: float-slow linear infinite;
        }
      `}</style>
    </div>
  );
}
