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
  Euro,
  Clock,
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
    urgency_level: 'NORMAL',
    message: '',
    lead_source: 'WEBSITE'
  });

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.email.trim() || !formData.message.trim()) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (formData.message.length < 10) {
      toast.error('Votre message doit contenir au moins 10 caractères');
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
          urgency_level: 'NORMAL',
          message: '',
          lead_source: 'WEBSITE'
        });

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
    <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700/50 shadow-2xl">
      <CardHeader>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div>
            <CardTitle className="text-2xl text-white">Contactez-Nous</CardTitle>
            <CardDescription className="text-slate-400">
              Obtenez une consultation gratuite et personnalisée
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Informations personnelles */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="name" className="text-slate-300 font-medium flex items-center">
                <User className="w-4 h-4 mr-2" />
                Nom Complet *
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Votre nom complet"
                className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
                required
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-slate-300 font-medium flex items-center">
                <Mail className="w-4 h-4 mr-2" />
                Adresse Email *
              </Label>
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

          <div>
            <Label htmlFor="phone" className="text-slate-300 font-medium flex items-center">
              <Phone className="w-4 h-4 mr-2" />
              Téléphone (Optionnel)
            </Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+33 1 23 45 67 89"
              className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 focus:border-orange-500"
            />
          </div>

          {/* Projet d'immigration */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="country" className="text-slate-300 font-medium flex items-center">
                <Globe className="w-4 h-4 mr-2" />
                Pays de Destination
              </Label>
              <Select
                value={formData.country}
                onValueChange={(value) => setFormData({ ...formData, country: value, visa_type: '' })}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                  <SelectValue placeholder="Sélectionnez un pays" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {countries.map((country) => (
                    <SelectItem 
                      key={country.value} 
                      value={country.value} 
                      className="text-white hover:bg-slate-700"
                    >
                      {country.flag} {country.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="visa_type" className="text-slate-300 font-medium flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Type de Visa
              </Label>
              <Select
                value={formData.visa_type}
                onValueChange={(value) => setFormData({ ...formData, visa_type: value })}
                disabled={!formData.country || formData.country === 'Autre'}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                  <SelectValue placeholder="Type de visa souhaité" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {formData.country && visaTypes[formData.country] ? (
                    visaTypes[formData.country].map((type) => (
                      <SelectItem 
                        key={type} 
                        value={type} 
                        className="text-white hover:bg-slate-700"
                      >
                        {type}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="Autre" className="text-white hover:bg-slate-700">
                      Autre / Non défini
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Budget et urgence */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="budget_range" className="text-slate-300 font-medium flex items-center">
                <Euro className="w-4 h-4 mr-2" />
                Budget Envisagé
              </Label>
              <Select
                value={formData.budget_range}
                onValueChange={(value) => setFormData({ ...formData, budget_range: value })}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                  <SelectValue placeholder="Fourchette budgétaire" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {budgetRanges.map((budget) => (
                    <SelectItem 
                      key={budget.value} 
                      value={budget.value} 
                      className="text-white hover:bg-slate-700"
                    >
                      {budget.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="urgency_level" className="text-slate-300 font-medium flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                Délai Souhaité
              </Label>
              <Select
                value={formData.urgency_level}
                onValueChange={(value) => setFormData({ ...formData, urgency_level: value })}
              >
                <SelectTrigger className="mt-2 bg-[#0F172A] border-slate-600 text-white focus:border-orange-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  {urgencyLevels.map((level) => (
                    <SelectItem 
                      key={level.value} 
                      value={level.value} 
                      className="text-white hover:bg-slate-700"
                    >
                      {level.icon} {level.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

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

          {/* Submit Button */}
          <Button
            type="submit"
            size="lg"
            className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300 py-6 text-lg"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                Envoi en cours...
              </span>
            ) : (
              <>
                <Send className="mr-2 w-5 h-5" />
                Envoyer Ma Demande
              </>
            )}
          </Button>

          {/* Privacy Notice */}
          <p className="text-center text-sm text-slate-400 mt-4">
            🔒 Vos informations sont sécurisées et confidentielles.<br />
            <strong>Réponse garantie sous 24h</strong> par nos experts.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}