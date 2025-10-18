import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';

/**
 * Composant d'animation cinématographique du processus d'immigration
 * Utilise des émojis/stickers pour raconter l'histoire du voyage d'immigration
 */
export default function ImmigrationJourneyAnimation() {
  const [currentStep, setCurrentStep] = useState(0);

  // Étapes du voyage d'immigration avec émojis
  const journeySteps = [
    {
      emoji: '📝',
      title: 'Préparation des Documents',
      description: 'Constitution du dossier',
      color: 'from-blue-500 to-blue-600',
      position: 'translate-x-0'
    },
    {
      emoji: '🎯',
      title: 'Dépôt de la Demande',
      description: 'Soumission officielle',
      color: 'from-purple-500 to-purple-600',
      position: 'translate-x-10'
    },
    {
      emoji: '⏳',
      title: 'Traitement',
      description: 'Analyse du dossier',
      color: 'from-orange-500 to-orange-600',
      position: 'translate-x-20'
    },
    {
      emoji: '✅',
      title: 'Visa Approuvé',
      description: 'Décision favorable',
      color: 'from-green-500 to-green-600',
      position: 'translate-x-32'
    },
    {
      emoji: '✈️',
      title: 'Vol vers le Canada',
      description: 'Départ imminent',
      color: 'from-sky-500 to-sky-600',
      position: 'translate-x-44'
    },
    {
      emoji: '🏠',
      title: 'Arrivée & Installation',
      description: 'Nouvelle vie commence',
      color: 'from-emerald-500 to-emerald-600',
      position: 'translate-x-56'
    },
    {
      emoji: '🎉',
      title: 'Succès !',
      description: 'Rêve réalisé',
      color: 'from-yellow-500 to-yellow-600',
      position: 'translate-x-64'
    }
  ];

  // Animation automatique qui cycle à travers les étapes
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % journeySteps.length);
    }, 2500); // Change toutes les 2.5 secondes

    return () => clearInterval(interval);
  }, [journeySteps.length]);

  return (
    <div className="relative w-full bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#334155] rounded-2xl p-8 overflow-hidden border-2 border-orange-500/20">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Title */}
      <div className="relative z-10 text-center mb-8">
        <h3 className="text-2xl md:text-3xl font-bold text-white mb-2">
          🌍 Votre Voyage d'Immigration
        </h3>
        <p className="text-slate-400 text-sm md:text-base">
          De la préparation jusqu'à votre nouvelle vie
        </p>
      </div>

      {/* Journey Timeline */}
      <div className="relative z-10 mb-8">
        {/* Progress Line */}
        <div className="absolute top-16 left-0 right-0 h-1 bg-slate-700 rounded-full">
          <div 
            className="h-full bg-gradient-to-r from-orange-500 to-green-500 rounded-full transition-all duration-1000 ease-out"
            style={{ width: `${((currentStep + 1) / journeySteps.length) * 100}%` }}
          ></div>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-7 gap-1 relative">
          {journeySteps.map((step, index) => (
            <div 
              key={index}
              className="flex flex-col items-center"
            >
              {/* Emoji Circle */}
              <div 
                className={`
                  relative w-16 h-16 md:w-20 md:h-20 rounded-full 
                  flex items-center justify-center
                  transition-all duration-500 transform
                  ${index === currentStep 
                    ? 'scale-125 shadow-2xl shadow-orange-500/50 bg-gradient-to-br ' + step.color 
                    : index < currentStep
                      ? 'scale-100 bg-gradient-to-br from-slate-600 to-slate-700'
                      : 'scale-90 bg-slate-800'
                  }
                `}
              >
                <span 
                  className={`
                    text-2xl md:text-3xl transition-all duration-300
                    ${index === currentStep ? 'animate-bounce' : ''}
                  `}
                >
                  {step.emoji}
                </span>
                
                {/* Glow effect for current step */}
                {index === currentStep && (
                  <div className="absolute inset-0 rounded-full bg-white/20 animate-ping"></div>
                )}
              </div>

              {/* Step Number */}
              <div className={`
                mt-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                ${index <= currentStep ? 'bg-orange-500 text-white' : 'bg-slate-700 text-slate-400'}
              `}>
                {index + 1}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Details */}
      <div className="relative z-10">
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
          <div className="p-6">
            <div className="flex items-center gap-4 mb-3">
              <div className={`
                w-16 h-16 rounded-xl bg-gradient-to-br ${journeySteps[currentStep].color}
                flex items-center justify-center text-4xl
                animate-pulse
              `}>
                {journeySteps[currentStep].emoji}
              </div>
              <div className="flex-1">
                <h4 className="text-xl font-bold text-white mb-1">
                  {journeySteps[currentStep].title}
                </h4>
                <p className="text-slate-400">
                  {journeySteps[currentStep].description}
                </p>
              </div>
            </div>

            {/* Progress indicators */}
            <div className="flex gap-2 justify-center mt-4">
              {journeySteps.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`
                    h-2 rounded-full transition-all duration-300
                    ${index === currentStep 
                      ? 'w-8 bg-orange-500' 
                      : index < currentStep
                        ? 'w-2 bg-green-500'
                        : 'w-2 bg-slate-600'
                    }
                  `}
                  aria-label={`Étape ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Floating emojis animation */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${3 + i}s`,
              opacity: 0.2
            }}
          >
            <span className="text-4xl">
              {['🌟', '🎯', '✨', '🚀', '💫'][i]}
            </span>
          </div>
        ))}
      </div>

      {/* CSS for floating animation */}
      <style jsx>{`
        @keyframes float {
          0% {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
          }
          10% {
            opacity: 0.3;
          }
          90% {
            opacity: 0.3;
          }
          100% {
            transform: translateY(-100px) rotate(360deg);
            opacity: 0;
          }
        }
        .animate-float {
          animation: float linear infinite;
        }
      `}</style>
    </div>
  );
}
