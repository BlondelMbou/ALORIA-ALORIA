import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';
import { Calculator, RefreshCcw, TrendingUp } from 'lucide-react';

/**
 * Calculateur CRS (Comprehensive Ranking System) pour l'immigration au Canada
 * Basé sur le système de points du programme Entrée Express
 */
export default function CRSCalculator({ onOptimizeClick }) {
  const [formData, setFormData] = useState({
    age: '',
    education: '',
    language: '',
    canadianExperience: '',
    foreignExperience: '',
    jobOffer: ''
  });

  const [score, setScore] = useState(0);
  const [maxScore] = useState(630); // Score max pour les critères de base
  const [scoreBreakdown, setScoreBreakdown] = useState({});

  // Options pour chaque critère avec leurs points
  const ageOptions = [
    { value: '18-19', label: '18-19 ans', points: 99 },
    { value: '20-29', label: '20-29 ans', points: 110 },
    { value: '30', label: '30 ans', points: 105 },
    { value: '31', label: '31 ans', points: 99 },
    { value: '32', label: '32 ans', points: 94 },
    { value: '33', label: '33 ans', points: 88 },
    { value: '34', label: '34 ans', points: 83 },
    { value: '35', label: '35 ans', points: 77 },
    { value: '36', label: '36 ans', points: 72 },
    { value: '37', label: '37 ans', points: 66 },
    { value: '38', label: '38 ans', points: 61 },
    { value: '39', label: '39 ans', points: 55 },
    { value: '40', label: '40 ans', points: 50 },
    { value: '41', label: '41 ans', points: 39 },
    { value: '42', label: '42 ans', points: 28 },
    { value: '43', label: '43 ans', points: 17 },
    { value: '44', label: '44 ans', points: 6 },
    { value: '45+', label: '45 ans et plus', points: 0 }
  ];

  const educationOptions = [
    { value: 'secondaire', label: 'Secondaire', points: 28 },
    { value: 'collegial_1an', label: 'Diplôme collégial (1 an)', points: 84 },
    { value: 'collegial_2ans', label: 'Diplôme collégial (2 ans)', points: 91 },
    { value: 'collegial_3ans', label: 'Diplôme collégial (3 ans+)', points: 98 },
    { value: 'baccalaureat', label: 'Baccalauréat (Licence)', points: 112 },
    { value: 'deux_baccalaureats', label: 'Deux baccalauréats ou plus', points: 119 },
    { value: 'maitrise', label: 'Maîtrise (Master)', points: 126 },
    { value: 'doctorat', label: 'Doctorat (PhD)', points: 140 }
  ];

  const languageOptions = [
    { value: 'CLB4', label: 'CLB 4 ou moins (A2)', points: 0 },
    { value: 'CLB5', label: 'CLB 5 (B1)', points: 32 },
    { value: 'CLB6', label: 'CLB 6 (B1)', points: 68 },
    { value: 'CLB7', label: 'CLB 7 (B2)', points: 110 },
    { value: 'CLB8', label: 'CLB 8 (B2)', points: 122 },
    { value: 'CLB9', label: 'CLB 9+ (C1/C2)', points: 136 }
  ];

  const canadianExperienceOptions = [
    { value: 'none', label: 'Aucune', points: 0 },
    { value: '1year', label: '1 an', points: 40 },
    { value: '2years', label: '2 ans', points: 53 },
    { value: '3years', label: '3 ans', points: 64 },
    { value: '4years', label: '4 ans', points: 72 },
    { value: '5years', label: '5 ans ou plus', points: 80 }
  ];

  const foreignExperienceOptions = [
    { value: 'none', label: 'Aucune', points: 0 },
    { value: '1year', label: '1 an', points: 13 },
    { value: '2years', label: '2 ans', points: 25 },
    { value: '3years', label: '3 ans ou plus', points: 50 }
  ];

  const jobOfferOptions = [
    { value: 'none', label: 'Aucune', points: 0 },
    { value: 'noc00', label: 'Offre NOC 00 (Cadre supérieur)', points: 200 },
    { value: 'noc0AB', label: 'Offre NOC 0, A ou B (Qualifié)', points: 50 }
  ];

  // Calculer le score total
  useEffect(() => {
    const calculateScore = () => {
      let total = 0;
      const breakdown = {};

      // Âge
      const ageOption = ageOptions.find(opt => opt.value === formData.age);
      if (ageOption) {
        breakdown.age = ageOption.points;
        total += ageOption.points;
      }

      // Éducation
      const eduOption = educationOptions.find(opt => opt.value === formData.education);
      if (eduOption) {
        breakdown.education = eduOption.points;
        total += eduOption.points;
      }

      // Langue
      const langOption = languageOptions.find(opt => opt.value === formData.language);
      if (langOption) {
        breakdown.language = langOption.points;
        total += langOption.points;
      }

      // Expérience canadienne
      const canExpOption = canadianExperienceOptions.find(opt => opt.value === formData.canadianExperience);
      if (canExpOption) {
        breakdown.canadianExperience = canExpOption.points;
        total += canExpOption.points;
      }

      // Expérience étrangère
      const forExpOption = foreignExperienceOptions.find(opt => opt.value === formData.foreignExperience);
      if (forExpOption) {
        breakdown.foreignExperience = forExpOption.points;
        total += forExpOption.points;
      }

      // Offre d'emploi
      const jobOption = jobOfferOptions.find(opt => opt.value === formData.jobOffer);
      if (jobOption) {
        breakdown.jobOffer = jobOption.points;
        total += jobOption.points;
      }

      setScore(total);
      setScoreBreakdown(breakdown);
    };

    calculateScore();
  }, [formData]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleReset = () => {
    setFormData({
      age: '',
      education: '',
      language: '',
      canadianExperience: '',
      foreignExperience: '',
      jobOffer: ''
    });
    setScore(0);
    setScoreBreakdown({});
  };

  const getScoreLevel = () => {
    if (score >= 480) return { label: 'Potentiel très élevé', color: 'text-green-500', bg: 'bg-green-500' };
    if (score >= 400) return { label: 'Potentiel élevé', color: 'text-blue-500', bg: 'bg-blue-500' };
    if (score >= 350) return { label: 'Potentiel moyen', color: 'text-orange-500', bg: 'bg-orange-500' };
    return { label: 'Potentiel à améliorer', color: 'text-gray-500', bg: 'bg-gray-500' };
  };

  const scoreLevel = getScoreLevel();
  const percentage = (score / maxScore) * 100;

  return (
    <Card className="w-full bg-[#1E293B] border-slate-700 shadow-xl">
      <CardHeader className="border-b border-slate-700 pb-6">
        <div className="flex items-center gap-3">
          <Calculator className="h-8 w-8 text-orange-500" />
          <div>
            <CardTitle className="text-2xl font-bold text-white">
              Calculateur CRS Canada
            </CardTitle>
            <CardDescription className="text-slate-400 mt-1">
              Évaluez votre score Entrée Express en quelques clics
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-6 space-y-6">
        {/* Formulaire */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Âge */}
          <div className="space-y-2">
            <Label htmlFor="age" className="text-slate-200 font-medium flex items-center gap-2">
              🎂 Âge
            </Label>
            <Select value={formData.age} onValueChange={(value) => handleChange('age', value)}>
              <SelectTrigger id="age" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Sélectionnez votre âge" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {ageOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Éducation */}
          <div className="space-y-2">
            <Label htmlFor="education" className="text-slate-200 font-medium flex items-center gap-2">
              🎓 Niveau d'études
            </Label>
            <Select value={formData.education} onValueChange={(value) => handleChange('education', value)}>
              <SelectTrigger id="education" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Sélectionnez votre diplôme" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {educationOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Langue */}
          <div className="space-y-2">
            <Label htmlFor="language" className="text-slate-200 font-medium flex items-center gap-2">
              💬 Niveau de langue (CLB/NCLC)
            </Label>
            <Select value={formData.language} onValueChange={(value) => handleChange('language', value)}>
              <SelectTrigger id="language" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Sélectionnez votre niveau" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {languageOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Expérience canadienne */}
          <div className="space-y-2">
            <Label htmlFor="canadianExp" className="text-slate-200 font-medium flex items-center gap-2">
              🇨🇦 Expérience au Canada
            </Label>
            <Select value={formData.canadianExperience} onValueChange={(value) => handleChange('canadianExperience', value)}>
              <SelectTrigger id="canadianExp" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Années d'expérience" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {canadianExperienceOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Expérience étrangère */}
          <div className="space-y-2">
            <Label htmlFor="foreignExp" className="text-slate-200 font-medium flex items-center gap-2">
              🌍 Expérience étrangère
            </Label>
            <Select value={formData.foreignExperience} onValueChange={(value) => handleChange('foreignExperience', value)}>
              <SelectTrigger id="foreignExp" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Années d'expérience" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {foreignExperienceOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Offre d'emploi */}
          <div className="space-y-2">
            <Label htmlFor="jobOffer" className="text-slate-200 font-medium flex items-center gap-2">
              💼 Offre d'emploi au Canada
            </Label>
            <Select value={formData.jobOffer} onValueChange={(value) => handleChange('jobOffer', value)}>
              <SelectTrigger id="jobOffer" className="bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Type d'offre d'emploi" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {jobOfferOptions.map(option => (
                  <SelectItem key={option.value} value={option.value} className="text-white hover:bg-slate-700">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Résultat */}
        {score > 0 && (
          <div className="mt-8 space-y-6">
            {/* Score principal */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-xl border-2 border-slate-700 shadow-2xl">
              <div className="flex flex-col items-center space-y-4">
                {/* Graphique circulaire */}
                <div className="relative w-48 h-48">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="#334155"
                      strokeWidth="16"
                      fill="none"
                    />
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="#f97316"
                      strokeWidth="16"
                      fill="none"
                      strokeDasharray={`${(percentage / 100) * 553} 553`}
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-5xl font-bold text-white">{score}</div>
                    <div className="text-slate-400 text-sm">/ {maxScore}</div>
                  </div>
                </div>

                {/* Statut */}
                <div className={`text-xl font-semibold ${scoreLevel.color}`}>
                  {scoreLevel.label}
                </div>

                {/* Barre de progression */}
                <div className="w-full bg-slate-700 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-full ${scoreLevel.bg} transition-all duration-1000 ease-out rounded-full`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>

                {/* Note explicative */}
                <p className="text-sm text-slate-400 text-center max-w-lg">
                  <strong>Note:</strong> Ce score est indicatif. Votre CRS final peut varier selon d'autres facteurs
                  (conjoint, nomination provinciale, etc.). Score minimum requis en 2025: <strong>480-500 points</strong>.
                </p>
              </div>
            </div>

            {/* Détails par critère */}
            {Object.keys(scoreBreakdown).length > 0 && (
              <div className="bg-slate-800/50 p-6 rounded-lg border border-slate-700">
                <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-orange-500" />
                  Détail de votre score
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {scoreBreakdown.age !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">🎂 Âge</span>
                      <span className="text-white font-bold">{scoreBreakdown.age} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.education !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">🎓 Études</span>
                      <span className="text-white font-bold">{scoreBreakdown.education} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.language !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">💬 Langue</span>
                      <span className="text-white font-bold">{scoreBreakdown.language} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.canadianExperience !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">🇨🇦 Exp. Canada</span>
                      <span className="text-white font-bold">{scoreBreakdown.canadianExperience} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.foreignExperience !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">🌍 Exp. Étranger</span>
                      <span className="text-white font-bold">{scoreBreakdown.foreignExperience} pts</span>
                    </div>
                  )}
                  {scoreBreakdown.jobOffer !== undefined && (
                    <div className="flex justify-between items-center p-3 bg-slate-900 rounded-lg">
                      <span className="text-slate-300 text-sm">💼 Offre emploi</span>
                      <span className="text-white font-bold">{scoreBreakdown.jobOffer} pts</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={handleReset}
                variant="outline"
                className="bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
              >
                <RefreshCcw className="mr-2 h-4 w-4" />
                Réinitialiser
              </Button>
              
              <Button
                onClick={onOptimizeClick}
                className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg"
              >
                <TrendingUp className="mr-2 h-4 w-4" />
                Optimiser mon profil
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
