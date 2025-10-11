import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { 
  ArrowRight, 
  CheckCircle, 
  Star, 
  Phone, 
  Mail, 
  MapPin, 
  Clock,
  Users,
  Award,
  Globe,
  MessageCircle,
  Send,
  ExternalLink,
  Calendar,
  Briefcase,
  Shield,
  TrendingUp,
  FileText,
  Heart,
  Target
} from 'lucide-react';

const LandingPageV3 = () => {
  const [companyInfo, setCompanyInfo] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    country: '',
    visa_type: '',
    budget_range: '',
    urgency_level: 'Normal',
    message: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [animatedStats, setAnimatedStats] = useState({
    cases: 0,
    success_rate: 0,
    countries: 0,
    satisfaction: 0
  });

  useEffect(() => {
    fetchCompanyInfo();
  }, []);

  useEffect(() => {
    if (companyInfo) {
      animateStats();
    }
  }, [companyInfo]);

  const fetchCompanyInfo = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/company-info`);
      if (response.ok) {
        const data = await response.json();
        setCompanyInfo(data);
      }
    } catch (error) {
      console.error('Error fetching company info:', error);
    }
  };

  const animateStats = () => {
    if (!companyInfo) return;

    const duration = 2000;
    const steps = 60;
    const stepDuration = duration / steps;

    const targets = {
      cases: companyInfo.statistics.successful_cases,
      success_rate: companyInfo.statistics.success_rate,
      countries: companyInfo.statistics.countries_served,
      satisfaction: companyInfo.statistics.client_satisfaction * 10
    };

    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;

      setAnimatedStats({
        cases: Math.floor(targets.cases * progress),
        success_rate: Math.floor(targets.success_rate * progress),
        countries: Math.floor(targets.countries * progress),
        satisfaction: (targets.satisfaction * progress).toFixed(1)
      });

      if (currentStep >= steps) {
        clearInterval(timer);
        setAnimatedStats({
          cases: targets.cases,
          success_rate: targets.success_rate,
          countries: targets.countries,
          satisfaction: targets.satisfaction.toFixed(1)
        });
      }
    }, stepDuration);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact-messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          lead_source: 'WEBSITE'
        })
      });

      if (response.ok) {
        toast.success('Message envoyé avec succès ! Nous vous recontacterons rapidement.');
        setFormData({
          name: '',
          email: '',
          phone: '',
          country: '',
          visa_type: '',
          budget_range: '',
          urgency_level: 'Normal',
          message: ''
        });
      } else {
        throw new Error('Erreur lors de l\'envoi du message');
      }
    } catch (error) {
      toast.error('Erreur lors de l\'envoi. Veuillez réessayer.');
      console.error('Error submitting contact form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (!companyInfo) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-white">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header Navigation */}
      <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-orange-500">{companyInfo.name}</h1>
                <p className="text-slate-400 text-xs">{companyInfo.tagline}</p>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-6">
              <a href="#services" className="text-slate-300 hover:text-orange-400 transition-colors">Services</a>
              <a href="#about" className="text-slate-300 hover:text-orange-400 transition-colors">À Propos</a>
              <a href="#contact" className="text-slate-300 hover:text-orange-400 transition-colors">Contact</a>
              <Link to="/login" className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors">
                Espace Client
              </Link>
            </nav>

            <div className="md:hidden flex items-center space-x-2">
              <Link to="/login" className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-2 rounded text-sm">
                Connexion
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-slate-800 to-slate-900 py-20">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="bg-orange-500/20 text-orange-400 mb-4">
                🏆 {animatedStats.success_rate}% de Réussite
              </Badge>
              
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Votre <span className="text-orange-500">Immigration</span> en{' '}
                <span className="text-orange-500">Toute Confiance</span>
              </h1>
              
              <p className="text-xl text-slate-300 mb-8 leading-relaxed">
                {companyInfo.description}
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-500 mb-1">{animatedStats.cases}+</div>
                  <div className="text-slate-400 text-sm">Dossiers Traités</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500 mb-1">{animatedStats.success_rate}%</div>
                  <div className="text-slate-400 text-sm">Taux de Réussite</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-500 mb-1">{animatedStats.countries}+</div>
                  <div className="text-slate-400 text-sm">Pays Servis</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-500 mb-1">{animatedStats.satisfaction}/5</div>
                  <div className="text-slate-400 text-sm">Satisfaction</div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <Button className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 text-lg">
                  <MessageCircle className="h-5 w-5 mr-2" />
                  Consultation Gratuite
                </Button>
                <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700 px-8 py-3 text-lg">
                  <Phone className="h-5 w-5 mr-2" />
                  {companyInfo.contact.phone}
                </Button>
              </div>
              
              <div className="flex items-center space-x-6 mt-8 text-sm text-slate-400">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Réponse sous 24h garantie</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-blue-500" />
                  <span>Certification officielle</span>
                </div>
              </div>
            </div>
            
            {/* Contact Form */}
            <Card className="bg-slate-700 border-slate-600 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-white text-center">
                  Évaluation Gratuite de votre Profil
                </CardTitle>
                <CardDescription className="text-slate-400 text-center">
                  Remplissez ce formulaire pour une première évaluation gratuite
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="name" className="text-slate-300">Nom complet *</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        placeholder="Votre nom"
                        required
                        className="bg-slate-600 border-slate-500 text-white"
                      />
                    </div>
                    <div>
                      <Label htmlFor="email" className="text-slate-300">Email *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        placeholder="votre@email.com"
                        required
                        className="bg-slate-600 border-slate-500 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="phone" className="text-slate-300">Téléphone</Label>
                      <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        placeholder="+33 6 12 34 56 78"
                        className="bg-slate-600 border-slate-500 text-white"
                      />
                    </div>
                    <div>
                      <Label htmlFor="country" className="text-slate-300">Pays d'origine *</Label>
                      <Input
                        id="country"
                        value={formData.country}
                        onChange={(e) => setFormData({...formData, country: e.target.value})}
                        placeholder="Votre pays"
                        required
                        className="bg-slate-600 border-slate-500 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="visa_type" className="text-slate-300">Type de projet</Label>
                      <select
                        id="visa_type"
                        value={formData.visa_type}
                        onChange={(e) => setFormData({...formData, visa_type: e.target.value})}
                        className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                      >
                        <option value="">Sélectionner...</option>
                        <option value="Visa Étudiant France">Visa Étudiant France</option>
                        <option value="Permis de Travail Canada">Permis de Travail Canada</option>
                        <option value="Regroupement Familial">Regroupement Familial</option>
                        <option value="Naturalisation française">Naturalisation française</option>
                        <option value="Visa Investisseur">Visa Investisseur</option>
                        <option value="Autre">Autre projet</option>
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="budget_range" className="text-slate-300">Budget estimé</Label>
                      <select
                        id="budget_range"
                        value={formData.budget_range}
                        onChange={(e) => setFormData({...formData, budget_range: e.target.value})}
                        className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                      >
                        <option value="">Sélectionner...</option>
                        <option value="500-1000€">500 - 1 000€</option>
                        <option value="1000-3000€">1 000 - 3 000€</option>
                        <option value="3000-5000€">3 000 - 5 000€</option>
                        <option value="5000+€">Plus de 5 000€</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="urgency_level" className="text-slate-300">Urgence du projet</Label>
                    <select
                      id="urgency_level"
                      value={formData.urgency_level}
                      onChange={(e) => setFormData({...formData, urgency_level: e.target.value})}
                      className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                    >
                      <option value="Information">Information seulement</option>
                      <option value="Normal">Démarche dans les 3-6 mois</option>
                      <option value="Urgent">Urgent (moins de 3 mois)</option>
                    </select>
                  </div>
                  
                  <div>
                    <Label htmlFor="message" className="text-slate-300">Votre message *</Label>
                    <textarea
                      id="message"
                      value={formData.message}
                      onChange={(e) => setFormData({...formData, message: e.target.value})}
                      placeholder="Décrivez votre situation et vos objectifs..."
                      rows={4}
                      required
                      className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md resize-none"
                    />
                  </div>
                  
                  <Button
                    type="submit"
                    disabled={submitting}
                    className="w-full bg-orange-600 hover:bg-orange-700 text-white py-3"
                  >
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Envoi en cours...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Obtenir mon Évaluation Gratuite
                      </>
                    )}
                  </Button>
                  
                  <p className="text-xs text-slate-500 text-center">
                    En soumettant ce formulaire, vous acceptez d'être contacté par nos conseillers.
                  </p>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-slate-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Nos Services d'Excellence
            </h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Une expertise reconnue pour tous vos projets d'immigration
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {companyInfo.services.map((service, index) => (
              <Card key={index} className="bg-slate-700 border-slate-600 hover:border-orange-500/50 transition-colors">
                <CardHeader>
                  <div className="flex justify-between items-start mb-4">
                    <CardTitle className="text-white">{service.name}</CardTitle>
                    <Badge className="bg-green-500/20 text-green-400">
                      {service.success_rate}% réussite
                    </Badge>
                  </div>
                  <CardDescription className="text-slate-300">
                    {service.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">Délai moyen:</span>
                      <span className="text-white">{service.duration}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">À partir de:</span>
                      <span className="text-orange-400 font-bold">{service.price_from}€</span>
                    </div>
                  </div>
                  <Button className="w-full bg-slate-600 hover:bg-orange-600 text-white transition-colors">
                    En savoir plus
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-slate-900">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Pourquoi Choisir {companyInfo.name} ?
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Award className="h-6 w-6 text-orange-500" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Expertise Certifiée</h3>
                    <p className="text-slate-300">
                      Nos consultants sont certifiés et reconnus par les organismes officiels des deux côtés de l'Atlantique.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Target className="h-6 w-6 text-green-500" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Approche Personnalisée</h3>
                    <p className="text-slate-300">
                      Chaque dossier est unique. Nous adaptons notre stratégie à votre situation personnelle.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Heart className="h-6 w-6 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Accompagnement Humain</h3>
                    <p className="text-slate-300">
                      Un suivi personnalisé et bienveillant tout au long de votre parcours d'immigration.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-8">
                <h4 className="text-lg font-semibold text-white mb-4">Nos Certifications:</h4>
                <div className="space-y-2">
                  {companyInfo.certifications.map((cert, index) => (
                    <div key={index} className="flex items-center space-x-2 text-slate-300">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{cert}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              {companyInfo.team.map((member, index) => (
                <Card key={index} className="bg-slate-700 border-slate-600">
                  <CardContent className="p-6 text-center">
                    <div className="w-20 h-20 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Users className="h-10 w-10 text-white" />
                    </div>
                    <h4 className="text-lg font-semibold text-white mb-1">{member.name}</h4>
                    <p className="text-orange-400 text-sm mb-2">{member.role}</p>
                    <p className="text-slate-400 text-xs mb-3">{member.specialization}</p>
                    <Badge className="bg-slate-600 text-slate-300 text-xs">
                      {member.experience}
                    </Badge>
                    <div className="flex justify-center space-x-1 mt-3">
                      {member.languages.map((lang, idx) => (
                        <Badge key={idx} className="bg-blue-500/20 text-blue-400 text-xs">
                          {lang}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-slate-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Contactez-Nous
            </h2>
            <p className="text-xl text-slate-300">
              Plusieurs moyens de nous joindre pour votre projet d'immigration
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8 mb-12">
            {/* Contact Info */}
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Phone className="h-5 w-5 text-orange-500" />
                  <span>Téléphone</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-orange-400 mb-2">{companyInfo.contact.phone}</p>
                <p className="text-slate-400 text-sm">Lun-Ven: 9h-18h | Sam: 10h-14h</p>
                <Button className="w-full mt-4 bg-green-600 hover:bg-green-700">
                  <MessageCircle className="h-4 w-4 mr-2" />
                  WhatsApp: {companyInfo.contact.whatsapp}
                </Button>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Mail className="h-5 w-5 text-orange-500" />
                  <span>Email</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl text-orange-400 mb-2">{companyInfo.contact.email}</p>
                <p className="text-slate-400 text-sm mb-4">Réponse sous 2h en moyenne</p>
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  <Mail className="h-4 w-4 mr-2" />
                  Nous écrire
                </Button>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <MapPin className="h-5 w-5 text-orange-500" />
                  <span>Adresse</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-slate-300">
                  <p>{companyInfo.contact.address}</p>
                  <p>{companyInfo.contact.postal_code} {companyInfo.contact.city}</p>
                  <p className="text-slate-400 text-sm">{companyInfo.contact.metro}</p>
                  <p className="text-slate-400 text-sm">{companyInfo.contact.parking}</p>
                </div>
                <Button className="w-full mt-4 bg-purple-600 hover:bg-purple-700">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Voir sur Google Maps
                </Button>
              </CardContent>
            </Card>
          </div>
          
          {/* Business Hours */}
          <Card className="bg-slate-700 border-slate-600">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Clock className="h-5 w-5 text-orange-500" />
                <span>Horaires d'Ouverture</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(companyInfo.business_hours).map(([day, hours]) => (
                  <div key={day} className="text-center">
                    <p className="text-slate-300 font-medium capitalize mb-1">
                      {day === 'monday' ? 'Lundi' :
                       day === 'tuesday' ? 'Mardi' :
                       day === 'wednesday' ? 'Mercredi' :
                       day === 'thursday' ? 'Jeudi' :
                       day === 'friday' ? 'Vendredi' :
                       day === 'saturday' ? 'Samedi' : 'Dimanche'}
                    </p>
                    <p className={`text-sm ${hours === 'Fermé' ? 'text-red-400' : 'text-orange-400'}`}>
                      {hours}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-700 py-12">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <Globe className="h-5 w-5 text-white" />
                </div>
                <span className="text-orange-500 text-lg font-bold">{companyInfo.name}</span>
              </div>
              <p className="text-slate-400 text-sm mb-4">{companyInfo.tagline}</p>
              <div className="flex space-x-4">
                {Object.entries(companyInfo.social_media).map(([platform, url]) => (
                  <a key={platform} href={url} target="_blank" rel="noopener noreferrer" 
                     className="text-slate-400 hover:text-orange-400 transition-colors">
                    <ExternalLink className="h-5 w-5" />
                  </a>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Services</h4>
              <ul className="space-y-2">
                {companyInfo.services.slice(0, 4).map((service, index) => (
                  <li key={index}>
                    <a href="#" className="text-slate-400 hover:text-orange-400 transition-colors text-sm">
                      {service.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li className="flex items-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>{companyInfo.contact.phone}</span>
                </li>
                <li className="flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>{companyInfo.contact.email}</span>
                </li>
                <li className="flex items-start space-x-2">
                  <MapPin className="h-4 w-4 mt-0.5" />
                  <span>{companyInfo.contact.address}, {companyInfo.contact.city}</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Mentions Légales</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="#" className="hover:text-orange-400 transition-colors">Politique de Confidentialité</a></li>
                <li><a href="#" className="hover:text-orange-400 transition-colors">Conditions d'Utilisation</a></li>
                <li><a href="#" className="hover:text-orange-400 transition-colors">Mentions Légales</a></li>
                <li><a href="#" className="hover:text-orange-400 transition-colors">RGPD</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-700 pt-8 mt-8 text-center">
            <p className="text-slate-400 text-sm">
              © 2024 {companyInfo.name}. Tous droits réservés. 
              Développé avec ❤️ pour faciliter votre immigration.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageV3;