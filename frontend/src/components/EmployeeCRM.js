import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { toast } from 'sonner';
import api from '../utils/api';
import { MessageCircle, Star, Phone, Mail, Calendar, User, Filter, Search, Plus, Eye, UserCheck, Clock, CheckCircle } from 'lucide-react';

export default function EmployeeCRM() {
  const [contactMessages, setContactMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [showResponseForm, setShowResponseForm] = useState(false);
  const [responseForm, setResponseForm] = useState({
    subject: '',
    message: '',
    followUp: false,
    followUpDate: ''
  });
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showConvertDialog, setShowConvertDialog] = useState(false);
  const [convertForm, setConvertForm] = useState({
    full_name: '',
    phone: '',
    country: 'Canada',
    visa_type: '',
    message: ''
  });

  const visaTypes = {
    Canada: ['Work Permit', 'Study Permit', 'Permanent Residence (Express Entry)'],
    France: ['Work Permit (Talent Permit)', 'Student Visa', 'Family Reunification']
  };

  useEffect(() => {
    fetchContactMessages();
  }, []);

  const fetchContactMessages = async () => {
    setLoading(true);
    try {
      const response = await api.get('/contact-messages');
      setContactMessages(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des messages');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    try {
      await api.patch(`/contact-messages/${messageId}/status`, { status: 'read' });
      toast.success('Message marqué comme lu');
      fetchContactMessages();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleSendResponse = async (messageId) => {
    try {
      await api.post(`/contact-messages/${messageId}/respond`, responseForm);
      toast.success('Réponse envoyée avec succès');
      setShowResponseForm(false);
      setResponseForm({
        subject: '',
        message: '',
        followUp: false,
        followUpDate: ''
      });
      fetchContactMessages();
    } catch (error) {
      toast.error('Erreur lors de l\'envoi de la réponse');
    }
  };

  const handleConvertToClient = async () => {
    try {
      const clientData = {
        ...convertForm,
        email: selectedMessage.email
      };
      
      await api.post('/clients', clientData);
      
      // Marquer le message comme converti
      await api.patch(`/contact-messages/${selectedMessage.id}/status`, { status: 'converted' });
      
      toast.success('Contact converti en client avec succès');
      setShowConvertDialog(false);
      setConvertForm({
        full_name: '',
        phone: '',
        country: 'Canada',
        visa_type: '',
        message: ''
      });
      fetchContactMessages();
    } catch (error) {
      toast.error('Erreur lors de la conversion en client');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-blue-500/10 text-blue-400 border border-blue-500/30';
      case 'read': return 'bg-orange-500/10 text-orange-400 border border-orange-500/30';
      case 'responded': return 'bg-green-500/10 text-green-400 border border-green-500/30';
      case 'converted': return 'bg-purple-500/10 text-purple-400 border border-purple-500/30';
      default: return 'bg-slate-500/10 text-slate-400 border border-slate-500/30';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'new': return 'Nouveau';
      case 'read': return 'Lu';
      case 'responded': return 'Répondu';
      case 'converted': return 'Converti';
      default: return 'Inconnu';
    }
  };

  const getLeadScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const filteredMessages = contactMessages.filter(msg => {
    const matchesStatus = filterStatus === 'all' || msg.status === filterStatus;
    const matchesSearch = msg.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         msg.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         msg.message.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">CRM - Gestion des Contacts</h2>
          <p className="text-slate-400">Gérez les messages de contact et convertissez-les en clients</p>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="bg-[#1E293B] border-slate-600">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                <Input
                  placeholder="Rechercher par nom, email ou message..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-400"
                />
              </div>
            </div>
            <div className="md:w-48">
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                  <SelectValue placeholder="Filtrer par statut" />
                </SelectTrigger>
                <SelectContent className="bg-[#1E293B] border-slate-600">
                  <SelectItem value="all" className="text-white hover:bg-slate-700">Tous</SelectItem>
                  <SelectItem value="new" className="text-white hover:bg-slate-700">Nouveaux</SelectItem>
                  <SelectItem value="read" className="text-white hover:bg-slate-700">Lus</SelectItem>
                  <SelectItem value="responded" className="text-white hover:bg-slate-700">Répondus</SelectItem>
                  <SelectItem value="converted" className="text-white hover:bg-slate-700">Convertis</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Messages List */}
      <div className="grid gap-4">
        {filteredMessages.length === 0 ? (
          <Card className="bg-[#1E293B] border-slate-600">
            <CardContent className="p-8 text-center">
              <MessageCircle className="mx-auto h-12 w-12 text-slate-400 mb-4" />
              <p className="text-slate-400">Aucun message de contact trouvé</p>
            </CardContent>
          </Card>
        ) : (
          filteredMessages.map((message) => (
            <Card key={message.id} className="bg-[#1E293B] border-slate-600 hover:border-orange-500/50 transition-colors">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{message.name}</h3>
                      <Badge className={getStatusColor(message.status)}>
                        {getStatusLabel(message.status)}
                      </Badge>
                      {message.lead_score && (
                        <div className="flex items-center gap-1">
                          <Star className={`w-4 h-4 ${getLeadScoreColor(message.lead_score)}`} />
                          <span className={`text-sm font-medium ${getLeadScoreColor(message.lead_score)}`}>
                            {message.lead_score}/100
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-slate-400 mb-3">
                      <div className="flex items-center gap-1">
                        <Mail className="w-4 h-4" />
                        {message.email}
                      </div>
                      {message.phone && (
                        <div className="flex items-center gap-1">
                          <Phone className="w-4 h-4" />
                          {message.phone}
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(message.created_at).toLocaleDateString('fr-FR')}
                      </div>
                    </div>

                    {message.country && (
                      <div className="mb-3">
                        <Badge className="bg-slate-700/50 text-slate-300 border border-slate-600">
                          {message.country}
                        </Badge>
                        {message.visa_type && (
                          <Badge className="ml-2 bg-slate-700/50 text-slate-300 border border-slate-600">
                            {message.visa_type}
                          </Badge>
                        )}
                      </div>
                    )}
                    
                    <p className="text-slate-300 mb-4">{message.message}</p>
                  </div>
                </div>

                <div className="flex gap-2 flex-wrap">
                  {message.status === 'new' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleMarkAsRead(message.id)}
                      className="border-slate-600 text-slate-300 hover:bg-slate-700"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Marquer comme lu
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedMessage(message);
                      setShowResponseForm(true);
                      setResponseForm({
                        subject: `Re: ${message.subject || 'Votre demande d\'information'}`,
                        message: '',
                        followUp: false,
                        followUpDate: ''
                      });
                    }}
                    className="border-slate-600 text-slate-300 hover:bg-slate-700"
                  >
                    <MessageCircle className="w-4 h-4 mr-2" />
                    Répondre
                  </Button>
                  
                  {message.status !== 'converted' && (
                    <Button
                      size="sm"
                      onClick={() => {
                        setSelectedMessage(message);
                        setConvertForm({
                          full_name: message.name,
                          phone: message.phone || '',
                          country: message.country || 'Canada',
                          visa_type: message.visa_type || '',
                          message: `Client converti depuis le contact CRM. Message original: ${message.message}`
                        });
                        setShowConvertDialog(true);
                      }}
                      className="bg-orange-500 hover:bg-orange-600 text-white"
                    >
                      <UserCheck className="w-4 h-4 mr-2" />
                      Convertir en client
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Response Dialog */}
      <Dialog open={showResponseForm} onOpenChange={setShowResponseForm}>
        <DialogContent className="bg-[#1E293B] border-slate-600 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle>Répondre au message</DialogTitle>
            <DialogDescription className="text-slate-400">
              Envoyez une réponse à {selectedMessage?.name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="subject" className="text-slate-300">Sujet</Label>
              <Input
                id="subject"
                value={responseForm.subject}
                onChange={(e) => setResponseForm({...responseForm, subject: e.target.value})}
                className="bg-[#0F172A] border-slate-600 text-white"
                placeholder="Sujet de la réponse"
              />
            </div>
            
            <div>
              <Label htmlFor="message" className="text-slate-300">Message</Label>
              <Textarea
                id="message"
                value={responseForm.message}
                onChange={(e) => setResponseForm({...responseForm, message: e.target.value})}
                className="bg-[#0F172A] border-slate-600 text-white"
                rows={6}
                placeholder="Votre réponse..."
              />
            </div>
            
            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => setShowResponseForm(false)}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                Annuler
              </Button>
              <Button
                onClick={() => handleSendResponse(selectedMessage?.id)}
                disabled={!responseForm.message.trim()}
                className="bg-orange-500 hover:bg-orange-600 text-white"
              >
                Envoyer la réponse
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Convert to Client Dialog */}
      <Dialog open={showConvertDialog} onOpenChange={setShowConvertDialog}>
        <DialogContent className="bg-[#1E293B] border-slate-600 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle>Convertir en client</DialogTitle>
            <DialogDescription className="text-slate-400">
              Créer un compte client pour {selectedMessage?.name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="full_name" className="text-slate-300">Nom complet</Label>
                <Input
                  id="full_name"
                  value={convertForm.full_name}
                  onChange={(e) => setConvertForm({...convertForm, full_name: e.target.value})}
                  className="bg-[#0F172A] border-slate-600 text-white"
                />
              </div>
              <div>
                <Label htmlFor="phone" className="text-slate-300">Téléphone</Label>
                <Input
                  id="phone"
                  value={convertForm.phone}
                  onChange={(e) => setConvertForm({...convertForm, phone: e.target.value})}
                  className="bg-[#0F172A] border-slate-600 text-white"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="country" className="text-slate-300">Pays de destination</Label>
                <Select
                  value={convertForm.country}
                  onValueChange={(value) => setConvertForm({...convertForm, country: value, visa_type: ''})}
                >
                  <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1E293B] border-slate-600">
                    <SelectItem value="Canada" className="text-white hover:bg-slate-700">Canada</SelectItem>
                    <SelectItem value="France" className="text-white hover:bg-slate-700">France</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="visa_type" className="text-slate-300">Type de visa</Label>
                <Select
                  value={convertForm.visa_type}
                  onValueChange={(value) => setConvertForm({...convertForm, visa_type: value})}
                >
                  <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                    <SelectValue placeholder="Sélectionner un type" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1E293B] border-slate-600">
                    {visaTypes[convertForm.country]?.map((type) => (
                      <SelectItem key={type} value={type} className="text-white hover:bg-slate-700">
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="client_message" className="text-slate-300">Notes (optionnel)</Label>
              <Textarea
                id="client_message"
                value={convertForm.message}
                onChange={(e) => setConvertForm({...convertForm, message: e.target.value})}
                className="bg-[#0F172A] border-slate-600 text-white"
                rows={3}
                placeholder="Notes sur le client..."
              />
            </div>
            
            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => setShowConvertDialog(false)}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                Annuler
              </Button>
              <Button
                onClick={handleConvertToClient}
                disabled={!convertForm.full_name.trim() || !convertForm.country || !convertForm.visa_type}
                className="bg-orange-500 hover:bg-orange-600 text-white"
              >
                <UserCheck className="w-4 h-4 mr-2" />
                Créer le client
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}