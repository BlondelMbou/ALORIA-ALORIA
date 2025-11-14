import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Globe, LogOut, Users, FileText, TrendingUp, CheckCircle, Clock, AlertCircle, UserCheck, Building2, Search, Filter, Plus, UserPlus, MessageCircle, User, Lock, Wallet, Download, Settings } from 'lucide-react';
import WithdrawalManager from '../components/WithdrawalManager';
import MyProspects from '../components/MyProspects';
import ChatWidget from '../components/ChatWidget';
import NotificationBell from '../components/NotificationBell';
import SearchAndSort from '../components/SearchAndSort';
import AloriaLogo from '../components/AloriaLogo';
import ProfileSettings from '../components/ProfileSettings';
import CredentialsPopup from '../components/CredentialsPopup';
import useSocket from '../hooks/useSocket';
import api, { clientsAPI, casesAPI, dashboardAPI, employeesAPI, visitorsAPI } from '../utils/api';

export default function ManagerDashboard() {
  const { user, logout } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [filteredMyClients, setFilteredMyClients] = useState([]);
  const [cases, setCases] = useState([]);
  const [filteredCases, setFilteredCases] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [visitors, setVisitors] = useState([]);
  const [filteredVisitors, setFilteredVisitors] = useState([]);
  const [payments, setPayments] = useState([]);
  const [filteredPayments, setFilteredPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newVisitor, setNewVisitor] = useState({ 
    full_name: '',
    phone_number: '',
    purpose: 'Consultation initiale',
    other_purpose: '',
    cni_number: '' 
  });
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [showCreateEmployee, setShowCreateEmployee] = useState(false);
  const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);
  const [newClientCredentials, setNewClientCredentials] = useState(null);
  const [newClient, setNewClient] = useState({
    email: '',
    full_name: '',
    phone: '',
    country: '',
    visa_type: '',
    first_payment_amount: 0,
    message: ''
  });
  const [newEmployee, setNewEmployee] = useState({
    email: '',
    full_name: '',
    phone: ''
  });
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [pendingPayments, setPendingPayments] = useState([]);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [rejectionDialog, setRejectionDialog] = useState({ show: false, payment: null, reason: '' });
  const [confirmationDialog, setConfirmationDialog] = useState({ show: false, payment: null, code: '', generatedCode: '' });
  const [reassignDialog, setReassignDialog] = useState({ show: false, client: null, newEmployeeId: '' });
  const [activeTab, setActiveTab] = useState('overview');
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  
  // WebSocket hook
  const { connected } = useSocket(localStorage.getItem('token'));

  // Calcul dynamique des stats à partir des données locales pour mise à jour en temps réel
  const calculatedStats = React.useMemo(() => {
    const activeCases = cases.filter(c => 
      c.status === 'In Progress' || c.status === 'Under Review' || c.status === 'En cours' || c.status === 'En attente'
    ).length;
    
    const completedCases = cases.filter(c => 
      c.status === 'Approved' || c.status === 'Completed' || c.status === 'Terminé' || c.status === 'Approuvé'
    ).length;
    
    return {
      total_cases: cases.length,
      active_cases: activeCases,
      completed_cases: completedCases,
      total_clients: clients.length,
      total_employees: employees.length,
      total_visitors: visitors.length
    };
  }, [cases, clients, employees, visitors]);

  // Utiliser les stats calculées si disponibles, sinon les stats du backend
  const displayStats = calculatedStats.total_cases > 0 ? calculatedStats : stats;

  useEffect(() => {
    fetchData();
    fetchPayments();
    
    // Auto-refresh des données toutes les 5 minutes pour garder les stats à jour
    const refreshInterval = setInterval(() => {
      // Refresh silencieux sans recharger toute la page
      fetchData();
      fetchPayments();
    }, 300000); // 5 minutes
    
    return () => clearInterval(refreshInterval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, clientsRes, casesRes, employeesRes, visitorsRes] = await Promise.all([
        dashboardAPI.getStats(),
        clientsAPI.getAll(),
        casesAPI.getAll(),
        employeesAPI.getAll(),
        visitorsAPI.getAll()
      ]);

      setStats(statsRes.data);
      setClients(clientsRes.data);
      setCases(casesRes.data);
      setEmployees(employeesRes.data);
      setVisitors(visitorsRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPayments = async () => {
    try {
      const [pendingRes, historyRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/pending`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/history`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);

      if (pendingRes.ok) {
        const pending = await pendingRes.json();
        setPendingPayments(pending);
      }

      if (historyRes.ok) {
        const history = await historyRes.json();
        setPaymentHistory(history);
      }
    } catch (error) {
      console.error('Error fetching payments:', error);
    }
  };

  const handlePaymentAction = async (payment, action) => {
    if (action === 'REJECTED') {
      setRejectionDialog({ show: true, payment, reason: '' });
      return;
    }
    
    if (action === 'CONFIRMED') {
      try {
        // Première étape : générer le code de confirmation
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/${payment.id}/confirm`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ action: 'CONFIRMED' })
        });
        
        if (!response.ok) throw new Error('Échec de génération du code');
        
        const result = await response.json();
        
        // Ouvrir le dialog de confirmation avec le code généré
        setConfirmationDialog({
          show: true,
          payment,
          code: '',
          generatedCode: result.confirmation_code
        });
        
      } catch (error) {
        toast.error(error.message || 'Erreur lors de la confirmation');
      }
    }
  };

  const handleConfirmWithCode = async () => {
    const { payment, code } = confirmationDialog;
    
    if (!code || code.trim() === '') {
      toast.error('Veuillez saisir le code de confirmation');
      return;
    }
    
    try {
      const confirmResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/${payment.id}/confirm`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          action: 'CONFIRMED',
          confirmation_code: code.trim()
        })
      });
      
      if (!confirmResponse.ok) {
        const errorData = await confirmResponse.json();
        throw new Error(errorData.detail || 'Code de confirmation incorrect');
      }
      
      toast.success('✅ Paiement confirmé avec succès!');
      setConfirmationDialog({ show: false, payment: null, code: '', generatedCode: '' });
      fetchPayments();
    } catch (error) {
      toast.error(error.message || 'Erreur lors de la confirmation');
    }
  };

  const handleRejection = async () => {
    if (!rejectionDialog.reason.trim()) {
      toast.error('Veuillez fournir une raison de rejet');
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/${rejectionDialog.payment.id}/confirm`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          action: 'REJECTED',
          rejection_reason: rejectionDialog.reason
        })
      });
      
      if (!response.ok) throw new Error('Failed to reject payment');
      
      toast.success('Paiement rejeté');
      setRejectionDialog({ show: false, payment: null, reason: '' });
      fetchPayments();
    } catch (error) {
      toast.error('Erreur lors du rejet du paiement');
    }
  };

  const downloadInvoice = async (paymentId, invoiceNumber) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/${paymentId}/invoice`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Facture_${invoiceNumber || paymentId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Facture téléchargée!');
      } else {
        toast.error('Impossible de télécharger la facture');
      }
    } catch (error) {
      console.error('Error downloading invoice:', error);
      toast.error('Erreur lors du téléchargement');
    }
  };

  const handleReassignClient = async () => {
    if (!reassignDialog.newEmployeeId) {
      toast.error('Veuillez sélectionner un employé');
      return;
    }

    try {
      await clientsAPI.reassign(reassignDialog.client.id, reassignDialog.newEmployeeId);
      toast.success('Client réassigné avec succès');
      setReassignDialog({ show: false, client: null, newEmployeeId: '' });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la réassignation');
    }
  };

  const handleCreateClient = async (e) => {
    e.preventDefault();
    
    if (!newClient.email || !newClient.full_name || !newClient.country || !newClient.visa_type) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    try {
      // Utiliser l'endpoint refactorisé /api/clients
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/clients`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newClient)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la création');
      }
      
      const data = await response.json();
      
      // Préparer les credentials pour le popup
      setNewClientCredentials({
        email: data.login_email || data.email,
        login_email: data.login_email || data.email,
        temporary_password: data.default_password || data.temporary_password,
        default_password: data.default_password || data.temporary_password,
        full_name: newClient.full_name,
        role: 'CLIENT',
        additional_info: {
          case_id: data.id,
          country: newClient.country,
          visa_type: newClient.visa_type
        }
      });
      setShowCredentialsDialog(true);
      
      toast.success('✅ Client créé avec succès!');
      setShowCreateClient(false);
      
      // Reset form
      setNewClient({
        email: '',
        full_name: '',
        phone: '',
        country: '',
        visa_type: '',
        first_payment_amount: 0,
        message: ''
      });
      
      fetchData(); // Refresh
    } catch (error) {
      toast.error(error.message || 'Erreur lors de la création du client');
      console.error(error);
    }
  };

  const handleCreateEmployee = async (e) => {
    e.preventDefault();
    
    if (!newEmployee.email || !newEmployee.full_name || !newEmployee.phone) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    try {
      // Utiliser l'endpoint /api/users/create
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          email: newEmployee.email,
          full_name: newEmployee.full_name,
          phone: newEmployee.phone,
          role: 'EMPLOYEE',
          send_email: false
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la création');
      }
      
      const data = await response.json();
      
      // Préparer les credentials pour le popup
      setNewClientCredentials({
        email: data.email,
        login_email: data.email,
        temporary_password: data.temporary_password,
        default_password: data.temporary_password,
        full_name: newEmployee.full_name,
        role: 'EMPLOYEE'
      });
      setShowCredentialsDialog(true);
      
      toast.success('✅ Employé créé avec succès!');
      setShowCreateEmployee(false);
      
      // Reset form
      setNewEmployee({
        email: '',
        full_name: '',
        phone: ''
      });
      
      fetchData(); // Refresh
    } catch (error) {
      toast.error(error.message || 'Erreur lors de la création de l\'employé');
      console.error(error);
    }
  };

  const handleUpdateCase = async (caseId, updates) => {
    try {
      await casesAPI.update(caseId, updates);
      toast.success('Dossier mis à jour');
      fetchData(); // Refresh unique
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
      console.error(error);
    }
  };

  const handleAddVisitor = async () => {
    if (!newVisitor.full_name || !newVisitor.phone_number || !newVisitor.cni_number) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      await visitorsAPI.create(newVisitor);
      toast.success('Visiteur enregistré avec succès');
      setNewVisitor({
        full_name: '',
        phone_number: '',
        purpose: 'Consultation initiale',
        other_purpose: '',
        cni_number: ''
      });
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error creating visitor:', error);
      toast.error('Erreur lors de l\'enregistrement du visiteur');
    }
  };

  const handleCheckoutVisitor = async (visitorId) => {
    try {
      await visitorsAPI.checkout(visitorId);
      toast.success('Visiteur marqué comme parti');
      fetchData();
    } catch (error) {
      console.error('Error checking out visitor:', error);
      toast.error('Erreur lors du checkout');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Nouveau': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      'En cours': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      'En attente': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      'Approuvé': 'bg-green-500/10 text-green-400 border-green-500/20',
      'Terminé': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      'In Progress': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      'Under Review': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      'Approved': 'bg-green-500/10 text-green-400 border-green-500/20',
      'Completed': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };
    return colors[status] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
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
                  Manager Dashboard
                </h1>
                <p className="text-sm text-slate-400 mt-1">Bienvenue, {user?.full_name}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                onClick={() => setShowProfileSettings(!showProfileSettings)}
                className="bg-slate-700 hover:bg-slate-600 text-white"
                title="Mon Profil"
              >
                <Settings className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Profil</span>
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50" data-testid="create-client-btn">
                    <UserPlus className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">Nouveau Client</span>
                    <span className="sm:hidden">Client</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#1E293B] border-slate-700 max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="text-white">Créer un Nouveau Client</DialogTitle>
                    <DialogDescription className="text-slate-400">
                      Remplissez les informations pour créer un nouveau profil client et son dossier d'immigration
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateClient} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-slate-300">Nom Complet *</Label>
                        <Input
                          value={newClient.full_name}
                          onChange={(e) => setNewClient({ ...newClient, full_name: e.target.value })}
                          required
                          placeholder="Ex: Jean Dupont"
                          className="bg-slate-800 border-slate-600 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-300">Email *</Label>
                        <Input
                          type="email"
                          value={newClient.email}
                          onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                          required
                          placeholder="email@example.com"
                          className="bg-slate-800 border-slate-600 text-white"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-slate-300">Téléphone</Label>
                      <Input
                        value={newClient.phone}
                        onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}
                        placeholder="+237 XXX XXX XXX"
                        className="bg-slate-800 border-slate-600 text-white"
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-slate-300">Pays de Destination *</Label>
                        <select
                          value={newClient.country}
                          onChange={(e) => setNewClient({ ...newClient, country: e.target.value, visa_type: '' })}
                          required
                          className="w-full bg-slate-800 border-slate-600 text-white p-2 rounded"
                        >
                          <option value="">Sélectionner...</option>
                          <option value="Canada">Canada</option>
                          <option value="France">France</option>
                        </select>
                      </div>
                      
                      <div>
                        <Label className="text-slate-300">Type de Visa *</Label>
                        <select
                          value={newClient.visa_type}
                          onChange={(e) => setNewClient({ ...newClient, visa_type: e.target.value })}
                          required
                          disabled={!newClient.country}
                          className="w-full bg-slate-800 border-slate-600 text-white p-2 rounded"
                        >
                          <option value="">Sélectionner...</option>
                          {newClient.country === 'Canada' && (
                            <>
                              <option value="Permis de travail">Permis de travail</option>
                              <option value="Permis d'études">Permis d'études</option>
                              <option value="Résidence permanente (Entrée express)">Résidence permanente (Entrée express)</option>
                            </>
                          )}
                          {newClient.country === 'France' && (
                            <>
                              <option value="Permis de travail (Passeport Talent)">Permis de travail (Passeport Talent)</option>
                              <option value="Visa étudiant">Visa étudiant</option>
                              <option value="Regroupement familial">Regroupement familial</option>
                            </>
                          )}
                        </select>
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-slate-300">Premier Versement (CFA)</Label>
                      <Input
                        type="number"
                        min="0"
                        value={newClient.first_payment_amount}
                        onChange={(e) => setNewClient({ ...newClient, first_payment_amount: parseFloat(e.target.value) || 0 })}
                        placeholder="Montant du premier versement (optionnel)"
                        className="bg-slate-800 border-slate-600 text-white"
                      />
                      <p className="text-slate-500 text-xs mt-1">Optionnel - Si le client effectue déjà un premier versement</p>
                    </div>
                    
                    <div className="bg-blue-500/10 border border-blue-500/30 p-3 rounded-lg">
                      <p className="text-blue-400 text-sm">
                        ℹ️ Un compte client sera créé avec un mot de passe temporaire qui sera affiché après la création.
                      </p>
                    </div>
                    
                    <Button 
                      type="submit" 
                      className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white"
                      disabled={!newClient.country || !newClient.visa_type}
                    >
                      <UserPlus className="w-4 h-4 mr-2" />
                      Créer le Client
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
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

      {/* Profil Settings */}
      {showProfileSettings && (
        <div className="p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Mon Profil</h2>
              <Button
                onClick={() => setShowProfileSettings(false)}
                variant="outline"
                className="border-slate-600 text-white"
              >
                Retour
              </Button>
            </div>
            <ProfileSettings user={user} onUpdate={fetchData} />
          </div>
        </div>
      )}

      {/* Stats Cards */}
      {!showProfileSettings && (
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-blue-500 border-slate-700" data-testid="kpi-total-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Total Dossiers</p>
                  <p className="text-3xl font-bold text-white">{displayStats?.total_cases || 0}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center border border-blue-500/20">
                  <FileText className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-yellow-500 border-slate-700" data-testid="kpi-active-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Dossiers Actifs</p>
                  <p className="text-3xl font-bold text-white">{displayStats?.active_cases || 0}</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center border border-yellow-500/20">
                  <Clock className="w-6 h-6 text-yellow-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-green-500 border-slate-700" data-testid="kpi-completed-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Terminés</p>
                  <p className="text-3xl font-bold text-white">{displayStats?.completed_cases || 0}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center border border-green-500/20">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-orange-500 border-slate-700" data-testid="kpi-total-clients">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Total Clients</p>
                  <p className="text-3xl font-bold text-white">{displayStats?.total_clients || 0}</p>
                </div>
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center border border-orange-500/20">
                  <Users className="w-6 h-6 text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="clients" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-7 gap-2 bg-[#1E293B] border border-slate-700 p-2">
            <TabsTrigger value="clients" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Clients</TabsTrigger>
            <TabsTrigger value="employees" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Équipe</TabsTrigger>
            <TabsTrigger value="cases" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Dossiers</TabsTrigger>
            <TabsTrigger value="visitors" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Visiteurs</TabsTrigger>
            <TabsTrigger value="prospects" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Prospects</TabsTrigger>
            <TabsTrigger value="payments" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Paiements</TabsTrigger>
            <TabsTrigger value="withdrawals" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-orange-600 data-[state=active]:text-white text-slate-300">Retraits</TabsTrigger>
          </TabsList>

          {/* Clients Tab */}
          <TabsContent value="clients">
            <Tabs defaultValue="all-clients" className="space-y-4">
              <TabsList className="grid w-full grid-cols-2 bg-[#0F172A] border border-slate-700">
                <TabsTrigger 
                  value="all-clients" 
                  className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-slate-300"
                >
                  Tous les Clients
                </TabsTrigger>
                <TabsTrigger 
                  value="my-clients" 
                  className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-slate-300"
                >
                  Mes Clients
                </TabsTrigger>
              </TabsList>

              {/* Tous les Clients */}
              <TabsContent value="all-clients">
                <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Liste de Tous les Clients</CardTitle>
                    <CardDescription className="text-slate-400">Suivez l'évolution des dossiers de vos clients</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Recherche et Tri */}
                    <SearchAndSort
                      data={clients}
                      searchFields={['client_name', 'assigned_employee_name', 'country', 'visa_type', 'current_status']}
                      sortOptions={[
                        { value: 'created_at', label: 'Date de création' },
                        { value: 'client_name', label: 'Nom du client' },
                        { value: 'country', label: 'Pays' },
                        { value: 'progress_percentage', label: 'Progression' },
                        { value: 'current_status', label: 'Statut' }
                      ]}
                      onFilteredDataChange={setFilteredClients}
                      placeholder="Rechercher un dossier (client, pays, type de visa, statut)..."
                    />

                {/* Cartes Clients - Style Mes Dossiers */}
                <div className="grid gap-6 mt-4">
                  {filteredClients.map((client) => {
                    const clientCase = cases.find(c => c.client_id === client.user_id);
                    const currentStepIndex = clientCase?.current_step_index || 0;
                    const totalSteps = clientCase?.workflow_steps?.length || 0;
                    const progressPercentage = client.progress_percentage || 0;

                    return (
                      <Card key={client.id} className="bg-[#0F172A] border-slate-700 hover:border-orange-500/50 transition-all">
                        <CardContent className="p-6">
                          {/* En-tête avec nom et statut */}
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="text-xl font-semibold text-white mb-1">
                                {client.full_name || client.client_name || 'Client'}
                              </h3>
                              <p className="text-slate-300">
                                {client.country} - {client.visa_type}
                              </p>
                            </div>
                            <Badge className={getStatusColor(client.current_status)}>
                              {client.current_status || 'Nouveau'}
                            </Badge>
                          </div>

                          {/* Progression */}
                          <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm text-slate-400">
                                Step {currentStepIndex + 1} of {totalSteps || 0}
                              </span>
                              <span className="text-sm font-medium text-orange-400">
                                {progressPercentage}%
                              </span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                              <div 
                                className="bg-gradient-to-r from-orange-500 to-orange-600 h-full transition-all" 
                                style={{ width: `${progressPercentage}%` }}
                              />
                            </div>
                          </div>

                          {/* Informations supplémentaires */}
                          <div className="bg-slate-900/50 rounded-lg p-4 mb-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-slate-400">Conseiller assigné:</span>
                              <span className="text-sm text-white">{client.assigned_employee_name || 'Non assigné'}</span>
                            </div>
                            {clientCase && (
                              <>
                                <div className="text-sm text-slate-400 border-t border-slate-700 pt-2 mt-2">
                                  <span className="font-semibold text-slate-300">Current Step:</span>
                                  <p className="text-slate-400 mt-1">
                                    {clientCase.workflow_steps?.[currentStepIndex]?.title || 'En cours de traitement'}
                                  </p>
                                </div>
                                <div className="text-sm text-slate-400">
                                  <span className="font-semibold text-slate-300">Required Documents:</span>
                                  <p className="text-slate-400 mt-1">
                                    {clientCase.workflow_steps?.[currentStepIndex]?.documents?.join(', ') || 'Aucun'}
                                  </p>
                                </div>
                              </>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white"
                              onClick={() => setSelectedClient(client)}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              Voir Détails
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="border-orange-600 text-orange-400 hover:bg-orange-600 hover:text-white"
                              onClick={() => setReassignDialog({ show: true, client, newEmployeeId: '' })}
                            >
                              Réassigner
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}

                  {filteredClients.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-slate-400 text-lg">Aucun client trouvé</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Mes Clients (Manager's own clients) */}
          <TabsContent value="my-clients">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Mes Clients Personnels</CardTitle>
                <CardDescription className="text-slate-400">Suivez l'évolution des dossiers de vos clients personnels</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Cartes Clients - Style Mes Dossiers */}
                <div className="grid gap-6 mt-4">
                  {clients.filter(c => c.assigned_employee_id === user?.id).map((client) => {
                    const clientCase = cases.find(c => c.client_id === client.user_id);
                    const currentStepIndex = clientCase?.current_step_index || 0;
                    const totalSteps = clientCase?.workflow_steps?.length || 0;
                    const progressPercentage = client.progress_percentage || 0;

                    return (
                      <Card key={client.id} className="bg-[#0F172A] border-slate-700 hover:border-orange-500/50 transition-all">
                        <CardContent className="p-6">
                          {/* En-tête avec nom et statut */}
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="text-xl font-semibold text-white mb-1">
                                {client.full_name || client.client_name || 'Client'}
                              </h3>
                              <p className="text-slate-300">
                                {client.country} - {client.visa_type}
                              </p>
                            </div>
                            <Badge className={getStatusColor(client.current_status)}>
                              {client.current_status || 'Nouveau'}
                            </Badge>
                          </div>

                          {/* Progression */}
                          <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm text-slate-400">
                                Step {currentStepIndex + 1} of {totalSteps || 0}
                              </span>
                              <span className="text-sm font-medium text-orange-400">
                                {progressPercentage}%
                              </span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                              <div 
                                className="bg-gradient-to-r from-orange-500 to-orange-600 h-full transition-all" 
                                style={{ width: `${progressPercentage}%` }}
                              />
                            </div>
                          </div>

                          {/* Informations supplémentaires */}
                          <div className="bg-slate-900/50 rounded-lg p-4 mb-4 space-y-2">
                            {clientCase && (
                              <>
                                <div className="text-sm text-slate-400">
                                  <span className="font-semibold text-slate-300">Current Step:</span>
                                  <p className="text-slate-400 mt-1">
                                    {clientCase.workflow_steps?.[currentStepIndex]?.title || 'En cours de traitement'}
                                  </p>
                                </div>
                                <div className="text-sm text-slate-400 border-t border-slate-700 pt-2 mt-2">
                                  <span className="font-semibold text-slate-300">Required Documents:</span>
                                  <p className="text-slate-400 mt-1">
                                    {clientCase.workflow_steps?.[currentStepIndex]?.documents?.join(', ') || 'Aucun'}
                                  </p>
                                </div>
                              </>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white"
                              onClick={() => setSelectedClient(client)}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              Voir Détails
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="border-orange-600 text-orange-400 hover:bg-orange-600 hover:text-white"
                              onClick={() => setReassignDialog({ show: true, client, newEmployeeId: '' })}
                            >
                              Réassigner
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}

                  {clients.filter(c => c.assigned_employee_id === user?.id).length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-slate-400 text-lg">Aucun client ne vous est directement assigné</p>
                      <p className="text-slate-500 text-sm mt-2">Créez un nouveau client ou demandez une réassignation</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </TabsContent>

      {/* Employees Tab */}
          <TabsContent value="employees">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-white">Membres de l'Équipe</CardTitle>
                  <CardDescription className="text-slate-400">Voir et gérer vos conseillers en immigration</CardDescription>
                </div>
                <Button
                  onClick={() => setShowCreateEmployee(true)}
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Créer un Employé
                </Button>
              </CardHeader>
              <CardContent>
                {/* Recherche et Tri */}
                <SearchAndSort
                  data={employees}
                  searchFields={['full_name', 'email', 'phone']}
                  sortOptions={[
                    { value: 'full_name', label: 'Nom' },
                    { value: 'email', label: 'Email' },
                    { value: 'created_at', label: 'Date d\'ajout' }
                  ]}
                  onFilteredDataChange={setFilteredEmployees}
                  placeholder="Rechercher un employé (nom, email, téléphone)..."
                />

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredEmployees.map((employee) => {
                    const employeeCases = cases.filter(c => {
                      const client = clients.find(cl => cl.id === c.client_id);
                      return client?.assigned_employee_id === employee.id;
                    });
                    const completedCases = employeeCases.filter(c => c.status === 'Approved' || c.status === 'Completed').length;
                    const activeCases = employeeCases.filter(c => c.status === 'In Progress' || c.status === 'Under Review').length;

                    return (
                      <Card key={employee.id} className="bg-gradient-to-br from-[#0F172A] to-[#1E293B] border-2 border-slate-700 hover:border-orange-500 transition-all">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="w-12 h-12 bg-orange-500/10 rounded-full flex items-center justify-center border border-orange-500/20">
                              <UserCheck className="w-6 h-6 text-orange-400" />
                            </div>
                            <Badge variant={employee.is_active ? "success" : "secondary"} className={employee.is_active ? "bg-green-500/10 text-green-400 border-green-500/20" : "bg-slate-700 text-slate-400"}>
                              {employee.is_active ? 'Actif' : 'Inactif'}
                            </Badge>
                          </div>
                          <h3 className="font-bold text-lg text-white mb-1">{employee.full_name}</h3>
                          <p className="text-sm text-slate-400 mb-4">{employee.email}</p>
                          <div className="space-y-2 mb-4">
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Dossiers Actifs:</span>
                              <span className="font-semibold text-white">{activeCases}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Terminés:</span>
                              <span className="font-semibold text-green-400">{completedCases}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Total Dossiers:</span>
                              <span className="font-semibold text-white">{employeeCases.length}</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Cases Tab */}
          <TabsContent value="cases">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Tous les Dossiers</CardTitle>
                <CardDescription className="text-slate-400">Vue complète de tous les dossiers d'immigration</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Recherche et Tri */}
                <SearchAndSort
                  data={cases}
                  searchFields={['client_name', 'country', 'visa_type', 'status']}
                  sortOptions={[
                    { value: 'created_at', label: 'Date de création' },
                    { value: 'client_name', label: 'Nom du client' },
                    { value: 'country', label: 'Pays' },
                    { value: 'status', label: 'Statut' },
                    { value: 'progress_percentage', label: 'Progression' }
                  ]}
                  onFilteredDataChange={setFilteredCases}
                  placeholder="Rechercher un dossier (client, pays, visa, statut)..."
                />

                <div className="space-y-4">
                  {filteredCases.map((caseItem) => (
                    <div key={caseItem.id} className="bg-[#0F172A] border border-slate-700 rounded-lg p-4 hover:border-orange-500 transition-all">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg text-white">{caseItem.client_name}</h3>
                          <p className="text-sm text-slate-400">{caseItem.country} - {caseItem.visa_type}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(caseItem.status)}>{caseItem.status}</Badge>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button variant="outline" size="sm" className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white">
                                Mise à jour
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="bg-[#1E293B] border-slate-700">
                              <DialogHeader>
                                <DialogTitle className="text-white">Mise à jour du Dossier</DialogTitle>
                                <DialogDescription className="text-slate-400">
                                  Mettre à jour le statut et la progression de {caseItem.client_name}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4">
                                <div>
                                  <Label className="text-slate-300">Étape actuelle</Label>
                                  <Select 
                                    value={caseItem.current_step_index.toString()}
                                    onValueChange={(value) => handleUpdateCase(caseItem.id, { current_step_index: parseInt(value) })}
                                  >
                                    <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="bg-[#1E293B] border-slate-600">
                                      {caseItem.workflow_steps.map((step, idx) => (
                                        <SelectItem key={idx} value={idx.toString()} className="text-white hover:bg-slate-700">
                                          Étape {idx + 1}: {step.title}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div>
                                  <Label className="text-slate-300">Statut</Label>
                                  <Select 
                                    value={caseItem.status}
                                    onValueChange={(value) => handleUpdateCase(caseItem.id, { status: value })}
                                  >
                                    <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent className="bg-[#1E293B] border-slate-600">
                                      <SelectItem value="Nouveau" className="text-white hover:bg-slate-700">Nouveau</SelectItem>
                                      <SelectItem value="En cours" className="text-white hover:bg-slate-700">En cours</SelectItem>
                                      <SelectItem value="En attente" className="text-white hover:bg-slate-700">En attente</SelectItem>
                                      <SelectItem value="Approuvé" className="text-white hover:bg-slate-700">Approuvé</SelectItem>
                                      <SelectItem value="Terminé" className="text-white hover:bg-slate-700">Terminé</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="mb-3">
                        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                          <span>Étape {caseItem.current_step_index + 1} sur {caseItem.workflow_steps.length}</span>
                          <span>{Math.round((caseItem.current_step_index + 1) / caseItem.workflow_steps.length * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-orange-500 to-orange-600 h-full transition-all"
                            style={{ width: `${((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100}%` }}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-slate-500 font-medium">Étape actuelle:</span>
                          <p className="text-slate-300">{caseItem.workflow_steps[caseItem.current_step_index]?.title}</p>
                        </div>
                        <div>
                          <span className="text-slate-500 font-medium">Créé le:</span>
                          <p className="text-slate-300">{new Date(caseItem.created_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Visitors Tab */}
          <TabsContent value="visitors">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Enregistrer un Visiteur</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Nom complet */}
                    <div>
                      <Label className="text-slate-300 font-medium">Nom complet du visiteur *</Label>
                      <Input
                        value={newVisitor.full_name}
                        onChange={(e) => setNewVisitor({ ...newVisitor, full_name: e.target.value })}
                        placeholder="Ex: Jean Dupont"
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="visitor-name-input"
                        required
                      />
                    </div>

                    {/* Numéro de téléphone */}
                    <div>
                      <Label className="text-slate-300 font-medium">Numéro de téléphone *</Label>
                      <Input
                        value={newVisitor.phone_number}
                        onChange={(e) => setNewVisitor({ ...newVisitor, phone_number: e.target.value })}
                        placeholder="+237 6XX XX XX XX"
                        type="tel"
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="visitor-phone-input"
                        required
                      />
                    </div>

                    {/* Numéro de CNI */}
                    <div>
                      <Label className="text-slate-300 font-medium">Numéro de CNI *</Label>
                      <Input
                        value={newVisitor.cni_number}
                        onChange={(e) => setNewVisitor({ ...newVisitor, cni_number: e.target.value })}
                        placeholder="Ex: 123456789"
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="visitor-cni-input"
                        required
                      />
                    </div>

                    {/* Motif */}
                    <div>
                      <Label className="text-slate-300 font-medium">Motif de la visite *</Label>
                      <Select value={newVisitor.purpose} onValueChange={(value) => setNewVisitor({ ...newVisitor, purpose: value })}>
                        <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-2">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#1E293B] border-slate-600">
                          <SelectItem value="Consultation initiale" className="text-white hover:bg-slate-700">Consultation initiale</SelectItem>
                          <SelectItem value="Suivi de dossier" className="text-white hover:bg-slate-700">Suivi de dossier</SelectItem>
                          <SelectItem value="Dépôt de documents" className="text-white hover:bg-slate-700">Dépôt de documents</SelectItem>
                          <SelectItem value="Rendez-vous" className="text-white hover:bg-slate-700">Rendez-vous</SelectItem>
                          <SelectItem value="Autre" className="text-white hover:bg-slate-700">Autre</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Other purpose (conditional) */}
                    {newVisitor.purpose === 'Autre' && (
                      <div>
                        <Label className="text-slate-300 font-medium">Précisez le motif</Label>
                        <Input
                          value={newVisitor.other_purpose}
                          onChange={(e) => setNewVisitor({ ...newVisitor, other_purpose: e.target.value })}
                          placeholder="Décrivez le motif de la visite"
                          className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        />
                      </div>
                    )}

                    <Button onClick={handleAddVisitor} className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50" data-testid="add-visitor-btn">
                      <Building2 className="w-4 h-4 mr-2" />
                      Enregistrer le Visiteur
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Liste des Visiteurs</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Recherche et Tri */}
                  <SearchAndSort
                    data={visitors}
                    searchFields={['full_name', 'phone_number', 'purpose', 'cni_number', 'registered_by']}
                    sortOptions={[
                      { value: 'arrival_time', label: 'Date d\'arrivée' },
                      { value: 'full_name', label: 'Nom' },
                      { value: 'purpose', label: 'Motif' }
                    ]}
                    onFilteredDataChange={setFilteredVisitors}
                    placeholder="Rechercher un visiteur (nom, téléphone, motif, CNI)..."
                  />

                  <div className="space-y-3">
                    {filteredVisitors.slice(0, 10).map((visitor) => (
                      <div key={visitor.id} className="flex items-center justify-between p-4 bg-[#0F172A] border border-slate-700 rounded-lg hover:border-orange-500/50 transition-all">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <p className="font-bold text-white text-lg">{visitor.full_name}</p>
                            <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                              📱 {visitor.phone_number}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-400 mb-1">
                            <span className="font-semibold">Motif:</span> {visitor.purpose}
                            {visitor.other_purpose && ` - ${visitor.other_purpose}`}
                          </p>
                          <p className="text-xs text-slate-500 mb-1">
                            <span className="font-semibold">CNI:</span> {visitor.cni_number}
                          </p>
                          <p className="text-xs text-slate-500">
                            <span className="font-semibold">Arrivée:</span> {new Date(visitor.arrival_time).toLocaleString('fr-FR')}
                          </p>
                          {visitor.registered_by && (
                            <p className="text-xs text-slate-600 mt-1">
                              Enregistré par: {visitor.registered_by}
                            </p>
                          )}
                        </div>
                        <div className="ml-4">
                          {!visitor.departure_time && (
                            <Button variant="outline" size="sm" onClick={() => handleCheckoutVisitor(visitor.id)} className="border-slate-600 text-slate-300 hover:bg-orange-500 hover:text-white hover:border-orange-500">
                              Départ
                            </Button>
                          )}
                          {visitor.departure_time && (
                            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                              ✓ Parti
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Prospects Tab */}
          <TabsContent value="prospects">
            <MyProspects />
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Pending Payments */}
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <span className="text-orange-500">💰</span>
                    <span>Paiements En Attente</span>
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Validez ou rejetez les déclarations de paiement des clients
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {pendingPayments.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-3">✅</div>
                      <p className="text-slate-400">Aucun paiement en attente</p>
                      <p className="text-slate-500 text-sm">Tous les paiements ont été traités</p>
                    </div>
                  ) : (
                    <>
                      {/* Recherche et Tri */}
                      <SearchAndSort
                        data={pendingPayments}
                        searchFields={['client_name', 'payment_method', 'description']}
                        sortOptions={[
                          { value: 'declared_at', label: 'Date de déclaration' },
                          { value: 'client_name', label: 'Nom du client' },
                          { value: 'amount', label: 'Montant' }
                        ]}
                        onFilteredDataChange={setFilteredPayments}
                        placeholder="Rechercher un paiement (client, méthode, description)..."
                      />

                      <div className="space-y-4 max-h-96 overflow-y-auto">
                        {filteredPayments.map((payment) => (
                        <div key={payment.id} className="bg-slate-600 rounded-lg p-4 border border-slate-500 space-y-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-white font-semibold text-lg">
                                {payment.amount} {payment.currency}
                              </p>
                              <p className="text-slate-300 text-sm">{payment.client_name}</p>
                            </div>
                            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                              ⏳ En attente
                            </Badge>
                          </div>
                          
                          <div className="space-y-1 text-sm">
                            <p className="text-slate-400">
                              <span className="font-medium text-slate-300">Méthode:</span> {payment.payment_method}
                            </p>
                            {payment.reference && (
                              <p className="text-slate-400">
                                <span className="font-medium text-slate-300">Référence:</span> {payment.reference}
                              </p>
                            )}
                            {payment.description && (
                              <p className="text-slate-400">
                                <span className="font-medium text-slate-300">Description:</span> {payment.description}
                              </p>
                            )}
                            <p className="text-slate-400">
                              <span className="font-medium text-slate-300">Déclaré le:</span> {new Date(payment.declared_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>

                          <div className="flex gap-2">
                            <Button
                              onClick={() => handlePaymentAction(payment, 'CONFIRMED')}
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                              size="sm"
                            >
                              ✅ Confirmer
                            </Button>
                            <Button
                              onClick={() => handlePaymentAction(payment, 'REJECTED')}
                              className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                              size="sm"
                            >
                              ❌ Rejeter
                            </Button>
                          </div>
                        </div>
                      ))}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <span className="text-green-500">📋</span>
                    <span>Historique des Paiements</span>
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Paiements confirmés ou rejetés
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {paymentHistory.length === 0 ? (
                      <div className="text-center py-8">
                        <div className="text-4xl mb-3">📋</div>
                        <p className="text-slate-400">Aucun historique</p>
                        <p className="text-slate-500 text-sm">Les paiements traités apparaîtront ici</p>
                      </div>
                    ) : (
                      paymentHistory.map((payment) => (
                        <div key={payment.id} className="bg-slate-600 rounded-lg p-3 border border-slate-500">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="text-white font-medium">
                                {payment.amount} {payment.currency}
                              </p>
                              <p className="text-slate-300 text-sm">{payment.client_name}</p>
                            </div>
                            <Badge className={
                              payment.status === 'confirmed' || payment.status === 'CONFIRMED'
                                ? 'bg-green-500/20 text-green-400 border-green-500/30'
                                : payment.status === 'rejected' || payment.status === 'REJECTED'
                                ? 'bg-red-500/20 text-red-400 border-red-500/30'
                                : 'bg-orange-500/20 text-orange-400 border-orange-500/30'
                            }>
                              {payment.status === 'confirmed' || payment.status === 'CONFIRMED' 
                                ? '✅ Confirmé' 
                                : payment.status === 'rejected' || payment.status === 'REJECTED'
                                ? '❌ Rejeté'
                                : '⏳ En attente'}
                            </Badge>
                          </div>
                          <p className="text-xs text-slate-400">
                            {new Date(payment.confirmed_at || payment.declared_at).toLocaleString('fr-FR')}
                          </p>
                          {payment.invoice_number && (
                            <p className="text-xs text-slate-400 mt-1">
                              <span className="font-medium">Facture:</span> {payment.invoice_number}
                            </p>
                          )}
                          {/* Bouton télécharger facture */}
                          {payment.status === 'CONFIRMED' && payment.invoice_number && (
                            <button
                              onClick={() => downloadInvoice(payment.id, payment.invoice_number)}
                              className="mt-2 w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-2 py-1 rounded text-xs transition-colors"
                            >
                              <Download className="w-3 h-3" />
                              Télécharger facture
                            </button>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Withdrawals Tab */}
          <TabsContent value="withdrawals">
            <WithdrawalManager />
          </TabsContent>
        </Tabs>
      </div>
      )}

      {/* Chat Widget */}
      <ChatWidget userRole="MANAGER" />

      {/* Rejection Dialog */}
      {rejectionDialog.show && (
        <Dialog open={rejectionDialog.show} onOpenChange={(open) => setRejectionDialog({ ...rejectionDialog, show: open })}>
          <DialogContent className="bg-[#1E293B] border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Rejeter le Paiement</DialogTitle>
              <DialogDescription className="text-slate-400">
                Veuillez indiquer la raison du rejet
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label className="text-slate-300">Raison du rejet *</Label>
                <Input
                  value={rejectionDialog.reason}
                  onChange={(e) => setRejectionDialog({ ...rejectionDialog, reason: e.target.value })}
                  placeholder="Ex: Montant incorrect, preuve de paiement invalide..."
                  className="bg-slate-800 border-slate-600 text-white mt-2"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleRejection}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Confirmer le Rejet
                </Button>
                <Button
                  onClick={() => setRejectionDialog({ show: false, payment: null, reason: '' })}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800"
                >
                  Annuler
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Confirmation Dialog */}
      {confirmationDialog.show && (
        <Dialog open={confirmationDialog.show} onOpenChange={(open) => setConfirmationDialog({ ...confirmationDialog, show: open })}>
          <DialogContent className="bg-[#1E293B] border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Confirmer le Paiement</DialogTitle>
              <DialogDescription className="text-slate-400">
                Saisissez le code de confirmation pour valider le paiement
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="bg-blue-500/10 border border-blue-500/30 p-3 rounded-lg">
                <p className="text-blue-400 text-sm font-medium">
                  Code généré: <span className="font-mono text-lg">{confirmationDialog.generatedCode}</span>
                </p>
                <p className="text-blue-300 text-xs mt-1">
                  Veuillez saisir ce code ci-dessous pour confirmer
                </p>
              </div>
              <div>
                <Label className="text-slate-300">Code de confirmation *</Label>
                <Input
                  value={confirmationDialog.code}
                  onChange={(e) => setConfirmationDialog({ ...confirmationDialog, code: e.target.value })}
                  placeholder="Saisissez le code de confirmation"
                  className="bg-slate-800 border-slate-600 text-white mt-2"
                  autoFocus
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleConfirmWithCode}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                  disabled={!confirmationDialog.code?.trim()}
                >
                  ✅ Confirmer le Paiement
                </Button>
                <Button
                  onClick={() => setConfirmationDialog({ show: false, payment: null, code: '', generatedCode: '' })}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800"
                >
                  Annuler
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Reassign Client Dialog */}
      {reassignDialog.show && (
        <Dialog open={reassignDialog.show} onOpenChange={(open) => setReassignDialog({ ...reassignDialog, show: open })}>
          <DialogContent className="bg-[#1E293B] border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Réassigner le Client</DialogTitle>
              <DialogDescription className="text-slate-400">
                Sélectionnez le nouvel employé pour {reassignDialog.client?.client_name}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              {employees.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-slate-400">Chargement de la liste des employés...</p>
                </div>
              ) : (
                <>
                  <div>
                    <Label className="text-slate-300">Nouvel Employé * ({employees.length} disponibles)</Label>
                    <select
                      value={reassignDialog.newEmployeeId}
                      onChange={(e) => setReassignDialog({ ...reassignDialog, newEmployeeId: e.target.value })}
                      className="w-full mt-2 px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      <option value="">Choisir un employé</option>
                      {employees.map((emp) => (
                        <option key={emp.id} value={emp.id}>
                          {emp.full_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleReassignClient}
                      className="flex-1 bg-orange-500 hover:bg-orange-600 text-white"
                      disabled={!reassignDialog.newEmployeeId}
                    >
                      Réassigner
                    </Button>
                    <Button
                      onClick={() => setReassignDialog({ show: false, client: null, newEmployeeId: '' })}
                      variant="outline"
                      className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800"
                    >
                      Annuler
                    </Button>
                  </div>
                </>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Popup Credentials Uniforme */}
      <CredentialsPopup
        open={showCredentialsDialog}
        onOpenChange={(open) => {
          setShowCredentialsDialog(open);
          if (!open) setNewClientCredentials(null);
        }}
        credentials={newClientCredentials}
      />

      {/* Dialog Créer un Employé */}
      <Dialog open={showCreateEmployee} onOpenChange={setShowCreateEmployee}>
        <DialogContent className="bg-[#1E293B] border-slate-700 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-white">Créer un Nouvel Employé</DialogTitle>
            <DialogDescription className="text-slate-400">
              Ajoutez un nouveau conseiller à votre équipe
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateEmployee} className="space-y-4">
            <div>
              <Label className="text-slate-300">Nom Complet *</Label>
              <Input
                value={newEmployee.full_name}
                onChange={(e) => setNewEmployee({ ...newEmployee, full_name: e.target.value })}
                required
                placeholder="Ex: Marie Kouassi"
                className="bg-slate-800 border-slate-600 text-white"
              />
            </div>
            
            <div>
              <Label className="text-slate-300">Email *</Label>
              <Input
                type="email"
                value={newEmployee.email}
                onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                required
                placeholder="email@example.com"
                className="bg-slate-800 border-slate-600 text-white"
              />
            </div>
            
            <div>
              <Label className="text-slate-300">Téléphone *</Label>
              <Input
                value={newEmployee.phone}
                onChange={(e) => setNewEmployee({ ...newEmployee, phone: e.target.value })}
                required
                placeholder="+237 XXX XXX XXX"
                className="bg-slate-800 border-slate-600 text-white"
              />
            </div>
            
            <div className="bg-green-500/10 border border-green-500/30 p-3 rounded-lg">
              <p className="text-green-400 text-sm">
                ℹ️ Un compte employé sera créé avec un mot de passe temporaire qui sera affiché après la création.
              </p>
            </div>
            
            <Button 
              type="submit" 
              className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white"
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Créer l'Employé
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Dialog Détails Client */}
      {selectedClient && (
        <Dialog open={!!selectedClient} onOpenChange={() => setSelectedClient(null)}>
          <DialogContent className="bg-[#1E293B] border-slate-700 max-w-3xl">
            <DialogHeader>
              <DialogTitle className="text-white flex items-center gap-2">
                <User className="w-6 h-6 text-blue-500" />
                Détails du Client
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-6 mt-4">
              {/* Informations de base */}
              <div className="bg-slate-800 p-4 rounded-lg space-y-3">
                <h4 className="text-white font-semibold mb-3">📋 Informations Personnelles</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-slate-400 text-sm">Nom complet</p>
                    <p className="text-white font-medium">{selectedClient.full_name}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Email</p>
                    <p className="text-white">{selectedClient.email}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Téléphone</p>
                    <p className="text-white">{selectedClient.phone || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Statut</p>
                    <Badge className={selectedClient.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'}>
                      {selectedClient.status === 'active' ? 'Actif' : selectedClient.status}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Informations du dossier */}
              <div className="bg-slate-800 p-4 rounded-lg space-y-3">
                <h4 className="text-white font-semibold mb-3">🗂️ Dossier d'Immigration</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-slate-400 text-sm">Pays de destination</p>
                    <p className="text-white font-medium">{selectedClient.country}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Type de visa</p>
                    <p className="text-white">{selectedClient.visa_type}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Employé assigné</p>
                    <p className="text-white">{selectedClient.assigned_employee_name || 'Non assigné'}</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-sm">Date de création</p>
                    <p className="text-white">
                      {selectedClient.created_at ? new Date(selectedClient.created_at).toLocaleDateString('fr-FR') : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Identifiants de connexion */}
              <div className="bg-blue-500/10 border border-blue-500/30 p-4 rounded-lg">
                <h4 className="text-blue-400 font-semibold mb-3">🔑 Identifiants de Connexion</h4>
                <div className="space-y-2">
                  <div>
                    <p className="text-slate-400 text-sm">Email de connexion</p>
                    <div className="flex items-center gap-2">
                      <code className="text-white bg-slate-900 px-3 py-1 rounded font-mono text-sm flex-1">
                        {selectedClient.email}
                      </code>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-slate-600"
                        onClick={() => {
                          navigator.clipboard.writeText(selectedClient.email);
                          toast.success('Email copié!');
                        }}
                      >
                        Copier
                      </Button>
                    </div>
                  </div>
                  <div className="text-slate-400 text-xs mt-2">
                    ℹ️ Le mot de passe temporaire a été envoyé par email lors de la création du compte
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  onClick={() => setSelectedClient(null)}
                  className="bg-slate-600 hover:bg-slate-500"
                >
                  Fermer
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
