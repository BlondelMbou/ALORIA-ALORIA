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
import { 
  Globe, ArrowRight, CheckCircle, Users, FileText, Clock, Star, MapPin, 
  Briefcase, GraduationCap, Heart, Shield, Award, TrendingUp, Phone, 
  Mail, MessageCircle, ChevronRight, Zap, Target, Eye, Lightbulb,
  BarChart3, Headphones, BookOpen, Calendar, MousePointer2, Menu, X
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  // Removed form state - now managed by ContactFormWidget component
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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
      name: "Marie Dubois",
      role: "Ingénieure Logiciel",
      country: "Canada 🇨🇦",
      text: "Grâce à ALORIA AGENCY, j'ai obtenu mon permis de travail au Canada en seulement 3 mois. Un service exceptionnel avec un suivi personnalisé extraordinaire !",
      rating: 5,
      image: "M"
    },
    {
      name: "Ahmed Ben Ali", 
      role: "Étudiant en Master",
      country: "France 🇫🇷",
      text: "L'équipe m'a accompagné parfaitement pour mon visa étudiant. Processus transparent, conseils avisés et résultats concrets. Je recommande vivement !",
      rating: 5,
      image: "A"
    },
    {
      name: "Chen Wei",
      role: "Consultant IT",
      country: "Canada 🇨🇦",
      text: "Processus totalement transparent avec une équipe dédiée. Ma résidence permanente a été approuvée sans le moindre stress. Professionnalisme remarquable !",
      rating: 5,
      image: "C"
    },
    {
      name: "Sophie Martin",
      role: "Architecte",
      country: "Allemagne 🇩🇪",
      text: "ALORIA AGENCY m'a aidée à obtenir ma Carte Bleue européenne. Expertise technique et accompagnement humain au rendez-vous. Un grand merci !",
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
      
      // Charger la liste des employés si c'est un manager
      if (user.role === 'MANAGER') {
        await loadEmployees();
      }
      
      toast.success(`Bienvenue ${user.full_name} !`);
    } catch (error) {
      toast.error('Email ou mot de passe incorrect');
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await api.get('/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des employés:', error);
    }
  };

  // Old form handler removed - contact form now handled by ContactFormWidget

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] overflow-hidden">
      {/* Header Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#0F172A]/95 backdrop-blur-lg border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                ALORIA AGENCY
              </span>
            </div>
            
            <nav className="hidden lg:flex items-center space-x-8">
              <a href="#services" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105">
                Services
              </a>
              <a href="#pays" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105">
                Destinations
              </a>
              <a href="#processus" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105">
                Notre Processus
              </a>
              <a href="#temoignages" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105">
                Témoignages
              </a>
              <a href="#faq" className="text-slate-300 hover:text-orange-500 font-medium transition-all duration-300 hover:scale-105">
                FAQ
              </a>
              <Button 
                onClick={() => navigate('/login')}
                variant="outline"
                className="border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white transition-all duration-300"
              >
                <ArrowRight className="w-4 h-4 mr-2" />
                Connexion
              </Button>
            </nav>

            <button 
              className="lg:hidden text-slate-300"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-[#0F172A]/95 backdrop-blur-lg lg:hidden">
          <div className="pt-20 px-4">
            <nav className="space-y-6">
              <a href="#services" className="block text-xl text-slate-300 hover:text-orange-500 transition-colors">
                Services
              </a>
              <a href="#pays" className="block text-xl text-slate-300 hover:text-orange-500 transition-colors">
                Destinations
              </a>
              <a href="#processus" className="block text-xl text-slate-300 hover:text-orange-500 transition-colors">
                Notre Processus
              </a>
              <a href="#temoignages" className="block text-xl text-slate-300 hover:text-orange-500 transition-colors">
                Témoignages
              </a>
              <a href="#faq" className="block text-xl text-slate-300 hover:text-orange-500 transition-colors">
                FAQ
              </a>
              <Button 
                onClick={() => navigate('/login')}
                className="bg-orange-500 text-white hover:bg-orange-600 w-full"
              >
                Connexion
              </Button>
            </nav>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className="max-w-7xl mx-auto relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column */}
            <div className="space-y-8 animate-fade-in">
              <Badge className="bg-orange-500/10 text-orange-400 border-orange-500/30 px-4 py-2">
                <Zap className="w-4 h-4 mr-2" />
                Services d'Immigration de Confiance Depuis 2012
              </Badge>
              
              <h1 className="text-5xl lg:text-7xl font-bold text-white leading-tight">
                Votre Rêve
                <span className="block bg-gradient-to-r from-orange-500 via-orange-400 to-yellow-400 bg-clip-text text-transparent mt-2">
                  d'Immigration
                </span>
                <span className="block text-slate-200">Devient Réalité</span>
              </h1>
              
              <p className="text-xl lg:text-2xl text-slate-300 leading-relaxed">
                Expertise premium pour vos demandes de visa vers le <span className="text-orange-400 font-semibold">Canada</span> et 
                la <span className="text-blue-400 font-semibold">France</span>. Nos experts certifiés transforment la complexité 
                de l'immigration en un processus simple, transparent et efficace.
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-3 p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <span className="text-slate-200 font-medium">Suivi Temps Réel</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                  <Shield className="w-6 h-6 text-blue-400" />
                  <span className="text-slate-200 font-medium">Experts Certifiés</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                  <Award className="w-6 h-6 text-purple-400" />
                  <span className="text-slate-200 font-medium">98% Succès</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
                  <Headphones className="w-6 h-6 text-orange-400" />
                  <span className="text-slate-200 font-medium">Support 24/7</span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <a href="#start-application">
                  <Button 
                    size="lg" 
                    className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-8 py-6 text-lg shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300 hover:scale-105"
                  >
                    <MousePointer2 className="mr-2 w-5 h-5" />
                    Commencer Maintenant
                  </Button>
                </a>
                <Button 
                  variant="outline"
                  size="lg"
                  className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white px-8 py-6 text-lg"
                  onClick={() => document.getElementById('services').scrollIntoView({ behavior: 'smooth' })}
                >
                  <Eye className="mr-2 w-5 h-5" />
                  Découvrir Nos Services
                </Button>
              </div>
            </div>

            {/* Right Column - Animated Stats */}
            <div className="grid grid-cols-2 gap-6 animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-orange-500/50 transition-all duration-500 hover:scale-105">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Users className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-4xl font-bold text-white mb-2">{animatedNumbers.clients.toLocaleString()}+</h3>
                  <p className="text-slate-400">Clients Satisfaits</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-green-500/50 transition-all duration-500 hover:scale-105">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <TrendingUp className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-4xl font-bold text-white mb-2">{animatedNumbers.success}%</h3>
                  <p className="text-slate-400">Taux de Réussite</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-blue-500/50 transition-all duration-500 hover:scale-105">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Globe className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-4xl font-bold text-white mb-2">{animatedNumbers.countries}+</h3>
                  <p className="text-slate-400">Pays Partenaires</p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 hover:border-purple-500/50 transition-all duration-500 hover:scale-105">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Calendar className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-4xl font-bold text-white mb-2">{animatedNumbers.experience}+</h3>
                  <p className="text-slate-400">Années d'Expérience</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-gradient-to-b from-[#1E293B]/50 to-transparent">
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
          </div>

          <div className="grid md:grid-cols-2 gap-8">
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
      <section id="pays" className="py-20">
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
      <section id="processus" className="py-20 bg-gradient-to-b from-[#1E293B]/50 to-transparent">
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
      <section id="temoignages" className="py-20">
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
      <section id="faq" className="py-20 bg-gradient-to-b from-transparent to-[#1E293B]/50">
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
      <section id="start-application" className="py-20 bg-gradient-to-b from-[#1E293B]/50 to-[#0F172A]">
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

      {/* Footer */}
      <footer className="bg-[#0F172A] border-t border-slate-700/50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Globe className="w-7 h-7 text-white" />
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                  ALORIA AGENCY
                </span>
              </div>
              <p className="text-slate-400 mb-6 leading-relaxed max-w-md">
                Votre partenaire de confiance depuis 2012 pour les services d'immigration premium 
                vers les destinations les plus prisées au monde.
              </p>
              <div className="flex space-x-4">
                <Button variant="outline" size="sm" className="border-slate-600 text-slate-400 hover:text-white">
                  <Phone className="w-4 h-4 mr-2" />
                  +33 1 23 45 67 89
                </Button>
                <Button variant="outline" size="sm" className="border-slate-600 text-slate-400 hover:text-white">
                  <Mail className="w-4 h-4 mr-2" />
                  Contact
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
                onClick={() => document.getElementById('start-application').scrollIntoView({ behavior: 'smooth' })}
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