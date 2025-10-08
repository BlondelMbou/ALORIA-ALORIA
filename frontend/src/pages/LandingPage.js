import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import api from '../utils/api';
import { 
  Globe, ArrowRight, CheckCircle, Users, FileText, Clock, Star, MapPin, 
  Briefcase, GraduationCap, Heart, Shield, Award, TrendingUp, Phone, 
  Mail, MessageCircle, ChevronRight, Zap, Target, Eye, Lightbulb,
  BarChart3, Headphones, BookOpen, Calendar, MousePointer2, Menu, X
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    country: '',
    visa_type: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [animatedNumbers, setAnimatedNumbers] = useState({
    clients: 0,
    success: 0,
    countries: 0,
    experience: 0
  });

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

  const countries = [
    { value: 'Canada', label: 'Canada', flag: '🇨🇦' },
    { value: 'France', label: 'France', flag: '🇫🇷' }
  ];

  const visaTypes = {
    Canada: ['Permis de Travail', 'Permis d\'Études', 'Résidence Permanente (Entrée Express)', 'Visa de Visiteur', 'Parrainage Familial'],
    France: ['Permis de Travail (Passeport Talent)', 'Visa Étudiant', 'Regroupement Familial', 'Carte de Résident', 'Visa Touristique']
  };

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.email || !formData.phone || !formData.country || !formData.visa_type) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    try {
      await api.post('/clients', formData);
      toast.success('🎉 Votre demande a été soumise avec succès ! Vérifiez votre email pour les informations de connexion.');
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        country: '',
        visa_type: '',
        message: ''
      });
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la soumission. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

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
                Expertise premium pour vos demandes de visa vers le <span className="text-orange-400 font-semibold">Canada</span>, 
                la <span className="text-blue-400 font-semibold">France</span>, la <span className="text-yellow-400 font-semibold">Belgique</span> et 
                l'<span className="text-red-400 font-semibold">Allemagne</span>. Nous transformons la complexité en simplicité.
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

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 shadow-2xl">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="full_name" className="text-slate-300 font-medium">Nom Complet *</Label>
                    <Input
                      id="full_name"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      placeholder="Entrez votre nom complet"
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-slate-300 font-medium">Adresse Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="votre.email@exemple.com"
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="phone" className="text-slate-300 font-medium">Téléphone *</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="+33 6 12 34 56 78"
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="country" className="text-slate-300 font-medium">Destination *</Label>
                    <Select
                      value={formData.country}
                      onValueChange={(value) => setFormData({ ...formData, country: value, visa_type: '' })}
                    >
                      <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                        <SelectValue placeholder="Sélectionner un pays" />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1E293B] border-slate-600">
                        {countries.map((country) => (
                          <SelectItem key={country.value} value={country.value} className="text-white hover:bg-slate-700">
                            <span className="flex items-center">
                              <span className="mr-3">{country.flag}</span>
                              {country.label}
                            </span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="visa_type" className="text-slate-300 font-medium">Type de Visa *</Label>
                  <Select
                    value={formData.visa_type}
                    onValueChange={(value) => setFormData({ ...formData, visa_type: value })}
                    disabled={!formData.country}
                  >
                    <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                      <SelectValue placeholder="Sélectionner le type de visa" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1E293B] border-slate-600">
                      {formData.country && visaTypes[formData.country]?.map((type) => (
                        <SelectItem key={type} value={type} className="text-white hover:bg-slate-700">
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="message" className="text-slate-300 font-medium">Message Personnalisé (Optionnel)</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    placeholder="Parlez-nous de vos objectifs, votre situation actuelle, vos préoccupations..."
                    rows={4}
                    className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
                  />
                </div>

                <Button
                  type="submit"
                  size="lg"
                  className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300 py-6 text-lg"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Traitement en cours...
                    </span>
                  ) : (
                    <>
                      <Zap className="mr-2 w-5 h-5" />
                      Obtenir Mon Évaluation Gratuite
                    </>
                  )}
                </Button>

                <p className="text-center text-sm text-slate-400 mt-4">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Vos informations sont sécurisées et confidentielles
                </p>
              </form>
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
                <li><a href="/login" className="hover:text-orange-500 transition-colors">Espace Client</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-6 text-white text-lg">Pays & Services</h3>
              <ul className="space-y-3 text-slate-400">
                <li className="flex items-center space-x-2">
                  <span>🇨🇦</span>
                  <span>Canada - Express Entry</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🇫🇷</span>
                  <span>France - Passeport Talent</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🇧🇪</span>
                  <span>Belgique - Carte Bleue</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🇩🇪</span>
                  <span>Allemagne - Migration</span>
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

      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.8s ease-out forwards;
        }
      `}</style>
    </div>
  );
}