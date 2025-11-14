import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
// Select components removed - now handled by ContactFormWidget
// Textarea component removed - now handled by ContactFormWidget
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import api from '../utils/api';
import ContactFormWidget from '../components/ContactFormWidget';
import CRSCalculator from '../components/CRSCalculator';
import ImmigrationJourneyAnimation from '../components/ImmigrationJourneyAnimationRefined';
import ServicesShowcase from '../components/ServicesShowcase';
import AloriaLogo from '../components/AloriaLogo';
import { 
  Globe, ArrowRight, CheckCircle, Users, FileText, Clock, Star, MapPin, 
  Briefcase, GraduationCap, Heart, Shield, Award, TrendingUp, Phone, 
  Mail, MessageCircle, ChevronRight, Zap, Target, Eye, Lightbulb,
  BarChart3, Headphones, BookOpen, Calendar, MousePointer2, Menu, X, Calculator
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  // Navigation state
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showAuthForm, setShowAuthForm] = useState(false);
  const [authData, setAuthData] = useState({
    email: '',
    password: ''
  });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  // Employee state moved to ContactFormWidget component
  const [animatedNumbers, setAnimatedNumbers] = useState({
    clients: 0,
    success: 0,
    countries: 0,
    experience: 0
  });
  const [openFAQ, setOpenFAQ] = useState(null);
  const [showContactWidget, setShowContactWidget] = useState(false);
  const [visibleSections, setVisibleSections] = useState(new Set());

  // Intersection Observer pour animations au scroll
  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    };

    const observerCallback = (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setVisibleSections(prev => new Set([...prev, entry.target.id]));
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observer toutes les sections avec un id
    const sections = document.querySelectorAll('section[id]');
    sections.forEach(section => observer.observe(section));

    return () => {
      sections.forEach(section => observer.unobserve(section));
    };
  }, []);

  // Helper pour appliquer les classes d'animation
  const getSectionClass = (sectionId, baseAnimation = 'animate-fade-in-up') => {
    return visibleSections.has(sectionId) ? baseAnimation : 'opacity-0';
  };

  const faqs = [
    {
      question: "Combien de temps prend le processus d'immigration ?",
      answer: "Les délais varient selon le pays et le type de visa. En moyenne : 3-6 mois pour les permis de travail, 6-12 mois pour les résidences permanentes. Nous vous fournissons un calendrier précis lors de l'évaluation initiale."
    },
    {
      question: "Quels sont vos taux de réussite ?",
      answer: "Notre taux de réussite global est de 98%. Ce taux élevé est dû à notre évaluation rigoureuse en amont et notre expertise dans la préparation des dossiers. Nous ne prenons que les dossiers où nous sommes confiants du succès."
    },
    {
      question: "Combien coûtent vos services ?",
      answer: "Nos honoraires varient selon la complexité du dossier (1500€ - 5000€). Nous proposons des plans de paiement flexibles et une transparence totale sur les coûts. L'évaluation initiale est gratuite."
    },
    {
      question: "Que se passe-t-il si mon dossier est refusé ?",
      answer: "Dans le rare cas d'un refus (2% des cas), nous analysons les motifs et préparons un nouveau dossier sans frais supplémentaires. Notre garantie satisfaction couvre cette situation."
    },
    {
      question: "Puis-je suivre l'avancement de mon dossier ?",
      answer: "Absolument ! Notre plateforme digitale vous permet de suivre chaque étape en temps réel. Vous recevez également des notifications par email et SMS pour chaque mise à jour importante."
    }
  ];

  // Animation des statistiques au scroll
  useEffect(() => {
    const targets = { clients: 2500, success: 98, countries: 15, experience: 12 };
    const duration = 2000;
    const steps = 60;
    const increment = duration / steps;

    const timers = Object.keys(targets).map(key => {
      const target = targets[key];
      const stepValue = target / steps;
      let current = 0;
      
      return setInterval(() => {
        current += stepValue;
        if (current >= target) {
          setAnimatedNumbers(prev => ({ ...prev, [key]: target }));
          clearInterval(timers[Object.keys(targets).indexOf(key)]);
        } else {
          setAnimatedNumbers(prev => ({ ...prev, [key]: Math.floor(current) }));
        }
      }, increment);
    });

    return () => timers.forEach(timer => clearInterval(timer));
  }, []);

  // Form data moved to ContactFormWidget component

  const services = [
    {
      icon: <Briefcase className="w-10 h-10" />,
      title: "Immigration Professionnelle",
      description: "Expertise complète pour les visas de travail, permis talents et opportunités professionnelles internationales.",
      features: ["Évaluation détaillée du profil", "Constitution du dossier complet", "Suivi personnalisé jusqu'à l'obtention"],
      color: "from-blue-500/20 to-blue-600/20 border-blue-500/30"
    },
    {
      icon: <GraduationCap className="w-10 h-10" />,
      title: "Visa Étudiant & Académique",
      description: "Accompagnement sur-mesure pour vos études à l'étranger, de l'inscription à l'intégration réussie.",
      features: ["Sélection d'établissements", "Dossier académique optimisé", "Support post-arrivée"],
      color: "from-green-500/20 to-green-600/20 border-green-500/30"
    },
    {
      icon: <Heart className="w-10 h-10" />,
      title: "Regroupement Familial",
      description: "Réunir votre famille en toute sérénité avec nos experts en droit de l'immigration familiale.",
      features: ["Procédures simplifiées", "Documentation exhaustive", "Accompagnement humain et bienveillant"],
      color: "from-purple-500/20 to-purple-600/20 border-purple-500/30"
    },
    {
      icon: <Shield className="w-10 h-10" />,
      title: "Résidence Permanente",
      description: "Votre projet de vie permanent avec un accompagnement stratégique pour chaque étape cruciale.",
      features: ["Stratégie optimale personnalisée", "Dossier béton garanti", "Taux de succès exceptionnel"],
      color: "from-orange-500/20 to-orange-600/20 border-orange-500/30"
    }
  ];

  const testimonials = [
    {
      name: "Marie-Claire Fouda",
      role: "Infirmière diplômée",
      country: "Canada 🇨🇦",
      text: "Franchement, ALORIA AGENCY c'est du sérieux! Mon permis de travail pour le Canada est sorti en 3 mois seulement. L'équipe là, ils sont trop forts, ils m'ont suivi de A à Z. Je suis trop contente, c'est top!",
      rating: 5,
      image: "M"
    },
    {
      name: "Jean-Paul Mbarga", 
      role: "Étudiant en Informatique",
      country: "France 🇫🇷",
      text: "Eh, mes amis, si vous cherchez pour aller en France, passez par ALORIA! Mon visa étudiant est sorti sans problème. Ils connaissent bien le terrain, tout est clair. Je recommande à 100%!",
      rating: 5,
      image: "J"
    },
    {
      name: "Patrick Ekotto",
      role: "Ingénieur Réseaux",
      country: "Canada 🇨🇦",
      text: "ALORIA m'a vraiment aidé pour ma résidence permanente au Canada. Le processus était bien expliqué, pas de stress du tout. Aujourd'hui je suis établi là-bas avec ma famille. Merci infiniment!",
      rating: 5,
      image: "P"
    },
    {
      name: "Sylvie Atangana",
      role: "Comptable professionnelle",
      country: "France 🇫🇷",
      text: "C'est une agence sérieuse, ça marche bien! Ils m'ont accompagnée pour mon Passeport Talent en France. Le dossier était bien monté, tout est passé nickel. Je suis vraiment satisfaite, que Dieu les bénisse!",
      rating: 5,
      image: "S"
    }
  ];

  const processSteps = [
    { 
      step: '01', 
      title: 'Consultation Gratuite', 
      desc: 'Évaluation personnalisée de votre profil et de vos objectifs d\'immigration',
      icon: Target,
      details: ['Analyse du profil', 'Stratégie personnalisée', 'Recommandations expertes']
    },
    { 
      step: '02', 
      title: 'Constitution du Dossier', 
      desc: 'Préparation méticuleuse de tous les documents requis avec vérification complète',
      icon: FileText,
      details: ['Documents officiels', 'Traductions certifiées', 'Vérifications multiples']
    },
    { 
      step: '03', 
      title: 'Suivi en Temps Réel', 
      desc: 'Plateforme digitale pour suivre l\'avancement avec notifications automatiques',
      icon: BarChart3,
      details: ['Dashboard personnel', 'Notifications SMS/Email', 'Mises à jour instantanées']
    },
    { 
      step: '04', 
      title: 'Succès Garanti', 
      desc: 'Obtention de votre visa avec support post-approbation pour l\'installation',
      icon: Award,
      details: ['Approbation officielle', 'Guide d\'installation', 'Support continu']
    }
  ];

  // Authentification pour accéder au formulaire
  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/login', authData);
      const { access_token, user } = response.data;
      
      // Vérifier que c'est un manager ou employé
      if (user.role !== 'MANAGER' && user.role !== 'EMPLOYEE') {
        toast.error('Seuls les gestionnaires et employés peuvent créer des clients');
        return;
      }
      
      localStorage.setItem('token', access_token);
      api.defaults.headers.Authorization = `Bearer ${access_token}`;
      
      setCurrentUser(user);
      setIsAuthenticated(true);
      setShowAuthForm(false);
      
      // Employee loading now handled by ContactFormWidget
      
      toast.success(`Bienvenue ${user.full_name} !`);
    } catch (error) {
      toast.error('Email ou mot de passe incorrect');
    }
  };

  // loadEmployees function moved to ContactFormWidget component

  // Old form handler removed - contact form now handled by ContactFormWidget

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] overflow-hidden">
      {/* Header Navigation - Mobile-First */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0F172A]/95 backdrop-blur-lg border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo - Responsive */}
            <div className="flex items-center">
              <AloriaLogo className="h-8 sm:h-10" showText={true} />
            </div>
            
            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-6 xl:space-x-8">
              <a href="#services" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Services
              </a>
              <a href="#pays" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Destinations
              </a>
              <a href="#processus" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Processus
              </a>
              <a href="#temoignages" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Témoignages
              </a>
              <a href="#calculateur-crs" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Calculateur
              </a>
              <a href="#contact-section" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                Contact
              </a>
              <a href="#faq" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105 text-sm xl:text-base">
                FAQ
              </a>
              <Button 
                onClick={() => navigate('/login')}
                variant="outline"
                className="border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white transition-all duration-300 text-sm"
              >
                <ArrowRight className="w-4 h-4 mr-2" />
                Connexion
              </Button>
            </nav>

            {/* Mobile Menu Button */}
            <div className="flex items-center space-x-2 lg:hidden">
              <Button 
                onClick={() => navigate('/login')}
                size="sm"
                className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 text-xs touch-manipulation"
              >
                <ArrowRight className="w-3 h-3 mr-1" />
                <span className="hidden xs:inline">Connexion</span>
                <span className="xs:hidden">Login</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="p-2 text-slate-300 hover:text-orange-500 hover:bg-slate-800 touch-manipulation"
              >
                {showMobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>

            <button 
              className="lg:hidden text-slate-300"
              onClick={() => setShowMobileMenu(!showMobileMenu)}
            >
              {showMobileMenu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </header>

        {/* Mobile Menu Overlay */}
        {showMobileMenu && (
          <div className="fixed inset-0 z-40 bg-[#0F172A]/95 backdrop-blur-lg lg:hidden">
            <div className="pt-20 px-4 sm:px-6">
              <nav className="space-y-4">
                <a 
                  href="#services" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center mr-3">
                      <ArrowRight className="w-4 h-4 text-orange-400" />
                    </div>
                    Services
                  </div>
                </a>
                <a 
                  href="#pays" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                      <Globe className="w-4 h-4 text-blue-400" />
                    </div>
                    Destinations
                  </div>
                </a>
                <a 
                  href="#processus" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center mr-3">
                      <CheckCircle className="w-4 h-4 text-purple-400" />
                    </div>
                    Notre Processus
                  </div>
                </a>
                <a 
                  href="#temoignages" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center mr-3">
                      <Users className="w-4 h-4 text-green-400" />
                    </div>
                    Témoignages
                  </div>
                </a>
                <a 
                  href="#calculateur-crs" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center mr-3">
                      <Calculator className="w-4 h-4 text-orange-400" />
                    </div>
                    Calculateur CRS
                  </div>
                </a>
                <a 
                  href="#contact-section" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-pink-500/20 rounded-lg flex items-center justify-center mr-3">
                      <Mail className="w-4 h-4 text-pink-400" />
                    </div>
                    Contact
                  </div>
                </a>
                <a 
                  href="#faq" 
                  className="block py-3 px-4 text-lg font-medium text-slate-300 hover:text-orange-500 hover:bg-slate-800/50 rounded-lg transition-all duration-300 touch-manipulation"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center mr-3">
                      <MessageCircle className="w-4 h-4 text-yellow-400" />
                    </div>
                    FAQ
                  </div>
                </a>
                
                {/* Mobile CTA */}
                <div className="pt-4 border-t border-slate-700">
                  <a href="#start-application" className="block" onClick={() => setShowMobileMenu(false)}>
                    <Button 
                      className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white py-4 text-lg font-semibold shadow-xl shadow-orange-500/25 touch-manipulation"
                    >
                      <MousePointer2 className="mr-2 w-5 h-5" />
                      Commencer Maintenant
                    </Button>
                  </a>
                </div>
              </nav>
            </div>
          </div>
        )}

      {/* Hero Section - Mobile-First Responsive */}
      <section className="pt-20 sm:pt-24 md:pt-28 pb-16 sm:pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden min-h-[600px] sm:min-h-screen flex items-center">
        {/* Animated background elements - Optimized for mobile */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-20 sm:-top-40 -right-20 sm:-right-40 w-40 sm:w-80 h-40 sm:h-80 bg-orange-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-20 sm:-bottom-40 -left-20 sm:-left-40 w-48 sm:w-96 h-48 sm:h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className="max-w-7xl mx-auto relative w-full">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Left Column - Mobile optimized */}
            <div className="space-y-6 sm:space-y-8 text-center lg:text-left animate-fade-in">
              <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm inline-flex items-center">
                <Zap className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                <span className="hidden sm:inline">Services d'Immigration de Confiance Depuis 2012</span>
                <span className="sm:hidden">Immigration Experts 2012</span>
              </Badge>
              
              <h1 className="text-3xl xs:text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
                Votre Rêve
                <span className="block bg-gradient-to-r from-orange-500 via-orange-400 to-yellow-400 bg-clip-text text-transparent mt-1 sm:mt-2">
                  d'Immigration
                </span>
                <span className="block text-slate-200">Devient Réalité</span>
              </h1>
              
              <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-slate-300 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                Expertise premium pour vos demandes de visa vers le <span className="text-orange-400 font-semibold">Canada</span> et 
                la <span className="text-blue-400 font-semibold">France</span>. 
                <span className="hidden sm:inline"> Nos experts certifiés transforment la complexité de l'immigration en un processus simple, transparent et efficace.</span>
              </p>

              {/* Features Grid - Responsive */}
              <div className="grid grid-cols-1 xs:grid-cols-2 gap-3 sm:gap-4 max-w-lg mx-auto lg:max-w-none lg:mx-0">
                <div className="flex items-center space-x-2 sm:space-x-3 p-2.5 sm:p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                  <CheckCircle className="w-4 h-4 sm:w-6 sm:h-6 text-green-400 flex-shrink-0" />
                  <span className="text-slate-200 font-medium text-sm sm:text-base">Suivi Temps Réel</span>
                </div>
                <div className="flex items-center space-x-2 sm:space-x-3 p-2.5 sm:p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <Shield className="w-4 h-4 sm:w-6 sm:h-6 text-blue-400 flex-shrink-0" />
                  <span className="text-slate-200 font-medium text-sm sm:text-base">Experts Certifiés</span>
                </div>
                <div className="flex items-center space-x-2 sm:space-x-3 p-2.5 sm:p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                  <Award className="w-4 h-4 sm:w-6 sm:h-6 text-purple-400 flex-shrink-0" />
                  <span className="text-slate-200 font-medium text-sm sm:text-base">98% Succès</span>
                </div>
                <div className="flex items-center space-x-2 sm:space-x-3 p-2.5 sm:p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
                  <Headphones className="w-4 h-4 sm:w-6 sm:h-6 text-orange-400 flex-shrink-0" />
                  <span className="text-slate-200 font-medium text-sm sm:text-base">Support 24/7</span>
                </div>
              </div>

              {/* CTA Buttons - Mobile optimized */}
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full">
                <Button 
                  size="lg" 
                  className="w-full sm:w-auto bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-6 sm:px-8 py-4 sm:py-6 text-base sm:text-lg shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300 hover:scale-105 touch-manipulation"
                  onClick={() => {
                    const crsCalculator = document.getElementById('calculateur-crs');
                    if (crsCalculator) {
                      crsCalculator.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                  }}
                >
                  <Calculator className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="hidden xs:inline">Commencer Maintenant</span>
                  <span className="xs:hidden">Commencer</span>
                </Button>
                <Button 
                  variant="outline"
                  size="lg"
                  className="w-full sm:w-auto border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white px-6 sm:px-8 py-4 sm:py-6 text-base sm:text-lg touch-manipulation"
                  onClick={() => document.getElementById('services').scrollIntoView({ behavior: 'smooth' })}
                >
                  <Eye className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                  <span className="hidden xs:inline">Découvrir Nos Services</span>
                  <span className="xs:hidden">Services</span>
                </Button>
              </div>
            </div>

            {/* Right Column - Immigration Journey Animation & Stats - Mobile responsive */}
            <div className="space-y-6 mt-8 lg:mt-0 animate-fade-in" style={{ animationDelay: '0.3s' }}>
              {/* Immigration Journey Animation avec stickers/émojis */}
              <ImmigrationJourneyAnimation />
              
              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 sm:gap-6">
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-orange-500/50 transition-all duration-300">
                <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl md:rounded-2xl flex items-center justify-center mx-auto mb-2 sm:mb-3 md:mb-4">
                    <Users className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 text-white" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1 sm:mb-2">{animatedNumbers.clients.toLocaleString()}+</h3>
                  <p className="text-slate-400 text-xs sm:text-sm md:text-base">Clients Satisfaits</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-green-500/50 transition-all duration-300">
                <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-xl md:rounded-2xl flex items-center justify-center mx-auto mb-2 sm:mb-3 md:mb-4">
                    <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 text-white" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1 sm:mb-2">{animatedNumbers.success}%</h3>
                  <p className="text-slate-400 text-xs sm:text-sm md:text-base">Taux de Réussite</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-blue-500/50 transition-all duration-300">
                <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl md:rounded-2xl flex items-center justify-center mx-auto mb-2 sm:mb-3 md:mb-4">
                    <Globe className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 text-white" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1 sm:mb-2">{animatedNumbers.countries}+</h3>
                  <p className="text-slate-400 text-xs sm:text-sm md:text-base">Pays Partenaires</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-purple-500/50 transition-all duration-300">
                <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl md:rounded-2xl flex items-center justify-center mx-auto mb-2 sm:mb-3 md:mb-4">
                    <Calendar className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 text-white" />
                  </div>
                  <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1 sm:mb-2">{animatedNumbers.experience}+</h3>
                  <p className="text-slate-400 text-xs sm:text-sm md:text-base">Années d'Expérience</p>
                </CardContent>
              </Card>
            </div>
            {/* End Stats Grid */}
            </div>
            {/* End Right Column */}
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className={`py-20 bg-gradient-to-b from-[#1E293B]/50 to-transparent transition-all duration-700 ${getSectionClass('services')}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30 mb-4">
              <Star className="w-4 h-4 mr-2" />
              Excellence & Expertise
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Nos Services Premium</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Des solutions sur-mesure pour chaque profil et chaque projet d'immigration, 
              avec l'expertise de nos consultants certifiés.
            </p>
            
            {/* Services Showcase Animation */}
            <div className="mt-12 max-w-6xl mx-auto">
              <ServicesShowcase />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mt-12">
            {services.map((service, idx) => (
              <Card key={idx} className={`bg-gradient-to-br ${service.color} border backdrop-blur-sm hover:scale-105 transition-all duration-500`}>
                <CardContent className="p-8">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="text-orange-400">
                      {service.icon}
                    </div>
                    <h3 className="text-2xl font-bold text-white">{service.title}</h3>
                  </div>
                  
                  <p className="text-slate-300 mb-6 leading-relaxed">
                    {service.description}
                  </p>

                  <ul className="space-y-3">
                    {service.features.map((feature, featIdx) => (
                      <li key={featIdx} className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span className="text-slate-200">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Countries Section */}
      <section id="pays" className={`py-20 transition-all duration-700 ${getSectionClass('pays')}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30 mb-4">
              <MapPin className="w-4 h-4 mr-2" />
              Destinations Premium
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Vos Destinations de Rêve</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Services d'immigration experts pour les destinations les plus prisées au monde.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {[
              { name: 'Canada', flag: '🇨🇦', desc: 'Travail, Études & Résidence Permanente - Immigration Express Entry, Permis de travail fermé/ouvert, Études supérieures', color: 'hover:border-red-500/50', bg: 'from-red-500/10 to-red-600/10' },
              { name: 'France', flag: '🇫🇷', desc: 'Passeport Talent & Études Supérieures - Visa étudiant, Regroupement familial, Carte de résident long séjour', color: 'hover:border-blue-500/50', bg: 'from-blue-500/10 to-blue-600/10' }
            ].map((country, idx) => (
              <Card key={country.name} className={`bg-gradient-to-br ${country.bg} border-slate-700/50 ${country.color} transition-all duration-500 hover:scale-105 text-center group`}>
                <CardContent className="p-8">
                  <div className="text-8xl mb-6 group-hover:scale-110 transition-transform duration-300">
                    {country.flag}
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">{country.name}</h3>
                  <p className="text-slate-300 leading-relaxed">{country.desc}</p>
                  <ChevronRight className="w-6 h-6 text-orange-400 mx-auto mt-4 group-hover:translate-x-2 transition-transform duration-300" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section id="processus" className={`py-20 bg-gradient-to-b from-[#1E293B]/50 to-transparent transition-all duration-700 ${getSectionClass('processus')}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/30 mb-4">
              <Lightbulb className="w-4 h-4 mr-2" />
              Processus Éprouvé
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Notre Méthodologie Gagnante</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Un processus structuré en 4 étapes pour maximiser vos chances de succès et 
              simplifier votre parcours d'immigration.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {processSteps.map((item, idx) => (
              <div key={idx} className="relative group">
                <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-orange-500/50 transition-all duration-500 hover:scale-105">
                  <CardContent className="p-8 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto mb-6 shadow-2xl shadow-orange-500/50 group-hover:rotate-12 transition-transform duration-300">
                      {item.step}
                    </div>
                    <item.icon className="w-10 h-10 text-orange-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                    <p className="text-slate-300 mb-4 leading-relaxed">{item.desc}</p>
                    <ul className="text-sm text-slate-400 space-y-1">
                      {item.details.map((detail, detailIdx) => (
                        <li key={detailIdx} className="flex items-center justify-center space-x-2">
                          <div className="w-1 h-1 bg-orange-400 rounded-full"></div>
                          <span>{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
                
                {idx < 3 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ChevronRight className="w-8 h-8 text-orange-500/50" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="temoignages" className={`py-20 transition-all duration-700 ${getSectionClass('temoignages')}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-green-500/10 text-green-400 border-green-500/30 mb-4">
              <Heart className="w-4 h-4 mr-2" />
              Témoignages Authentiques
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Ils Nous Font Confiance</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Découvrez les histoires inspirantes de nos clients qui ont réalisé leur rêve 
              d'immigration grâce à notre expertise.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {testimonials.map((testimonial, idx) => (
              <Card key={idx} className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-orange-500/50 transition-all duration-500 hover:scale-105">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center text-white font-bold">
                      {testimonial.image}
                    </div>
                    <div>
                      <h4 className="font-bold text-white">{testimonial.name}</h4>
                      <p className="text-sm text-slate-400">{testimonial.role}</p>
                    </div>
                  </div>
                  
                  <div className="flex space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  
                  <p className="text-slate-300 text-sm leading-relaxed mb-3">
                    "{testimonial.text}"
                  </p>
                  
                  <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30 text-xs">
                    {testimonial.country}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className={`py-20 bg-gradient-to-b from-transparent to-[#1E293B]/50 transition-all duration-700 ${getSectionClass('faq')}`}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30 mb-4">
              <MessageCircle className="w-4 h-4 mr-2" />
              Questions Fréquentes
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Tout Ce Que Vous Devez Savoir</h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Les réponses aux questions les plus posées par nos futurs clients
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <Card key={index} className="bg-[#1E293B] border-slate-700 overflow-hidden">
                <CardHeader 
                  className="cursor-pointer hover:bg-slate-800/50 transition-all duration-200"
                  onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
                >
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-white text-lg font-medium">{faq.question}</CardTitle>
                    <ChevronRight 
                      className={`w-5 h-5 text-orange-500 transform transition-transform duration-200 ${
                        openFAQ === index ? 'rotate-90' : ''
                      }`}
                    />
                  </div>
                </CardHeader>
                {openFAQ === index && (
                  <CardContent className="pt-0 pb-6">
                    <p className="text-slate-300 leading-relaxed">{faq.answer}</p>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>

          <div className="text-center mt-12">
            <Card className="bg-gradient-to-r from-orange-500/10 to-orange-600/10 border-orange-500/30 p-6 inline-block">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                  <Headphones className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                  <h3 className="text-white font-bold">Une question spécifique ?</h3>
                  <p className="text-slate-300 text-sm">Contactez notre équipe au +33 1 75 43 89 12</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Application Form */}
      <section id="contact-section" className={`py-20 bg-gradient-to-b from-[#1E293B]/50 to-[#0F172A] transition-all duration-700 ${getSectionClass('contact-section')}`}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30 mb-4">
              <Target className="w-4 h-4 mr-2" />
              Démarrage Immédiat
            </Badge>
            <h2 className="text-5xl font-bold text-white mb-6">Commencez Votre Aventure</h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Remplissez ce formulaire pour recevoir une évaluation gratuite et personnalisée 
              de votre profil d'immigration.
            </p>
          </div>

          {/* Authentication Modal */}
        {showAuthForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="bg-[#1E293B] border-slate-700 max-w-md w-full">
              <CardHeader>
                <CardTitle className="text-white">Authentification Requise</CardTitle>
                <CardDescription className="text-slate-400">
                  Seuls les gestionnaires et employés peuvent créer des clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAuth} className="space-y-4">
                  <div>
                    <Label className="text-slate-300">Email</Label>
                    <Input
                      type="email"
                      value={authData.email}
                      onChange={(e) => setAuthData({...authData, email: e.target.value})}
                      className="bg-[#0F172A] border-slate-600 text-white"
                      placeholder="votre.email@aloria.com"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">Mot de passe</Label>
                    <Input
                      type="password"
                      value={authData.password}
                      onChange={(e) => setAuthData({...authData, password: e.target.value})}
                      className="bg-[#0F172A] border-slate-600 text-white"
                      required
                    />
                  </div>
                  <div className="flex space-x-2">
                    <Button type="submit" className="flex-1 bg-orange-500 hover:bg-orange-600">
                      Se connecter
                    </Button>
                    <Button 
                      type="button"
                      variant="outline" 
                      onClick={() => setShowAuthForm(false)}
                      className="border-slate-600 text-slate-300"
                    >
                      Annuler
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 shadow-2xl">
            <CardContent className="p-8">
              {isAuthenticated && (
                <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <p className="text-green-400 font-medium">
                    ✅ Connecté en tant que {currentUser.full_name} ({currentUser.role === 'MANAGER' ? 'Gestionnaire' : 'Employé'})
                  </p>
                </div>
              )}
              
              {/* Nouveau formulaire de contact géré par ContactFormWidget */}
              <ContactFormWidget />
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Section Calculateur CRS */}
      <section id="calculateur-crs" className={`py-16 sm:py-20 lg:py-24 bg-gradient-to-b from-[#0F172A] to-[#1E293B] transition-all duration-700 ${getSectionClass('calculateur-crs')}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Section */}
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center p-3 bg-orange-500/10 rounded-2xl mb-6">
              <Calculator className="h-8 w-8 text-orange-500" />
            </div>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4 sm:mb-6">
              Vérifiez votre <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-600">Potentiel d'Admissibilité</span>
            </h2>
            <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed px-4">
              Estimation indicative basée sur le système <strong>Entrée Express du Canada</strong>. 
              Pour un résultat précis, utilisez l'outil officiel du Canada ou échangez avec nos conseillers ALORIA.
            </p>
          </div>

          {/* Calculateur CRS */}
          <div className="max-w-5xl mx-auto">
            <CRSCalculator 
              onOptimizeClick={() => {
                // Scroll vers le formulaire de contact
                const contactSection = document.querySelector('#contact-section');
                if (contactSection) {
                  contactSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  toast.info('📝 Remplissez le formulaire ci-dessous pour optimiser votre profil avec nos experts !');
                }
              }}
            />
          </div>

          {/* CTA Section */}
          <div className="mt-12 text-center">
            <div className="inline-flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg"
                className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-xl"
                onClick={() => window.open('https://www.canada.ca/fr/immigration-refugies-citoyennete/services/immigrer-canada/entree-express/admissibilite/criteres-selection-travailleur-qualifie-federal/grille-selection-six-facteurs.html', '_blank')}
              >
                <Globe className="mr-2 h-5 w-5" />
                Calculateur Officiel Canada
              </Button>
              <Button 
                size="lg"
                variant="outline"
                className="border-slate-600 text-white hover:bg-slate-800"
                onClick={() => {
                  const contactSection = document.querySelector('#contact-section');
                  if (contactSection) {
                    contactSection.scrollIntoView({ behavior: 'smooth' });
                  }
                }}
              >
                <MessageCircle className="mr-2 h-5 w-5" />
                Parler à un Conseiller
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0F172A] border-t border-slate-700/50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <AloriaLogo className="h-10 mb-4" showText={true} />
              <p className="text-slate-400 mb-6 leading-relaxed max-w-md">
                Votre partenaire de confiance depuis 2012 pour les services d'immigration premium 
                vers les destinations les plus prisées au monde.
              </p>
              <div className="flex items-center gap-2 mb-4 text-orange-500">
                <MapPin className="w-5 h-5" />
                <span className="text-slate-300 font-semibold">📍 Douala, Cameroun</span>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button variant="outline" size="sm" className="border-slate-600 text-slate-400 hover:text-white">
                  <Phone className="w-4 h-4 mr-2" />
                  +237 6 XX XX XX XX
                </Button>
                <Button variant="outline" size="sm" className="border-slate-600 text-slate-400 hover:text-white">
                  <Mail className="w-4 h-4 mr-2" />
                  contact@aloria-agency.com
                </Button>
              </div>
            </div>
            
            <div>
              <h3 className="font-bold mb-6 text-white text-lg">Navigation</h3>
              <ul className="space-y-3 text-slate-400">
                <li><a href="#services" className="hover:text-orange-500 transition-colors">Services Premium</a></li>
                <li><a href="#pays" className="hover:text-orange-500 transition-colors">Destinations</a></li>
                <li><a href="#processus" className="hover:text-orange-500 transition-colors">Notre Processus</a></li>
                <li><a href="#temoignages" className="hover:text-orange-500 transition-colors">Témoignages</a></li>
                <li><a href="#calculateur-crs" className="hover:text-orange-500 transition-colors">Calculateur CRS</a></li>
                <li><a href="#contact-section" className="hover:text-orange-500 transition-colors">Contact</a></li>
                <li><a href="#faq" className="hover:text-orange-500 transition-colors">FAQ</a></li>
                <li><a href="/login" className="hover:text-orange-500 transition-colors">Espace Client</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-6 text-white text-lg">Pays & Services</h3>
              <ul className="space-y-3 text-slate-400">
                <li className="flex items-center space-x-2">
                  <span>🇨🇦</span>
                  <span>Canada - Express Entry, Permis de Travail</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🇫🇷</span>
                  <span>France - Passeport Talent, Visa Étudiant</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>💼</span>
                  <span>Regroupement Familial</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🎓</span>
                  <span>Visas Étudiants & Académiques</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-700/50 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-slate-400 text-center md:text-left">
              &copy; 2025 ALORIA AGENCY. Tous droits réservés. | Expertise en Immigration Premium
            </p>
            <div className="flex items-center space-x-4 mt-4 md:mt-0">
              <Badge className="bg-green-500/10 text-green-400 border-green-500/30">
                <CheckCircle className="w-3 h-3 mr-1" />
                Certifié
              </Badge>
              <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                <Shield className="w-3 h-3 mr-1" />
                Sécurisé
              </Badge>
              <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30">
                <Award className="w-3 h-3 mr-1" />
                Premium
              </Badge>
            </div>
          </div>
        </div>
      </footer>

      {/* Contact Widget Flottant */}
      <div className="fixed bottom-6 right-6 z-50">
        {showContactWidget && (
          <Card className="mb-4 w-80 bg-[#1E293B] border-orange-500/50 shadow-2xl animate-fade-in">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-center">
                <CardTitle className="text-white text-lg">Besoin d'aide ?</CardTitle>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowContactWidget(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 cursor-pointer transition-all">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
                  <Phone className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-white font-medium">Appel Gratuit</p>
                  <p className="text-sm text-slate-400">+33 1 75 43 89 12</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 cursor-pointer transition-all">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-white font-medium">Email</p>
                  <p className="text-sm text-slate-400">contact@aloria-agency.com</p>
                </div>
              </div>
              
              <div 
                className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 cursor-pointer transition-all"
                onClick={() => {
                  const contactSection = document.querySelector('#contact-section');
                  if (contactSection) {
                    contactSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    toast.success('📝 Remplissez le formulaire pour votre évaluation gratuite !');
                  } else {
                    toast.error('Section contact non trouvée');
                  }
                }}
              >
                <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-white font-medium">Évaluation Gratuite</p>
                  <p className="text-sm text-slate-400">Formulaire en ligne</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
        <Button
          onClick={() => setShowContactWidget(!showContactWidget)}
          className="w-14 h-14 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 shadow-2xl hover:scale-110 transition-all duration-300"
        >
          {showContactWidget ? (
            <X className="w-6 h-6" />
          ) : (
            <MessageCircle className="w-6 h-6" />
          )}
        </Button>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out forwards;
        }
        
        .animate-bounce-gentle {
          animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-10px); }
          60% { transform: translateY(-5px); }
        }
        
        @keyframes pulse-glow {
          0%, 100% { 
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.4);
            transform: scale(1);
          }
          50% { 
            box-shadow: 0 0 40px rgba(249, 115, 22, 0.8);
            transform: scale(1.05);
          }
        }
        
        .animate-pulse-glow {
          animation: pulse-glow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}