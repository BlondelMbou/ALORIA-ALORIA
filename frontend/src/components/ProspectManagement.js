import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from './ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import api from '../utils/api';
import { 
  Users, 
  UserPlus, 
  DollarSign, 
  MessageCircle, 
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  ArrowRight,
  Mail,
  Phone,
  Globe,
  FileText
} from 'lucide-react';

/**
 * Composant de gestion des prospects pour SuperAdmin
 * Permet de voir, assigner et gérer tous les prospects
 */
export default function ProspectManagement({ userRole }) {
  const [prospects, setProspects] = useState([]);
  const [filteredProspects, setFilteredProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [employees, setEmployees] = useState([]);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [assigneeId, setAssigneeId] = useState('');
  const [consultantNotes, setConsultantNotes] = useState('');

  // Statuts traduits
  const statusLabels = {
    'nouveau': { label: 'Nouveau', color: 'bg-blue-500', icon: '🆕' },
    'assigne_employe': { label: 'Assigné Employé', color: 'bg-purple-500', icon: '👤' },
    'paiement_50k': { label: 'Payé 50k CFA', color: 'bg-green-500', icon: '💰' },
    'en_consultation': { label: 'En Consultation', color: 'bg-orange-500', icon: '💬' },
    'converti_client': { label: 'Converti Client', color: 'bg-emerald-500', icon: '✅' },
    'archive': { label: 'Archivé', color: 'bg-gray-500', icon: '📦' }
  };

  useEffect(() => {
    fetchProspects();
    if (userRole === 'SUPERADMIN') {
      fetchEmployees();
    }
  }, [userRole]);

  useEffect(() => {
    filterProspects();
  }, [prospects, searchTerm, statusFilter]);

  const fetchProspects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/contact-messages');
      setProspects(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des prospects:', error);
      toast.error('Impossible de charger les prospects');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/admin/users');
      // Filtrer seulement les employés et managers actifs
      const activeEmployees = response.data.filter(
        user => user.is_active && ['MANAGER', 'EMPLOYEE'].includes(user.role)
      );
      setEmployees(activeEmployees);
    } catch (error) {
      console.error('Erreur lors du chargement des employés:', error);
      toast.error('Erreur lors du chargement de la liste des employés');
    }
  };

  const filterProspects = () => {
    let filtered = [...prospects];

    // Filtrer par terme de recherche
    if (searchTerm) {
      filtered = filtered.filter(p =>
        p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.country?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrer par statut
    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => p.status === statusFilter);
    }

    // Trier par date de création (plus récent en premier)
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    setFilteredProspects(filtered);
  };

  const handleAssignProspect = async () => {
    if (!selectedProspect || !assigneeId) {
      toast.error('Veuillez sélectionner un employé');
      return;
    }

    try {
      await api.patch(`/contact-messages/${selectedProspect.id}/assign`, {
        assigned_to: assigneeId
      });
      toast.success('Prospect assigné avec succès !');
      setSelectedProspect(null);
      setAssigneeId('');
      fetchProspects();
    } catch (error) {
      console.error('Erreur lors de l\'assignation:', error);
      toast.error('Erreur lors de l\'assignation du prospect');
    }
  };

  const handleAddConsultantNote = async () => {
    if (!selectedProspect || !consultantNotes.trim()) {
      toast.error('Veuillez saisir une note');
      return;
    }

    try {
      await api.patch(`/contact-messages/${selectedProspect.id}/consultant-notes`, {
        note: consultantNotes
      });
      toast.success('Note ajoutée avec succès !');
      setConsultantNotes('');
      setSelectedProspect(null);
      fetchProspects();
    } catch (error) {
      console.error('Erreur lors de l\'ajout de la note:', error);
      toast.error('Erreur lors de l\'ajout de la note');
    }
  };

  const getProspectsByStatus = (status) => {
    return prospects.filter(p => p.status === status);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header avec statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border-blue-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Nouveaux</p>
                <p className="text-2xl font-bold text-white">{getProspectsByStatus('nouveau').length}</p>
              </div>
              <div className="text-3xl">🆕</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border-purple-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Assignés</p>
                <p className="text-2xl font-bold text-white">{getProspectsByStatus('assigne_employe').length}</p>
              </div>
              <div className="text-3xl">👤</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Payés 50k</p>
                <p className="text-2xl font-bold text-white">{getProspectsByStatus('paiement_50k').length}</p>
              </div>
              <div className="text-3xl">💰</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 border-emerald-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Convertis</p>
                <p className="text-2xl font-bold text-white">{getProspectsByStatus('converti_client').length}</p>
              </div>
              <div className="text-3xl">✅</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtres et recherche */}
      <Card className="bg-[#1E293B] border-slate-700">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="search" className="text-slate-300 mb-2 block">
                <Search className="w-4 h-4 inline mr-2" />
                Rechercher
              </Label>
              <Input
                id="search"
                placeholder="Nom, email, pays..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-slate-800 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label htmlFor="status-filter" className="text-slate-300 mb-2 block">
                <Filter className="w-4 h-4 inline mr-2" />
                Filtrer par statut
              </Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                  <SelectValue placeholder="Tous les statuts" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem value="all" className="text-white">Tous les statuts</SelectItem>
                  {Object.entries(statusLabels).map(([key, value]) => (
                    <SelectItem key={key} value={key} className="text-white">
                      {value.icon} {value.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button 
                variant="outline" 
                className="w-full border-slate-600 text-white hover:bg-slate-700"
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                }}
              >
                Réinitialiser
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Liste des prospects */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-orange-500" />
          Prospects ({filteredProspects.length})
        </h3>

        {filteredProspects.length === 0 ? (
          <Card className="bg-[#1E293B] border-slate-700">
            <CardContent className="p-12 text-center">
              <p className="text-slate-400">Aucun prospect trouvé</p>
            </CardContent>
          </Card>
        ) : (
          filteredProspects.map((prospect) => (
            <Card 
              key={prospect.id} 
              className="bg-[#1E293B] border-slate-700 hover:border-orange-500/50 transition-all"
            >
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  {/* Informations du prospect */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <h4 className="text-lg font-bold text-white">{prospect.name}</h4>
                      <Badge className={`${statusLabels[prospect.status]?.color || 'bg-gray-500'} text-white`}>
                        {statusLabels[prospect.status]?.icon} {statusLabels[prospect.status]?.label || prospect.status}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-2 text-slate-300">
                        <Mail className="w-4 h-4 text-slate-400" />
                        {prospect.email}
                      </div>
                      {prospect.phone && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Phone className="w-4 h-4 text-slate-400" />
                          {prospect.phone}
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-slate-300">
                        <Globe className="w-4 h-4 text-slate-400" />
                        {prospect.country}
                      </div>
                      {prospect.assigned_to_name && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Users className="w-4 h-4 text-slate-400" />
                          Assigné à: {prospect.assigned_to_name}
                        </div>
                      )}
                    </div>

                    {prospect.message && (
                      <p className="text-slate-400 text-sm italic">"{prospect.message.substring(0, 100)}..."</p>
                    )}

                    {prospect.payment_50k_amount && (
                      <Badge className="bg-green-500/20 text-green-400">
                        💰 {prospect.payment_50k_amount} CFA payés
                      </Badge>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    {userRole === 'SUPERADMIN' && prospect.status === 'nouveau' && (
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            size="sm"
                            className="bg-orange-500 hover:bg-orange-600"
                            onClick={() => setSelectedProspect(prospect)}
                          >
                            <UserPlus className="w-4 h-4 mr-2" />
                            Assigner
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-[#1E293B] border-slate-700">
                          <DialogHeader>
                            <DialogTitle className="text-white">Assigner le prospect</DialogTitle>
                            <DialogDescription className="text-slate-400">
                              Choisissez un employé ou manager pour contacter {prospect.name}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 mt-4">
                            <div>
                              <Label htmlFor="assignee" className="text-slate-300">Employé/Manager</Label>
                              <Select value={assigneeId} onValueChange={setAssigneeId}>
                                <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-2">
                                  <SelectValue placeholder="Sélectionner..." />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-600">
                                  {employees.map((emp) => (
                                    <SelectItem key={emp.id} value={emp.id} className="text-white">
                                      {emp.full_name} ({emp.role})
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                            <Button 
                              onClick={handleAssignProspect}
                              className="w-full bg-orange-500 hover:bg-orange-600"
                            >
                              Confirmer l'assignation
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    )}

                    {userRole === 'SUPERADMIN' && prospect.status === 'paiement_50k' && (
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            size="sm"
                            variant="outline"
                            className="border-slate-600 text-white hover:bg-slate-700"
                            onClick={() => setSelectedProspect(prospect)}
                          >
                            <MessageCircle className="w-4 h-4 mr-2" />
                            Ajouter Note
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-[#1E293B] border-slate-700">
                          <DialogHeader>
                            <DialogTitle className="text-white">Note Consultant</DialogTitle>
                            <DialogDescription className="text-slate-400">
                              Ajoutez des notes sur votre consultation avec {prospect.name}
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 mt-4">
                            {prospect.consultant_notes && prospect.consultant_notes.length > 0 && (
                              <div className="bg-slate-800 p-4 rounded-lg space-y-2 max-h-40 overflow-y-auto">
                                <p className="text-slate-400 text-sm font-semibold">Notes précédentes:</p>
                                {prospect.consultant_notes.map((note, idx) => (
                                  <div key={idx} className="border-l-2 border-orange-500 pl-3">
                                    <p className="text-slate-300 text-sm">{note.content}</p>
                                    <p className="text-slate-500 text-xs mt-1">
                                      {note.created_by} - {new Date(note.created_at).toLocaleDateString('fr-FR')}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                            <div>
                              <Label htmlFor="notes" className="text-slate-300">Nouvelle note</Label>
                              <textarea
                                id="notes"
                                rows={4}
                                value={consultantNotes}
                                onChange={(e) => setConsultantNotes(e.target.value)}
                                placeholder="Détails de la consultation, recommandations..."
                                className="w-full mt-2 px-3 py-2 bg-slate-800 border border-slate-600 text-white rounded-md"
                              />
                            </div>
                            <Button 
                              onClick={handleAddConsultantNote}
                              className="w-full bg-orange-500 hover:bg-orange-600"
                            >
                              Enregistrer la note
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    )}

                    <Button 
                      size="sm"
                      variant="ghost"
                      className="text-slate-400 hover:text-white"
                      onClick={() => {
                        // TODO: Afficher détails complets
                        toast.info('Détails du prospect');
                      }}
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Détails
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
