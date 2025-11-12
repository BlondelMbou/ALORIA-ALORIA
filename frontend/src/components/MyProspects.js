import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { toast } from 'sonner';
import api from '../utils/api';
import { 
  Users, 
  DollarSign, 
  Search,
  AlertTriangle,
  Mail,
  Phone,
  Globe,
  CheckCircle,
  UserPlus
} from 'lucide-react';

/**
 * Composant pour les prospects assignés à l'employé/manager
 * Permet de gérer et d'affecter les prospects au consultant
 */
export default function MyProspects() {
  const [prospects, setProspects] = useState([]);
  const [filteredProspects, setFilteredProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('Cash');
  const [transactionRef, setTransactionRef] = useState('');
  const [showConversionDialog, setShowConversionDialog] = useState(false);
  const [conversionData, setConversionData] = useState({
    country: '',
    visa_type: '',
    first_payment_amount: 0
  });

  const statusLabels = {
    'assigne_employe': { label: 'À Contacter', color: 'bg-purple-500', icon: '📞' },
    'paiement_50k': { label: 'Chez le Consultant', color: 'bg-green-500', icon: '💼' },
    'en_consultation': { label: 'En Consultation', color: 'bg-orange-500', icon: '💬' },
    'converti_client': { label: 'Devenu Client', color: 'bg-emerald-500', icon: '✅' }
  };

  useEffect(() => {
    fetchMyProspects();
    
    // Auto-refresh toutes les 30 secondes pour mettre à jour les statuts
    const interval = setInterval(fetchMyProspects, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterProspects();
  }, [prospects, searchTerm]);

  const fetchMyProspects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/contact-messages');
      setProspects(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des prospects:', error);
      toast.error('Impossible de charger vos prospects');
    } finally {
      setLoading(false);
    }
  };

  const filterProspects = () => {
    let filtered = [...prospects];

    if (searchTerm) {
      filtered = filtered.filter(p =>
        p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.country?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    setFilteredProspects(filtered);
  };

  const handleAffectToConsultant = async () => {
    if (!selectedProspect) return;

    try {
      const response = await api.patch(`/contact-messages/${selectedProspect.id}/assign-consultant`, {
        payment_method: paymentMethod,
        transaction_reference: transactionRef || null
      });
      
      toast.success(`Paiement de 50,000 CFA enregistré ! Facture: ${response.data.invoice_number}`);
      setShowConfirmDialog(false);
      setSelectedProspect(null);
      setPaymentMethod('Cash');
      setTransactionRef('');
      fetchMyProspects();
    } catch (error) {
      console.error('Erreur lors de l\'affectation:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'affectation au consultant');
    }
  };

  const handleConvertToClient = async (prospect) => {
    if (!window.confirm(`Convertir "${prospect.name}" en client ? Cette action créera un compte client et un dossier.`)) {
      return;
    }

    try {
      await api.post(`/contact-messages/${prospect.id}/convert-to-client`);
      toast.success('Prospect converti en client avec succès !');
      fetchMyProspects();
    } catch (error) {
      console.error('Erreur conversion:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la conversion en client');
    }
  };

  const openConfirmDialog = (prospect) => {
    setSelectedProspect(prospect);
    setShowConfirmDialog(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  const prospectsToContact = prospects.filter(p => p.status === 'assigne_employe');
  const prospectsWithConsultant = prospects.filter(p => ['paiement_50k', 'en_consultation'].includes(p.status));
  const convertedClients = prospects.filter(p => p.status === 'converti_client');

  return (
    <div className="space-y-6">
      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border-purple-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">À Contacter</p>
                <p className="text-2xl font-bold text-white">{prospectsToContact.length}</p>
              </div>
              <div className="text-3xl">📞</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Chez Consultant</p>
                <p className="text-2xl font-bold text-white">{prospectsWithConsultant.length}</p>
              </div>
              <div className="text-3xl">💼</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 border-emerald-500/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Convertis</p>
                <p className="text-2xl font-bold text-white">{convertedClients.length}</p>
              </div>
              <div className="text-3xl">✅</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recherche */}
      <Card className="bg-[#1E293B] border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-slate-400" />
            <Input
              placeholder="Rechercher un prospect..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-800 border-slate-600 text-white"
            />
          </div>
        </CardContent>
      </Card>

      {/* Liste des prospects */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-orange-500" />
          Mes Prospects ({filteredProspects.length})
        </h3>

        {filteredProspects.length === 0 ? (
          <Card className="bg-[#1E293B] border-slate-700">
            <CardContent className="p-12 text-center">
              <p className="text-slate-400">Aucun prospect assigné</p>
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
                  {/* Informations */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3 flex-wrap">
                      <h4 className="text-lg font-bold text-white">{prospect.name}</h4>
                      <Badge className={`${statusLabels[prospect.status]?.color || 'bg-gray-500'} text-white`}>
                        {statusLabels[prospect.status]?.icon} {statusLabels[prospect.status]?.label}
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
                        {prospect.country} - {prospect.visa_type}
                      </div>
                    </div>

                    {prospect.message && (
                      <p className="text-slate-400 text-sm italic">
                        "{prospect.message.substring(0, 150)}..."
                      </p>
                    )}

                    {prospect.payment_50k_amount && (
                      <Badge className="bg-green-500/20 text-green-400">
                        💰 {prospect.payment_50k_amount} CFA payés
                      </Badge>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2 min-w-[200px]">
                    {prospect.status === 'assigne_employe' && (
                      <>
                        <Button 
                          size="sm"
                          className="bg-orange-500 hover:bg-orange-600"
                          onClick={() => openConfirmDialog(prospect)}
                        >
                          <DollarSign className="w-4 h-4 mr-2" />
                          Affecter au Consultant
                        </Button>
                        <p className="text-xs text-slate-400 text-center mt-1">
                          💡 Paiement requis: 50 000 CFA pour consultation
                        </p>
                        <p className="text-xs text-orange-400 text-center">
                          ⚠️ Conversion client possible APRÈS consultation
                        </p>
                      </>
                    )}

                    {prospect.status === 'paiement_50k' && (
                      <>
                        <Badge className="bg-green-500/20 text-green-400 justify-center py-2 mb-2">
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Chez le consultant
                        </Badge>
                        <Button 
                          size="sm"
                          className="bg-blue-500 hover:bg-blue-600"
                          onClick={() => handleConvertToClient(prospect)}
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          Convertir en Client
                        </Button>
                      </>
                    )}

                    {prospect.status === 'en_consultation' && (
                      <>
                        <Badge className="bg-orange-500/20 text-orange-400 justify-center py-2 mb-2">
                          💬 En consultation
                        </Badge>
                        <Button 
                          size="sm"
                          className="bg-blue-500 hover:bg-blue-600"
                          onClick={() => handleConvertToClient(prospect)}
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          Convertir en Client
                        </Button>
                      </>
                    )}

                    {prospect.status === 'converti_client' && (
                      <Badge className="bg-emerald-500/20 text-emerald-400 justify-center py-2">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Client créé
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Dialog de confirmation */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent className="bg-[#1E293B] border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-orange-500" />
              Confirmation Paiement & Affectation
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              Veuillez confirmer que le prospect a bien effectué le paiement avant de l'affecter au consultant.
            </DialogDescription>
          </DialogHeader>
          
          {selectedProspect && (
            <div className="space-y-4 mt-4">
              <div className="bg-slate-800 p-4 rounded-lg space-y-2">
                <p className="text-white font-semibold">{selectedProspect.name}</p>
                <p className="text-slate-400 text-sm">{selectedProspect.email}</p>
                <p className="text-slate-400 text-sm">{selectedProspect.country} - {selectedProspect.visa_type}</p>
              </div>

              <div className="bg-orange-500/10 border border-orange-500/30 p-4 rounded-lg">
                <p className="text-orange-400 font-semibold mb-2 flex items-center gap-2">
                  <DollarSign className="w-5 h-5" />
                  Montant requis: 50 000 CFA
                </p>
                <p className="text-slate-300 text-sm">
                  Ce montant couvre la consultation approfondie avec le consultant.
                  Un email de confirmation sera envoyé automatiquement au prospect.
                </p>
              </div>

              <div className="space-y-3">
                <div>
                  <Label className="text-slate-300">Méthode de paiement *</Label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full mt-2 px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="Cash">Cash (Espèces)</option>
                    <option value="Mobile Money">Mobile Money</option>
                    <option value="Virement">Virement Bancaire</option>
                  </select>
                </div>

                <div>
                  <Label className="text-slate-300">Référence transaction (optionnelle)</Label>
                  <Input
                    value={transactionRef}
                    onChange={(e) => setTransactionRef(e.target.value)}
                    placeholder="Ex: MTN-123456789 ou N° de reçu"
                    className="mt-2 bg-slate-800 border-slate-600 text-white"
                  />
                </div>
              </div>

              <div className="flex gap-3">
                <Button 
                  variant="outline"
                  className="flex-1 border-slate-600 text-white hover:bg-slate-700"
                  onClick={() => {
                    setShowConfirmDialog(false);
                    setSelectedProspect(null);
                  }}
                >
                  Annuler
                </Button>
                <Button 
                  className="flex-1 bg-orange-500 hover:bg-orange-600"
                  onClick={handleAffectToConsultant}
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Confirmer Affectation
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
