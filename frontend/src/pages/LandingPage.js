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
  BarChart3, Headphones, BookOpen, Calendar, MousePointer2
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

  const countries = [
    { value: 'Canada', label: 'Canada', flag: '🇨🇦' },
    { value: 'France', label: 'France', flag: '🇫🇷' }
  ];

  const visaTypes = {
    Canada: ['Permis de Travail', 'Permis d\'Études', 'Résidence Permanente (Entrée Express)'],
    France: ['Permis de Travail (Passeport Talent)', 'Visa Étudiant', 'Regroupement Familial']
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.email || !formData.phone || !formData.country || !formData.visa_type) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    try {
      await api.clients.create(formData);
      toast.success('Votre demande a été soumise ! Vérifiez votre email pour les détails de connexion.');
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
      }, 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Échec de la soumission');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Globe className="w-8 h-8 text-orange-500" />
              <span className="text-2xl font-bold text-white">ALORIA AGENCY</span>
            </div>
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#services" className="text-slate-300 hover:text-orange-500 font-medium transition-colors">
                Services
              </a>
              <a href="#pays" className="text-slate-300 hover:text-orange-500 font-medium transition-colors">
                Pays
              </a>
              <a href="#comment-ca-marche" className="text-slate-300 hover:text-orange-500 font-medium transition-colors">
                Comment ça marche
              </a>
              <Button 
                onClick={() => navigate('/login')}
                className="bg-transparent border-2 border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white"
                data-testid="header-login-btn"
              >
                Connexion
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column */}
            <div className="space-y-8 fade-in">
              <div className="inline-block">
                <span className="px-4 py-2 bg-orange-500/10 text-orange-400 rounded-full text-sm font-semibold border border-orange-500/20">
                  Services d'Immigration de Confiance
                </span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-white leading-tight">
                Votre Parcours
                <span className="gradient-text block mt-2">d'Immigration Commence Ici</span>
              </h1>
              
              <p className="text-xl text-slate-300 leading-relaxed">
                Accompagnement expert pour vos demandes de visa vers le Canada, la France, la Belgique et l'Allemagne. 
                Nous simplifions le processus d'immigration complexe avec transparence et efficacité.
              </p>

              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-slate-300">Suivi en temps réel</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-slate-300">Conseillers experts</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-slate-300">100% transparence</span>
                </div>
              </div>

              <a href="#start-application" className="inline-block">
                <Button 
                  size="lg" 
                  className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-8 py-6 text-lg shadow-lg shadow-orange-500/50"
                  data-testid="hero-get-started-btn"
                >
                  Commencer <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </a>
            </div>

            {/* Right Column - Stats Cards */}
            <div className="grid grid-cols-2 gap-6 fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-6 rounded-2xl border border-slate-700/50 card-hover">
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center mb-4 border border-orange-500/20">
                  <Globe className="w-6 h-6 text-orange-400" />
                </div>
                <h3 className="text-3xl font-bold text-white">4</h3>
                <p className="text-slate-400 mt-1">Pays</p>
              </div>
              
              <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-6 rounded-2xl border border-slate-700/50 card-hover">
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 border border-blue-500/20">
                  <FileText className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-3xl font-bold text-white">12+</h3>
                <p className="text-slate-400 mt-1">Types de Visa</p>
              </div>
              
              <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-6 rounded-2xl border border-slate-700/50 card-hover">
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4 border border-green-500/20">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-3xl font-bold text-white">98%</h3>
                <p className="text-slate-400 mt-1">Taux de Réussite</p>
              </div>
              
              <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-6 rounded-2xl border border-slate-700/50 card-hover">
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4 border border-purple-500/20">
                  <MessageCircle className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-3xl font-bold text-white">24/7</h3>
                <p className="text-slate-400 mt-1">Support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Countries Section */}
      <section id="pays" className="py-20 bg-[#1E293B]/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Pays que Nous Servons</h2>
            <p className="text-xl text-slate-300">Services d'immigration experts pour plusieurs destinations</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { name: 'Canada', flag: '🇨🇦', desc: 'Travail, Études & PR' },
              { name: 'France', flag: '🇫🇷', desc: 'Passeport Talent & Études' },
              { name: 'Belgique', flag: '🇧🇪', desc: 'Travail & Regroupement familial' },
              { name: 'Allemagne', flag: '🇩🇪', desc: 'Carte Bleue EU & Migration qualifiée' }
            ].map((country) => (
              <div key={country.name} className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-8 rounded-2xl border border-slate-700/50 hover:border-orange-500/50 transition-all card-hover text-center">
                <div className="text-6xl mb-4">{country.flag}</div>
                <h3 className="text-2xl font-bold text-white mb-2">{country.name}</h3>
                <p className="text-slate-400">{country.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="comment-ca-marche" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Comment Ça Marche</h2>
            <p className="text-xl text-slate-300">Étapes simples pour démarrer votre parcours d'immigration</p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Soumettre Demande', desc: 'Remplissez notre formulaire simple', icon: FileText },
              { step: '2', title: 'Assignation', desc: 'Jumelé avec un conseiller expert', icon: Users },
              { step: '3', title: 'Suivi Progrès', desc: 'Mises à jour en temps réel', icon: Clock },
              { step: '4', title: 'Atteindre Objectifs', desc: 'Recevez votre approbation', icon: CheckCircle }
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-6 rounded-2xl border border-slate-700/50 text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4 shadow-lg shadow-orange-500/50">
                    {item.step}
                  </div>
                  <item.icon className="w-8 h-8 text-orange-400 mx-auto mb-3" />
                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-slate-400">{item.desc}</p>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                    <ArrowRight className="w-6 h-6 text-orange-500/50" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Application Form */}
      <section id="start-application" className="py-20 bg-[#1E293B]/30">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Commencez Votre Demande</h2>
            <p className="text-xl text-slate-300">Remplissez le formulaire ci-dessous pour débuter votre parcours</p>
          </div>

          <form onSubmit={handleSubmit} className="bg-gradient-to-br from-[#1E293B] to-[#334155] p-8 rounded-2xl border border-slate-700/50 shadow-2xl">
            <div className="space-y-6">
              <div>
                <Label htmlFor="full_name" className="text-slate-300">Nom Complet *</Label>
                <Input
                  id="full_name"
                  data-testid="input-full-name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="Entrez votre nom complet"
                  className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="email" className="text-slate-300">Adresse Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    data-testid="input-email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="votre.email@exemple.com"
                    className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="phone" className="text-slate-300">Numéro de Téléphone *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    data-testid="input-phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+33 6 12 34 56 78"
                    className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="country" className="text-slate-300">Pays de Destination *</Label>
                  <Select
                    value={formData.country}
                    onValueChange={(value) => setFormData({ ...formData, country: value, visa_type: '' })}
                  >
                    <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white" data-testid="select-country">
                      <SelectValue placeholder="Sélectionner un pays" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1E293B] border-slate-600">
                      {countries.map((country) => (
                        <SelectItem key={country.value} value={country.value} className="text-white hover:bg-slate-700">
                          <span className="flex items-center">
                            <span className="mr-2">{country.flag}</span>
                            {country.label}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="visa_type" className="text-slate-300">Type de Visa *</Label>
                  <Select
                    value={formData.visa_type}
                    onValueChange={(value) => setFormData({ ...formData, visa_type: value })}
                    disabled={!formData.country}
                  >
                    <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white" data-testid="select-visa-type">
                      <SelectValue placeholder="Sélectionner le type" />
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
              </div>

              <div>
                <Label htmlFor="message" className="text-slate-300">Informations Complémentaires (Optionnel)</Label>
                <Textarea
                  id="message"
                  data-testid="textarea-message"
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Parlez-nous de vos objectifs d'immigration..."
                  rows={4}
                  className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50"
                disabled={loading}
                data-testid="submit-application-btn"
              >
                {loading ? (
                  <span className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Soumission en cours...
                  </span>
                ) : (
                  'Soumettre la Demande'
                )}
              </Button>
            </div>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0F172A] border-t border-slate-700/50 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <Globe className="w-8 h-8 text-orange-500" />
                <span className="text-2xl font-bold">ALORIA AGENCY</span>
              </div>
              <p className="text-slate-400 mb-4">
                Votre partenaire de confiance pour les services d'immigration vers le Canada, la France, la Belgique et l'Allemagne.
              </p>
            </div>
            
            <div>
              <h3 className="font-bold mb-4 text-white">Liens Rapides</h3>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#services" className="hover:text-orange-500 transition-colors">Services</a></li>
                <li><a href="#pays" className="hover:text-orange-500 transition-colors">Pays</a></li>
                <li><a href="/login" className="hover:text-orange-500 transition-colors">Connexion</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4 text-white">Contact</h3>
              <ul className="space-y-2 text-slate-400">
                <li>Email: info@aloriaagency.com</li>
                <li>Tél: +33 1 23 45 67 89</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-700/50 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 ALORIA AGENCY. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
