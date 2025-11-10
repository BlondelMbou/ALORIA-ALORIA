import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { LogOut, Users, Calendar, CheckCircle, Clock, Phone, Mail, MapPin, FileText, Send } from 'lucide-react';
import AloriaLogo from '../components/AloriaLogo';
import NotificationBell from '../components/NotificationBell';
import SearchAndSort from '../components/SearchAndSort';
import api from '../utils/api';

export default function ConsultantDashboard() {
  const { user, logout } = useContext(AuthContext);
  const [prospects, setProspects] = useState([]);
  const [filteredProspects, setFilteredProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [consultantNotes, setConsultantNotes] = useState('');

  useEffect(() => {
    fetchProspects();
    // Auto-refresh toutes les 2 minutes
    const interval = setInterval(fetchProspects, 120000);
    return () => clearInterval(interval);
  }, []);

  const fetchProspects = async () => {
    try {
      // Récupérer tous les prospects avec statut paiement_50k (affectés au consultant)
      const response = await api.get('/api/contact-messages');
      const allProspects = response.data;
      
      // Filtrer seulement ceux affectés au consultant (statut paiement_50k)
      const consultantProspects = allProspects.filter(p => p.status === 'paiement_50k');
      
      setProspects(consultantProspects);
      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement prospects:', error);
      toast.error('Erreur lors du chargement des prospects');
      setLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!consultantNotes.trim()) {
      toast.error('Veuillez saisir une note');
      return;
    }

    try {
      await api.patch(`/contact-messages/${selectedProspect.id}/consultant-notes`, {
        note: consultantNotes
      });
      
      toast.success('Note ajoutée avec succès');
      setConsultantNotes('');
      setSelectedProspect(null);
      fetchProspects();
    } catch (error) {
      console.error('Erreur ajout note:', error);
      toast.error('Erreur lors de l\'ajout de la note');
    }
  };

  const handleConvertToClient = async (prospectId) => {
    if (!window.confirm('Convertir ce prospect en client ? Cette action est irréversible.')) {
      return;
    }

    try {
      await api.post(`/contact-messages/${prospectId}/convert-to-client`);
      toast.success('Prospect converti en client avec succès !');
      fetchProspects();
    } catch (error) {
      console.error('Erreur conversion:', error);
      toast.error('Erreur lors de la conversion');
    }
  };

  const getLeadScoreColor = (score) => {
    if (score >= 80) return 'bg-green-500/20 text-green-400 border-green-500/30';
    if (score >= 60) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <Card className="bg-gradient-to-r from-[#0F172A] to-[#1E293B] border-none shadow-2xl rounded-none">
        <CardContent className="p-4 md:p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <AloriaLogo className="h-10" />
              <div>
                <h1 className="text-xl md:text-2xl font-bold text-white">
                  Consultant Dashboard
                </h1>
                <p className="text-sm text-slate-400 mt-1">Bienvenue, {user?.full_name}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <NotificationBell />
              <Button 
                onClick={logout}
                className="bg-slate-700 hover:bg-slate-600 text-white"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-blue-500 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Total Prospects</p>
                  <p className="text-3xl font-bold text-white">{prospects.length}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center border border-blue-500/20">
                  <Users className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-green-500 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Consultations Payées</p>
                  <p className="text-3xl font-bold text-white">{prospects.length}</p>
                  <p className="text-xs text-green-400 mt-1">{prospects.length * 50000} CFA</p>
                </div>
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center border border-green-500/20">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-orange-500 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">En Attente</p>
                  <p className="text-3xl font-bold text-white">{prospects.filter(p => !p.consultant_notes || p.consultant_notes.length === 0).length}</p>
                </div>
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center border border-orange-500/20">
                  <Clock className="w-6 h-6 text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
          <CardHeader>
            <CardTitle className="text-white text-2xl">Mes Prospects Assignés</CardTitle>
            <CardDescription className="text-slate-400">
              Prospects ayant payé la consultation de 50,000 CFA
            </CardDescription>
          </CardHeader>
          <CardContent>
            {prospects.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg">Aucun prospect assigné</p>
                <p className="text-slate-500 text-sm mt-2">Les prospects payants apparaîtront ici</p>
              </div>
            ) : (
              <>
                {/* Recherche et Tri */}
                <SearchAndSort
                  data={prospects}
                  searchFields={['name', 'email', 'country', 'destination', 'assigned_to_name']}
                  sortOptions={[
                    { value: 'created_at', label: 'Date de création' },
                    { value: 'name', label: 'Nom' },
                    { value: 'lead_score', label: 'Score' },
                    { value: 'country', label: 'Pays' }
                  ]}
                  onFilteredDataChange={setFilteredProspects}
                  placeholder="Rechercher un prospect (nom, email, pays, destination)..."
                />

                {/* Liste des prospects */}
                <div className="grid gap-6">
                  {filteredProspects.map((prospect) => (
                    <Card key={prospect.id} className="bg-gradient-to-br from-[#0F172A] to-[#1E293B] border-2 border-slate-700 hover:border-orange-500/50 transition-all">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-white">{prospect.name}</h3>
                              <Badge className={getLeadScoreColor(prospect.lead_score)}>
                                Score: {prospect.lead_score}/100
                              </Badge>
                              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                💰 50,000 CFA Payé
                              </Badge>
                            </div>
                            
                            <div className="grid md:grid-cols-2 gap-3 text-sm mt-3">
                              <div className="flex items-center text-slate-300">
                                <Mail className="w-4 h-4 mr-2 text-blue-400" />
                                {prospect.email}
                              </div>
                              <div className="flex items-center text-slate-300">
                                <Phone className="w-4 h-4 mr-2 text-green-400" />
                                {prospect.phone_number || 'N/A'}
                              </div>
                              <div className="flex items-center text-slate-300">
                                <MapPin className="w-4 h-4 mr-2 text-orange-400" />
                                {prospect.country} → {prospect.destination}
                              </div>
                              <div className="flex items-center text-slate-300">
                                <Calendar className="w-4 h-4 mr-2 text-purple-400" />
                                Créé le: {new Date(prospect.created_at).toLocaleDateString('fr-FR')}
                              </div>
                            </div>

                            {/* Message du prospect */}
                            {prospect.message && (
                              <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                                <p className="text-xs text-slate-400 mb-1 font-semibold">Message:</p>
                                <p className="text-sm text-slate-300">{prospect.message}</p>
                              </div>
                            )}

                            {/* Notes consultant existantes */}
                            {prospect.consultant_notes && prospect.consultant_notes.length > 0 && (
                              <div className="mt-4 space-y-2">
                                <p className="text-xs text-slate-400 font-semibold">📝 Notes Consultant:</p>
                                {prospect.consultant_notes.map((note, idx) => (
                                  <div key={idx} className="p-3 bg-blue-500/10 rounded-lg border border-blue-500/30">
                                    <p className="text-sm text-slate-300">{note.note}</p>
                                    <p className="text-xs text-slate-500 mt-1">
                                      {note.added_by} - {new Date(note.created_at).toLocaleString('fr-FR')}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Assigné par */}
                            <div className="mt-3 text-xs text-slate-500">
                              Assigné par: {prospect.assigned_to_name || 'N/A'}
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 mt-4">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                onClick={() => setSelectedProspect(prospect)}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                              >
                                <FileText className="w-4 h-4 mr-2" />
                                Ajouter une Note
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="bg-[#1E293B] border-slate-700">
                              <DialogHeader>
                                <DialogTitle className="text-white">Ajouter une Note Consultant</DialogTitle>
                                <DialogDescription className="text-slate-400">
                                  Note pour {prospect.name}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4">
                                <Textarea
                                  value={consultantNotes}
                                  onChange={(e) => setConsultantNotes(e.target.value)}
                                  placeholder="Saisissez vos observations, recommandations, plan d'action..."
                                  rows={6}
                                  className="bg-slate-800 border-slate-600 text-white"
                                />
                                <Button 
                                  onClick={handleAddNote}
                                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                  <Send className="w-4 h-4 mr-2" />
                                  Enregistrer la Note
                                </Button>
                              </div>
                            </DialogContent>
                          </Dialog>

                          <Button 
                            onClick={() => handleConvertToClient(prospect.id)}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Convertir en Client
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
