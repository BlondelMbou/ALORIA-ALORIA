import React, { useState, useEffect } from 'react';
import { Plane, FileCheck, Clock, CheckCircle, Home, Sparkles, FileText } from 'lucide-react';

/**
 * Composant raffiné d'animation du processus d'immigration
 * Design doux et professionnel avec palette harmonieuse
 */
export default function ImmigrationJourneyAnimation() {
  const [currentStep, setCurrentStep] = useState(0);

  // Étapes du voyage avec icônes vectorielles et palette douce
  const journeySteps = [
    {
      icon: FileText,
      title: 'Préparation',
      description: 'Constitution du dossier',
      gradient: 'from-blue-400/20 to-indigo-400/20',
      iconColor: 'text-blue-400',
      borderColor: 'border-blue-400/30'
    },
    {
      icon: FileCheck,
      title: 'Dépôt',
      description: 'Soumission officielle',
      gradient: 'from-purple-400/20 to-violet-400/20',
      iconColor: 'text-purple-400',
      borderColor: 'border-purple-400/30'
    },
    {
      icon: Clock,
      title: 'Traitement',
      description: 'Analyse en cours',
      gradient: 'from-amber-400/20 to-orange-400/20',
      iconColor: 'text-amber-400',
      borderColor: 'border-amber-400/30'
    },
    {
      icon: CheckCircle,
      title: 'Approbation',
      description: 'Visa accordé',
      gradient: 'from-emerald-400/20 to-green-400/20',
      iconColor: 'text-emerald-400',
      borderColor: 'border-emerald-400/30'
    },
    {
      icon: Plane,
      title: 'Départ',
      description: 'Vol imminent',
      gradient: 'from-sky-400/20 to-cyan-400/20',
      iconColor: 'text-sky-400',
      borderColor: 'border-sky-400/30'
    },
    {
      icon: Home,
      title: 'Installation',
      description: 'Nouvelle vie',
      gradient: 'from-teal-400/20 to-emerald-400/20',
      iconColor: 'text-teal-400',
      borderColor: 'border-teal-400/30'
    },
    {
      icon: Sparkles,
      title: 'Succès',
      description: 'Rêve réalisé',
      gradient: 'from-rose-400/20 to-pink-400/20',
      iconColor: 'text-rose-400',
      borderColor: 'border-rose-400/30'
    }
  ];

  // Animation automatique fluide
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % journeySteps.length);
    }, 3000); // 3 secondes par étape

    return () => clearInterval(interval);
  }, [journeySteps.length]);

  return (
    <div className="relative w-full bg-gradient-to-br from-slate-900/50 via-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-3xl p-6 md:p-10 overflow-hidden border border-slate-700/50 shadow-2xl">
      {/* Dégradés de fond doux */}
      <div className="absolute inset-0 overflow-hidden opacity-30">
        <div className="absolute -top-20 -right-20 w-96 h-96 bg-gradient-radial from-blue-500/10 to-transparent rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-gradient-radial from-orange-500/10 to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Titre avec typographie douce */}
      <div className="relative z-10 text-center mb-10">
        <h3 className="text-2xl md:text-4xl font-light text-white mb-3 tracking-wide">
          Votre Parcours d'Immigration
        </h3>
        <div className="w-24 h-1 bg-gradient-to-r from-transparent via-orange-400/50 to-transparent mx-auto mb-4 rounded-full"></div>
        <p className="text-slate-400 text-sm md:text-base font-light">
          Chaque étape, un pas vers votre avenir
        </p>
      </div>

      {/* Ligne de progression élégante */}
      <div className="relative z-10 mb-12">
        <div className="relative h-1 bg-gradient-to-r from-slate-700/50 via-slate-600/50 to-slate-700/50 rounded-full overflow-hidden">
          <div 
            className="absolute h-full bg-gradient-to-r from-blue-400 via-purple-400 via-orange-400 via-emerald-400 via-sky-400 via-teal-400 to-rose-400 rounded-full transition-all duration-1000 ease-in-out shadow-lg"
            style={{ 
              width: `${((currentStep + 1) / journeySteps.length) * 100}%`,
              boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
            }}
          ></div>
        </div>

        {/* Étapes avec design raffiné */}
        <div className="relative flex justify-between items-start mt-8 px-4">
          {journeySteps.map((step, index) => {
            const Icon = step.icon;
            const isActive = index === currentStep;
            const isPassed = index < currentStep;

            return (
              <div 
                key={index} 
                className={`flex flex-col items-center transition-all duration-700 ${
                  isActive ? 'scale-110' : isPassed ? 'scale-95 opacity-70' : 'scale-90 opacity-50'
                }`}
                style={{
                  flex: 1,
                  maxWidth: '120px'
                }}
              >
                {/* Cercle d'icône avec effet glassmorphism */}
                <div 
                  className={`
                    relative w-14 h-14 md:w-16 md:h-16 rounded-2xl 
                    bg-gradient-to-br ${step.gradient} 
                    backdrop-blur-md border ${step.borderColor}
                    flex items-center justify-center
                    transition-all duration-500 shadow-lg
                    ${isActive ? 'ring-4 ring-white/20 shadow-2xl' : ''}
                  `}
                >
                  <Icon 
                    className={`w-6 h-6 md:w-8 md:h-8 ${step.iconColor} transition-all duration-500 ${
                      isActive ? 'animate-bounce' : ''
                    }`}
                    strokeWidth={isActive ? 2.5 : 2}
                  />
                  
                  {/* Pulse effect pour l'étape active */}
                  {isActive && (
                    <div className="absolute inset-0 rounded-2xl bg-white/10 animate-ping"></div>
                  )}
                </div>

                {/* Texte avec fade in élégant */}
                <div className={`mt-3 text-center transition-all duration-500 ${
                  isActive ? 'opacity-100' : 'opacity-40'
                }`}>
                  <p className={`text-xs md:text-sm font-semibold transition-colors duration-500 ${
                    isActive ? 'text-white' : 'text-slate-400'
                  }`}>
                    {step.title}
                  </p>
                  <p className={`text-[10px] md:text-xs mt-1 transition-colors duration-500 ${
                    isActive ? 'text-slate-300' : 'text-slate-500'
                  }`}>
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Message inspirant avec animation fade */}
      <div className="relative z-10 text-center">
        <div className="inline-block px-6 py-3 bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-md rounded-2xl border border-slate-600/50 shadow-lg">
          <p className="text-sm md:text-base text-slate-300 font-light">
            {journeySteps[currentStep].title} : {journeySteps[currentStep].description}
          </p>
        </div>
      </div>

      {/* Indicateurs de progression subtils */}
      <div className="flex justify-center gap-2 mt-6 relative z-10">
        {journeySteps.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentStep(index)}
            className={`transition-all duration-300 rounded-full ${
              index === currentStep 
                ? 'w-8 h-2 bg-gradient-to-r from-orange-400 to-orange-500 shadow-lg' 
                : 'w-2 h-2 bg-slate-600 hover:bg-slate-500'
            }`}
            aria-label={`Aller à l'étape ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
