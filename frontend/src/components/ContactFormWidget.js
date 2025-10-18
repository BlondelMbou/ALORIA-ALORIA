import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { 
  Send, 
  User, 
  Mail, 
  Phone, 
  Globe, 
  MessageCircle, 
  Target,
  CheckCircle
} from 'lucide-react';

export default function ContactFormWidget() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    country: '',
    visa_type: '',
    budget_range: '',
    urgency_level: 'Normal',
    message: '',
    lead_source: 'Site web',
    how_did_you_know: '',
    referred_by_employee: ''
  });
  const [showEmployeeField, setShowEmployeeField] = useState(false);

  const countries = [
    { value: 'Canada', label: 'Canada', flag: '🇨🇦' },
    { value: 'France', label: 'France', flag: '🇫🇷' },
    { value: 'Allemagne', label: 'Allemagne', flag: '🇩🇪' },
    { value: 'Suisse', label: 'Suisse', flag: '🇨🇭' },
    { value: 'Belgique', label: 'Belgique', flag: '🇧🇪' },
    { value: 'Autre', label: 'Autre destination', flag: '🌍' }
  ];

  const visaTypes = {
    Canada: [
      'Permis de Travail',
      'Permis d\'Études',
      'Résidence Permanente (Entrée Express)',
      'Visa de Visiteur',
      'Parrainage Familial'
    ],
    France: [
      'Permis de Travail (Passeport Talent)',
      'Visa Étudiant',
      'Regroupement Familial',
      'Carte de Résident',
      'Visa Touristique'
    ],
    Allemagne: [
      'Carte Bleue Européenne',
      'Visa de Travail',
      'Visa Étudiant',
      'Regroupement Familial'
    ],
    Suisse: [
      'Permis de Travail (B)',
      'Permis de Séjour (C)',
      'Visa Étudiant',
      'Regroupement Familial'
    ],
    Belgique: [
      'Permis de Travail',
      'Visa Étudiant',
      'Regroupement Familial',
      'Carte Bleue Européenne'
    ]
  };

  const budgetRanges = [
    { value: '1000-3000€', label: '1 000 - 3 000 €' },
    { value: '3000-5000€', label: '3 000 - 5 000 €' },
    { value: '5000+€', label: '5 000 € et plus' },
    { value: 'À discuter', label: 'À discuter' }
  ];

  const urgencyLevels = [
    { value: 'Urgent', label: 'Urgent (< 3 mois)', icon: '🚀' },
    { value: 'Normal', label: 'Normal (3-6 mois)', icon: '📅' },
    { value: 'Information', label: 'Information générale', icon: '⏰' }
  ];

  const knowledgeSources = [
    { value: 'Recherche Google', label: 'Recherche Google', icon: '🔍' },
    { value: 'Réseaux sociaux', label: 'Réseaux sociaux (Facebook, Instagram, LinkedIn)', icon: '📱' },
    { value: 'Recommandation famille/amis', label: 'Recommandation de famille ou amis', icon: '👥' },
    { value: 'Par une personne', label: 'Par un employé d\'ALORIA AGENCY', icon: '👤' },
    { value: 'Publicité en ligne', label: 'Publicité en ligne', icon: '📺' },
    { value: 'Article de presse', label: 'Article de presse/blog', icon: '📰' },
    { value: 'Événement/salon', label: 'Événement ou salon', icon: '🏢' },
    { value: 'Autre', label: 'Autre', icon: '💭' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.email.trim() || !formData.message.trim() || !formData.how_did_you_know.trim()) {
      toast.error('Veuillez remplir tous les champs obligatoires (nom, email, message et comment vous nous avez connus)');
      return;
    }

    if (formData.message.length < 10) {
      toast.error('Votre message doit contenir au moins 10 caractères');
      return;
    }

    if (formData.how_did_you_know === 'Par une personne' && !formData.referred_by_employee.trim()) {
      toast.error('Veuillez préciser le nom de l\'employé qui vous a recommandé');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact-messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const result = await response.json();
        
        toast.success('🎉 Votre message a été envoyé avec succès ! Notre équipe vous contactera sous 24h.');
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          phone: '',
          country: '',
          visa_type: '',
          budget_range: '',
          urgency_level: 'Normal',
          message: '',
          lead_source: 'Site web',
          how_did_you_know: '',
          referred_by_employee: ''
        });
        setShowEmployeeField(false);

      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de l\'envoi');
      }

    } catch (error) {
      console.error('Contact form error:', error);
      toast.error('Erreur lors de l\'envoi. Veuillez réessayer ou nous contacter par téléphone.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 shadow-2xl mx-auto max-w-4xl">
      <CardHeader className="p-4 sm:p-6 lg:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto sm:mx-0">
            <MessageCircle className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          </div>
          <div className="text-center sm:text-left">
            <CardTitle className="text-xl sm:text-2xl text-white">Contactez-Nous</CardTitle>
            <CardDescription className="text-slate-400 text-sm sm:text-base">
              Obtenez une consultation gratuite et personnalisée
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-4 sm:p-6 lg:p-8">
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
          {/* Informations personnelles - Mobile responsive */}
          <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
            <div>
              <Label htmlFor="name" className="text-slate-300 font-medium flex items-center text-sm sm:text-base">
                <User className="w-4 h-4 mr-2 flex-shrink-0" />
                Nom Complet *
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Votre nom complet"
                className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500 text-sm sm:text-base h-11 sm:h-12"
                required
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-slate-300 font-medium flex items-center text-sm sm:text-base">
                <Mail className="w-4 h-4 mr-2 flex-shrink-0" />
                Adresse Email *
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="votre.email@exemple.com"
                className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500 text-sm sm:text-base h-11 sm:h-12"
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="phone" className="text-slate-300 font-medium flex items-center text-sm sm:text-base">
              <Phone className="w-4 h-4 mr-2 flex-shrink-0" />
              Téléphone (Optionnel)
            </Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+33 1 23 45 67 89"
              className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500 text-sm sm:text-base h-11 sm:h-12"
            />
          </div>

          {/* Projet d'immigration - Mobile responsive */}
          <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
            <div>
              <Label htmlFor="country" className="text-slate-300 font-medium flex items-center text-sm sm:text-base">
                <Globe className="w-4 h-4 mr-2 flex-shrink-0" />
                Pays de Destination
              </Label>
              <Select
                value={formData.country}
                onValueChange={(value) => setFormData({ ...formData, country: value, visa_type: '' })}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500 h-11 sm:h-12 text-sm sm:text-base">
                  <SelectValue placeholder="Sélectionnez un pays" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {countries.map((country) => (
                    <SelectItem 
                      key={country.value} 
                      value={country.value} 
                      className="text-white hover:bg-slate-700 text-sm sm:text-base"
                    >
                      {country.flag} {country.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="visa_type" className="text-slate-300 font-medium flex items-center text-sm sm:text-base">
                <Target className="w-4 h-4 mr-2 flex-shrink-0" />
                Type de Visa
              </Label>
              <Select
                value={formData.visa_type}
                onValueChange={(value) => setFormData({ ...formData, visa_type: value })}
                disabled={!formData.country || formData.country === 'Autre'}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500 h-11 sm:h-12 text-sm sm:text-base disabled:opacity-50">
                  <SelectValue placeholder="Type de visa souhaité" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {formData.country && visaTypes[formData.country] ? (
                    visaTypes[formData.country].map((type) => (
                      <SelectItem 
                        key={type} 
                        value={type} 
                        className="text-white hover:bg-slate-700 text-sm sm:text-base"
                      >
                        {type}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="Autre" className="text-white hover:bg-slate-700 text-sm sm:text-base">
                      Autre / Non défini
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Budget et Délai retirés selon les nouvelles exigences */}

          {/* Comment avez-vous connu ALORIA AGENCY */}
          <div>
            <Label htmlFor="how_did_you_know" className="text-slate-300 font-medium flex items-center">
              <MessageCircle className="w-4 h-4 mr-2" />
              Comment avez-vous connu ALORIA AGENCY ? *
            </Label>
            <Select
              value={formData.how_did_you_know}
              onValueChange={(value) => {
                setFormData({ ...formData, how_did_you_know: value, referred_by_employee: '' });
                setShowEmployeeField(value === 'Par une personne');
              }}
            >
              <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                <SelectValue placeholder="Sélectionnez comment vous nous avez connus" />
              </SelectTrigger>
              <SelectContent className="bg-[#1E293B] border-slate-600">
                {knowledgeSources.map((source) => (
                  <SelectItem 
                    key={source.value} 
                    value={source.value} 
                    className="text-white hover:bg-slate-700"
                  >
                    {source.icon} {source.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Champ employé si "Par une personne" est sélectionné */}
          {showEmployeeField && (
            <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <Label htmlFor="referred_by_employee" className="text-orange-300 font-medium flex items-center">
                <User className="w-4 h-4 mr-2" />
                Nom de l'employé qui vous a recommandé
              </Label>
              <Input
                id="referred_by_employee"
                value={formData.referred_by_employee}
                onChange={(e) => setFormData({ ...formData, referred_by_employee: e.target.value })}
                placeholder="Prénom et nom de l'employé"
                className="mt-2 bg-[#0F172A] border-orange-500/50 text-white placeholder:text-slate-500 focus:border-orange-500"
              />
              <p className="text-xs text-orange-300 mt-2">
                ℹ️ Cette information nous permettra d'attribuer votre dossier directement à cette personne
              </p>
            </div>
          )}

          {/* Message */}
          <div>
            <Label htmlFor="message" className="text-slate-300 font-medium flex items-center">
              <MessageCircle className="w-4 h-4 mr-2" />
              Votre Message *
            </Label>
            <Textarea
              id="message"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              placeholder="Parlez-nous de votre projet d'immigration, vos objectifs, votre situation actuelle, vos préoccupations..."
              rows={5}
              className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
              required
            />
            <p className="text-xs text-slate-400 mt-2">
              Minimum 10 caractères • {formData.message.length}/1000
            </p>
          </div>

          {/* Lead Score Indicator (optional visual feedback) */}
          {(formData.budget_range || formData.urgency_level !== 'NORMAL' || formData.country) && (
            <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-5 h-5 text-orange-400" />
                <span className="text-orange-400 font-medium">Profil Premium Détecté</span>
              </div>
              <p className="text-sm text-orange-300">
                Votre profil sera traité en priorité par nos experts senior
              </p>
            </div>
          )}

          {/* Submit Button - Mobile optimized */}
          <Button
            type="submit"
            size="lg"
            className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300 py-4 sm:py-6 text-base sm:text-lg font-semibold touch-manipulation"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white mr-2 sm:mr-3"></div>
                <span className="text-sm sm:text-base">Envoi en cours...</span>
              </span>
            ) : (
              <>
                <Send className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                <span className="hidden xs:inline">Envoyer Ma Demande</span>
                <span className="xs:hidden">Envoyer</span>
              </>
            )}
          </Button>

          {/* Privacy Notice - Mobile responsive */}
          <div className="text-center text-xs sm:text-sm text-slate-400 mt-4 space-y-1">
            <p className="flex items-center justify-center">
              <span className="text-green-400 mr-1">🔒</span>
              Informations sécurisées et confidentielles
            </p>
            <p className="font-semibold text-orange-400">
              Réponse garantie sous 24h par nos experts
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}