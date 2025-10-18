import { useState, useEffect, useContext } from 'react';
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
import { dashboardAPI, clientsAPI, casesAPI, employeesAPI, visitorsAPI } from '../utils/api';
import api from '../utils/api';
import { Globe, LogOut, Users, FileText, TrendingUp, CheckCircle, Clock, AlertCircle, UserCheck, Building2, Search, Filter, Plus, UserPlus, MessageCircle, User, Lock, Wallet } from 'lucide-react';
import WithdrawalManager from '../components/WithdrawalManager';
import MyProspects from '../components/MyProspects';
import ChatWidget from '../components/ChatWidget';
import NotificationBell from '../components/NotificationBell';
import SearchAndSort from '../components/SearchAndSort';
import useSocket from '../hooks/useSocket';

export default function ManagerDashboard() {
  const { user, logout } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [clients, setClients] = useState([]);
  const [cases, setCases] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [visitors, setVisitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newVisitor, setNewVisitor] = useState({ 
    full_name: '', 
    phone_number: '', 
    purpose: 'Consultation initiale',
    other_purpose: '',
    cni_number: '' 
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCountry, setFilterCountry] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [newClient, setNewClient] = useState({
    email: '',
    full_name: '',
    phone: '',
    country: '',
    visa_type: '',
    message: ''
  });
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeSearchTab, setActiveSearchTab] = useState('clients');
  const [pendingPayments, setPendingPayments] = useState([]);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [confirmationDialog, setConfirmationDialog] = useState({
    show: false,
    payment: null,
    code: '',
    action: ''
  });
  const [rejectionDialog, setRejectionDialog] = useState({
    show: false,
    payment: null,
    reason: ''
  });
  
  // WebSocket hook
  const { connected } = useSocket(localStorage.getItem('token'));

  useEffect(() => {
    fetchData();
    fetchPayments();
    
    // Auto-refresh des données toutes les 30 minutes (sans perdre le travail en cours)
    const refreshInterval = setInterval(() => {
      // Refresh silencieux sans recharger toute la page
      fetchData();
      fetchPayments();
    }, 1800000); // 30 minutes
    
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

  const performIntelligentSearch = async (query, category = 'all') => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/global?q=${encodeURIComponent(query)}&category=${category}&limit=10`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Erreur lors de la recherche');
    } finally {
      setIsSearching(false);
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

        if (response.ok) {
          const result = await response.json();
          if (result.confirmation_code) {
            // Code généré, demander la confirmation
            setConfirmationDialog({ 
              show: true, 
              payment: result, 
              code: '', 
              action: 'CONFIRMED',
              generatedCode: result.confirmation_code
            });
          }
        } else {
          throw new Error('Erreur lors de la génération du code de confirmation');
        }
      } catch (error) {
        toast.error(error.message);
        console.error('Error generating confirmation code:', error);
      }
    }
  };

  const confirmPaymentWithCode = async () => {
    try {
      console.log('=== DEBUGGING PAYMENT CONFIRMATION ===');
      console.log('Payment ID:', confirmationDialog.payment.id);
      console.log('Confirmation code:', confirmationDialog.code);
      console.log('Generated code:', confirmationDialog.generatedCode);
      
      const requestBody = { 
        action: 'CONFIRMED',
        confirmation_code: confirmationDialog.code
      };
      console.log('Request body:', requestBody);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/${confirmationDialog.payment.id}/confirm`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestBody)
      });

      console.log('Response status:', response.status);
      const responseData = await response.json();
      console.log('Response data:', responseData);

      if (response.ok) {
        toast.success('Paiement confirmé avec succès ! Facture générée automatiquement.');
        setConfirmationDialog({ show: false, payment: null, code: '', action: '' });
        fetchPayments(); // Refresh unique
      } else {
        throw new Error(responseData.detail || 'Code de confirmation incorrect');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error confirming payment:', error);
    }
  };

  const rejectPaymentWithReason = async () => {
    if (!rejectionDialog.reason.trim()) {
      toast.error('Un motif de rejet est obligatoire');
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

      if (response.ok) {
        toast.success('Paiement rejeté. Le client a été notifié.');
        setRejectionDialog({ show: false, payment: null, reason: '' });
        fetchPayments(); // Refresh unique
      } else {
        throw new Error('Erreur lors du rejet du paiement');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error rejecting payment:', error);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Les nouveaux mots de passe ne correspondent pas');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Le nouveau mot de passe doit contenir au moins 8 caractères');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/change-password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        })
      });

      if (response.ok) {
        toast.success('Mot de passe modifié avec succès !');
        setPasswordForm({
          old_password: '',
          new_password: '',
          confirm_password: ''
        });
        setShowPasswordDialog(false);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors du changement de mot de passe');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error changing password:', error);
    }
  };

  const handleReassignClient = async (clientId, employeeId) => {
    try {
      await clientsAPI.reassign(clientId, employeeId);
      toast.success('Client reassigned successfully');
      fetchData(); // Refresh unique
      setSelectedClient(null);
    } catch (error) {
      toast.error('Failed to reassign client');
    }
  };

  const handleCreateClient = async () => {
    try {
      const response = await clientsAPI.create(newClient);
      const clientData = response.data;
      
      // Show login credentials if new account was created
      if (clientData.default_password) {
        toast.success(
          <div>
            <p className="font-bold">Client créé avec succès!</p>
            <p>Email: {clientData.login_email}</p>
            <p>Mot de passe: {clientData.default_password}</p>
            <p className="text-xs text-slate-400 mt-1">Le client doit changer ce mot de passe lors de sa première connexion</p>
          </div>,
          { duration: 8000 }
        );
      } else {
        toast.success('Client créé avec succès (compte existant utilisé)');
      }
      
      setNewClient({
        email: '',
        full_name: '',
        phone: '',
        country: '',
        visa_type: '',
        message: ''
      });
      setShowCreateClient(false);
      // Refresh uniquement les données sans perdre l'interface
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la création du client');
    }
  };

  const handleShowClientCredentials = async (clientId) => {
    try {
      const response = await api.get(`/clients/${clientId}/credentials`);
      const credentials = response.data;
      
      toast.info(
        <div>
          <p className="font-bold">Informations de connexion client:</p>
          <p>Email: {credentials.email}</p>
          <p>Mot de passe par défaut: {credentials.password}</p>
          <p className="text-xs text-slate-400 mt-1">Le client peut changer son mot de passe dans son profil</p>
        </div>,
        { duration: 10000 }
      );
    } catch (error) {
      toast.error('Erreur lors de la récupération des informations de connexion');
    }
  };

  const handleUpdateCase = async (caseId, updateData) => {
    try {
      await casesAPI.update(caseId, updateData);
      toast.success('Dossier mis à jour avec succès');
      fetchData(); // Refresh data
    } catch (error) {
      toast.error('Erreur lors de la mise à jour du dossier');
    }
  };

  const handleAddVisitor = async () => {
    // Validation
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
      fetchData();
    } catch (error) {
      console.error('Erreur enregistrement visiteur:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement du visiteur');
    }
  };

  const handleCheckoutVisitor = async (visitorId) => {
    try {
      await visitorsAPI.checkout(visitorId);
      toast.success('Visitor checked out');
      fetchData();
    } catch (error) {
      toast.error('Failed to checkout visitor');
    }
  };

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.client_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          client.assigned_employee_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCountry = filterCountry === 'all' || client.country === filterCountry;
    const matchesStatus = filterStatus === 'all' || client.current_status === filterStatus;
    return matchesSearch && matchesCountry && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'new': return 'bg-blue-100 text-blue-700';
      case 'in progress': return 'bg-yellow-100 text-yellow-700';
      case 'approved': case 'completed': return 'bg-green-100 text-green-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
      {/* Header */}
      <header className="bg-[#1E293B] border-b border-slate-700/50 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <Globe className="w-6 h-6 sm:w-8 sm:h-8 text-orange-500" />
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-white">
                  <span className="hidden sm:inline">ALORIA AGENCY</span>
                  <span className="sm:hidden">ALORIA</span>
                </h1>
                <p className="text-xs sm:text-sm text-slate-400">
                  <span className="hidden xs:inline">Tableau de Bord Gestionnaire</span>
                  <span className="xs:hidden">Manager</span>
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4">
              <NotificationBell currentUser={user} />
              <div className="hidden md:block text-right">
                <p className="text-sm font-medium text-white">{user.full_name}</p>
                <p className="text-xs text-slate-400">{user.role}</p>
              </div>
              
              {/* Profile Button - Responsive */}
              <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-xs sm:text-sm px-2 sm:px-4 py-1.5 sm:py-2 touch-manipulation"
                  >
                    <User className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                    <span className="hidden xs:inline">Profil</span>
                    <span className="xs:hidden">👤</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-800 border-slate-600 text-white">
                  <DialogHeader>
                    <DialogTitle className="flex items-center space-x-2">
                      <Lock className="w-5 h-5 text-orange-500" />
                      <span>Changer le Mot de Passe</span>
                    </DialogTitle>
                    <DialogDescription className="text-slate-400">
                      Modifiez votre mot de passe pour sécuriser votre compte
                    </DialogDescription>
                  </DialogHeader>
                  
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                      <Label htmlFor="old_password" className="text-slate-300">Mot de passe actuel</Label>
                      <Input
                        id="old_password"
                        type="password"
                        value={passwordForm.old_password}
                        onChange={(e) => setPasswordForm({...passwordForm, old_password: e.target.value})}
                        placeholder="Entrez votre mot de passe actuel"
                        required
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="new_password" className="text-slate-300">Nouveau mot de passe</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={passwordForm.new_password}
                        onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                        placeholder="Entrez un nouveau mot de passe (min. 8 caractères)"
                        required
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="confirm_password" className="text-slate-300">Confirmer le nouveau mot de passe</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={passwordForm.confirm_password}
                        onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                        placeholder="Confirmez votre nouveau mot de passe"
                        required
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowPasswordDialog(false)}
                        className="border-slate-600 text-slate-300"
                      >
                        Annuler
                      </Button>
                      <Button
                        type="submit"
                        className="bg-orange-600 hover:bg-orange-700 text-white"
                      >
                        <Lock className="w-4 h-4 mr-2" />
                        Modifier
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
              
              {/* Logout Button - Responsive */}
              <Button 
                variant="outline" 
                onClick={logout} 
                className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-xs sm:text-sm px-2 sm:px-4 py-1.5 sm:py-2 touch-manipulation"
              >
                <LogOut className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                <span className="hidden xs:inline">Déconnexion</span>
                <span className="xs:hidden">Exit</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-blue-500 border-slate-700" data-testid="kpi-total-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Total Dossiers</p>
                  <p className="text-3xl font-bold text-white">{stats?.total_cases || 0}</p>
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
                  <p className="text-3xl font-bold text-white">{stats?.active_cases || 0}</p>
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
                  <p className="text-3xl font-bold text-white">{stats?.completed_cases || 0}</p>
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
                  <p className="text-3xl font-bold text-white">{stats?.total_clients || 0}</p>
                </div>
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center border border-orange-500/20">
                  <Users className="w-6 h-6 text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Cases by Country */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Dossiers par Pays</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.cases_by_country && Object.entries(stats.cases_by_country).map(([country, count]) => (
                  <div key={country} className="flex items-center justify-between">
                    <span className="text-slate-300 font-medium">{country}</span>
                    <div className="flex items-center space-x-3">
                      <div className="w-32 bg-slate-700 rounded-full h-2">
                        <div
                          className="bg-orange-500 h-2 rounded-full"
                          style={{ width: `${(count / stats.total_cases) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-white font-semibold w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Dossiers par Statut</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats?.cases_by_status && Object.entries(stats.cases_by_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <Badge className={getStatusColor(status)}>{status}</Badge>
                    <span className="text-white font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="clients" className="w-full">
          <TabsList className="grid w-full grid-cols-7 mb-6 bg-[#1E293B] border border-slate-700">
            <TabsTrigger value="clients" data-testid="tab-clients" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Clients</TabsTrigger>
            <TabsTrigger value="employees" data-testid="tab-employees" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Employés</TabsTrigger>
            <TabsTrigger value="prospects" data-testid="tab-prospects" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Prospects</TabsTrigger>
            <TabsTrigger value="cases" data-testid="tab-cases" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Dossiers</TabsTrigger>
            <TabsTrigger value="payments" data-testid="tab-payments" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Paiements</TabsTrigger>
            <TabsTrigger value="withdrawals" data-testid="tab-withdrawals" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Retraits</TabsTrigger>
            <TabsTrigger value="visitors" data-testid="tab-visitors" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Visiteurs</TabsTrigger>
          </TabsList>

          {/* Clients Tab */}
          <TabsContent value="clients">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-white">Tous les Clients</CardTitle>
                    <CardDescription className="text-slate-400">Gérer et surveiller les dossiers clients</CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <Dialog open={showCreateClient} onOpenChange={setShowCreateClient}>
                      <DialogTrigger asChild>
                        <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                          <UserPlus className="w-4 h-4 mr-2" />
                          Nouveau Client
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-[#1E293B] border-slate-700 max-w-lg">
                        <DialogHeader>
                          <DialogTitle className="text-white">Créer un Nouveau Client</DialogTitle>
                          <DialogDescription className="text-slate-400">
                            Remplissez les informations du client pour créer son dossier
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label className="text-slate-300">Nom Complet</Label>
                            <Input
                              value={newClient.full_name}
                              onChange={(e) => setNewClient({...newClient, full_name: e.target.value})}
                              className="bg-[#0F172A] border-slate-600 text-white"
                              placeholder="Nom complet du client"
                            />
                          </div>
                          <div>
                            <Label className="text-slate-300">Email</Label>
                            <Input
                              type="email"
                              value={newClient.email}
                              onChange={(e) => setNewClient({...newClient, email: e.target.value})}
                              className="bg-[#0F172A] border-slate-600 text-white"
                              placeholder="email@example.com"
                            />
                          </div>
                          <div>
                            <Label className="text-slate-300">Téléphone</Label>
                            <Input
                              value={newClient.phone}
                              onChange={(e) => setNewClient({...newClient, phone: e.target.value})}
                              className="bg-[#0F172A] border-slate-600 text-white"
                              placeholder="+33 1 23 45 67 89"
                            />
                          </div>
                          <div>
                            <Label className="text-slate-300">Pays de Destination</Label>
                            <Select value={newClient.country} onValueChange={(value) => setNewClient({...newClient, country: value})}>
                              <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                                <SelectValue placeholder="Sélectionner un pays" />
                              </SelectTrigger>
                              <SelectContent className="bg-[#1E293B] border-slate-600">
                                <SelectItem value="Canada" className="text-white hover:bg-slate-700">Canada</SelectItem>
                                <SelectItem value="France" className="text-white hover:bg-slate-700">France</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label className="text-slate-300">Type de Visa</Label>
                            <Select value={newClient.visa_type} onValueChange={(value) => setNewClient({...newClient, visa_type: value})}>
                              <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                                <SelectValue placeholder="Sélectionner le type de visa" />
                              </SelectTrigger>
                              <SelectContent className="bg-[#1E293B] border-slate-600">
                                {newClient.country === 'Canada' && (
                                  <>
                                    <SelectItem value="Work Permit" className="text-white hover:bg-slate-700">Permis de Travail</SelectItem>
                                    <SelectItem value="Study Permit" className="text-white hover:bg-slate-700">Permis d'Études</SelectItem>
                                    <SelectItem value="Permanent Residence (Express Entry)" className="text-white hover:bg-slate-700">Résidence Permanente</SelectItem>
                                  </>
                                )}
                                {newClient.country === 'France' && (
                                  <>
                                    <SelectItem value="Work Permit (Talent Permit)" className="text-white hover:bg-slate-700">Permis Talent</SelectItem>
                                    <SelectItem value="Student Visa" className="text-white hover:bg-slate-700">Visa Étudiant</SelectItem>
                                    <SelectItem value="Family Reunification" className="text-white hover:bg-slate-700">Regroupement Familial</SelectItem>
                                  </>
                                )}
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label className="text-slate-300">Message Initial (Optionnel)</Label>
                            <Input
                              value={newClient.message}
                              onChange={(e) => setNewClient({...newClient, message: e.target.value})}
                              className="bg-[#0F172A] border-slate-600 text-white"
                              placeholder="Note ou demande spécifique..."
                            />
                          </div>
                          <div className="flex space-x-2">
                            <Button 
                              onClick={handleCreateClient}
                              className="flex-1 bg-orange-500 hover:bg-orange-600 text-white"
                            >
                              Créer le Client
                            </Button>
                            <Button 
                              variant="outline" 
                              onClick={() => setShowCreateClient(false)}
                              className="border-slate-600 text-slate-300 hover:bg-slate-800"
                            >
                              Annuler
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                    
                    <div className="relative">
                      <Input
                        placeholder="Recherche intelligente (clients, dossiers, employés...)"
                        value={searchTerm}
                        onChange={(e) => {
                          setSearchTerm(e.target.value);
                          performIntelligentSearch(e.target.value, activeSearchTab);
                        }}
                        className="w-80 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 pr-10"
                        data-testid="search-clients-input"
                      />
                      <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      
                      {/* Search Results Dropdown */}
                      {(searchTerm && searchResults.length > 0) && (
                        <div className="absolute top-full left-0 right-0 bg-slate-800 border border-slate-600 rounded-lg shadow-lg z-50 mt-1">
                          <div className="p-3 border-b border-slate-600">
                            <div className="flex space-x-2 text-xs">
                              {['clients', 'cases', 'users', 'visitors'].map((tab) => (
                                <button
                                  key={tab}
                                  onClick={() => {
                                    setActiveSearchTab(tab);
                                    performIntelligentSearch(searchTerm, tab);
                                  }}
                                  className={`px-3 py-1 rounded ${
                                    activeSearchTab === tab 
                                      ? 'bg-orange-600 text-white' 
                                      : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                                  }`}
                                >
                                  {tab === 'clients' ? 'Clients' :
                                   tab === 'cases' ? 'Dossiers' :
                                   tab === 'users' ? 'Utilisateurs' : 'Visiteurs'}
                                </button>
                              ))}
                            </div>
                          </div>
                          <div className="max-h-64 overflow-y-auto">
                            {searchResults.map((result, index) => (
                              <div 
                                key={index}
                                className="p-3 hover:bg-slate-700 cursor-pointer border-b border-slate-700 last:border-b-0"
                                onClick={() => {
                                  // Handle result click based on type
                                  setSearchTerm('');
                                  setSearchResults([]);
                                  toast.success(`Sélectionné: ${result.title}`);
                                }}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <p className="text-white font-medium">{result.title}</p>
                                    <p className="text-slate-400 text-sm">{result.description}</p>
                                  </div>
                                  <Badge className={`${
                                    result.category === 'clients' ? 'bg-blue-500/20 text-blue-400' :
                                    result.category === 'cases' ? 'bg-green-500/20 text-green-400' :
                                    result.category === 'users' ? 'bg-purple-500/20 text-purple-400' :
                                    'bg-orange-500/20 text-orange-400'
                                  }`}>
                                    {result.category}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                          {isSearching && (
                            <div className="p-4 text-center text-slate-400">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500 mx-auto"></div>
                              <span className="ml-2">Recherche...</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <Select value={filterCountry} onValueChange={setFilterCountry}>
                      <SelectTrigger className="w-32 bg-[#0F172A] border-slate-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1E293B] border-slate-600">
                        <SelectItem value="all" className="text-white hover:bg-slate-700">Tous les Pays</SelectItem>
                        <SelectItem value="Canada" className="text-white hover:bg-slate-700">Canada</SelectItem>
                        <SelectItem value="France" className="text-white hover:bg-slate-700">France</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b border-slate-700">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Nom Client</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Pays</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Type de Visa</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Statut</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Progrès</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Conseiller</th>
                        <th className="text-left py-3 px-4 font-semibold text-slate-300">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredClients.map((client) => {
                        const clientCase = cases.find(c => c.client_id === client.id);
                        return (
                          <tr key={client.id} className="border-b border-slate-700/50 hover:bg-slate-800/30">
                            <td className="py-3 px-4 text-white">{clientCase?.client_name || 'N/A'}</td>
                            <td className="py-3 px-4">
                              <Badge variant="outline" className="border-slate-600 text-slate-300">{client.country}</Badge>
                            </td>
                            <td className="py-3 px-4 text-sm text-slate-300">{client.visa_type}</td>
                            <td className="py-3 px-4">
                              <Badge className={getStatusColor(client.current_status)}>
                                {client.current_status}
                              </Badge>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-2">
                                <div className="w-20 bg-slate-700 rounded-full h-2">
                                  <div
                                    className="bg-orange-500 h-2 rounded-full"
                                    style={{ width: `${client.progress_percentage}%` }}
                                  ></div>
                                </div>
                                <span className="text-xs text-slate-400">{Math.round(client.progress_percentage)}%</span>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-sm text-slate-300">{client.assigned_employee_name || 'Non assigné'}</td>
                            <td className="py-3 px-4">
                              <div className="flex space-x-2">
                                <Button 
                                  variant="outline" 
                                  size="sm" 
                                  onClick={() => handleShowClientCredentials(client.id)}
                                  className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white"
                                >
                                  Login Info
                                </Button>
                                <Dialog>
                                  <DialogTrigger asChild>
                                    <Button variant="outline" size="sm" onClick={() => setSelectedClient(client)} className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white">
                                      Réassigner
                                    </Button>
                                  </DialogTrigger>
                                <DialogContent className="bg-[#1E293B] border-slate-700">
                                  <DialogHeader>
                                    <DialogTitle className="text-white">Réassigner le Client</DialogTitle>
                                    <DialogDescription className="text-slate-400">
                                      Sélectionner un nouveau conseiller pour {clientCase?.client_name}
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="space-y-4">
                                    <Label className="text-slate-300">Sélectionner l'Employé</Label>
                                    <Select onValueChange={(value) => handleReassignClient(client.id, value)}>
                                      <SelectTrigger className="bg-[#0F172A] border-slate-600 text-white">
                                        <SelectValue placeholder="Choisir un employé" />
                                      </SelectTrigger>
                                      <SelectContent className="bg-[#1E293B] border-slate-600">
                                        {employees.map((emp) => (
                                          <SelectItem key={emp.id} value={emp.id} className="text-white hover:bg-slate-700">
                                            {emp.full_name}
                                          </SelectItem>
                                        ))}
                                      </SelectContent>
                                    </Select>
                                  </div>
                                </DialogContent>
                              </Dialog>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Employees Tab */}
          <TabsContent value="employees">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Membres de l'Équipe</CardTitle>
                <CardDescription className="text-slate-400">Voir et gérer vos conseillers en immigration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {employees.map((employee) => {
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
                <div className="space-y-4">
                  {cases.map((caseItem) => (
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
                                      <SelectItem value="Rejeté" className="text-white hover:bg-slate-700">Rejeté</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </div>
                      <div className="mb-3">
                        <div className="flex justify-between text-sm text-slate-400 mb-1">
                          <span>Étape {caseItem.current_step_index + 1} sur {caseItem.workflow_steps.length}</span>
                          <span>{Math.round(((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-orange-500 h-2 rounded-full transition-all"
                            style={{ width: `${((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <p className="text-sm text-slate-300">
                        <strong>Étape Actuelle:</strong> {caseItem.workflow_steps[caseItem.current_step_index]?.title || 'N/A'}
                      </p>
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
                        <SelectContent className="bg-slate-800 border-slate-600">
                          <SelectItem value="Consultation initiale" className="text-white hover:bg-slate-700">Consultation initiale</SelectItem>
                          <SelectItem value="Remise de documents" className="text-white hover:bg-slate-700">Remise de documents</SelectItem>
                          <SelectItem value="Mise à jour du dossier" className="text-white hover:bg-slate-700">Mise à jour du dossier</SelectItem>
                          <SelectItem value="Rendez-vous de suivi" className="text-white hover:bg-slate-700">Rendez-vous de suivi</SelectItem>
                          <SelectItem value="Autre" className="text-white hover:bg-slate-700">Autre</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Précisions si Autre */}
                    {newVisitor.purpose === 'Autre' && (
                      <div>
                        <Label className="text-slate-300 font-medium">Précisez le motif</Label>
                        <Input
                          value={newVisitor.other_purpose}
                          onChange={(e) => setNewVisitor({ ...newVisitor, other_purpose: e.target.value })}
                          placeholder="Veuillez préciser..."
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
                  <CardTitle className="text-white">Visiteurs d'Aujourd'hui</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {visitors.slice(0, 10).map((visitor) => (
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
                            <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                              ✅ Parti
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
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {pendingPayments.length === 0 ? (
                      <div className="text-center py-8">
                        <div className="text-4xl mb-3">✅</div>
                        <p className="text-slate-400">Aucun paiement en attente</p>
                        <p className="text-slate-500 text-sm">Tous les paiements ont été traités</p>
                      </div>
                    ) : (
                      pendingPayments.map((payment) => (
                        <div key={payment.id} className="bg-slate-600 rounded-lg p-4 border border-slate-500">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <p className="text-white font-bold text-lg">
                                {payment.amount} {payment.currency}
                              </p>
                              <p className="text-slate-300 font-medium">{payment.client_name}</p>
                              <p className="text-slate-400 text-sm">{payment.payment_method}</p>
                            </div>
                            <Badge className="bg-yellow-500/20 text-yellow-400">
                              En attente
                            </Badge>
                          </div>
                          
                          {payment.description && (
                            <p className="text-slate-300 text-sm mb-3 italic">"{payment.description}"</p>
                          )}
                          
                          <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                            <span>Déclaré le: {new Date(payment.created_at).toLocaleDateString('fr-FR')}</span>
                            <span>Client ID: {payment.client_id}</span>
                          </div>

                          <div className="flex space-x-2">
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
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <span className="text-orange-500">📋</span>
                    <span>Historique des Paiements</span>
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Tous les paiements confirmés et rejetés
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
                            <div className="text-right">
                              <Badge 
                                className={`mb-1 ${
                                  payment.status === 'CONFIRMED' 
                                    ? 'bg-green-500/20 text-green-400' 
                                    : 'bg-red-500/20 text-red-400'
                                }`}
                              >
                                {payment.status === 'CONFIRMED' ? 'Confirmé' : 'Rejeté'}
                              </Badge>
                              {payment.invoice_number && (
                                <p className="text-xs text-slate-400">
                                  {payment.invoice_number}
                                </p>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex justify-between text-xs text-slate-500">
                            <span>Déclaré: {new Date(payment.created_at).toLocaleDateString('fr-FR')}</span>
                            {payment.confirmation_date && (
                              <span>Traité: {new Date(payment.confirmation_date).toLocaleDateString('fr-FR')}</span>
                            )}
                          </div>
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

          {/* Prospects Tab */}
          <TabsContent value="prospects">
            <MyProspects />
          </TabsContent>

        </Tabs>

        {/* Confirmation Dialog */}
        {confirmationDialog.show && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4 border border-slate-600">
              <h3 className="text-lg font-bold text-white mb-4">Code de Confirmation</h3>
              <div className="space-y-4">
                <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4">
                  <p className="text-orange-400 text-sm mb-2">Code généré :</p>
                  <p className="text-2xl font-mono font-bold text-orange-400 text-center tracking-widest">
                    {confirmationDialog.generatedCode}
                  </p>
                </div>
                
                <div>
                  <Label className="text-slate-300">Saisissez le code pour confirmer :</Label>
                  <Input
                    type="text"
                    value={confirmationDialog.code}
                    onChange={(e) => setConfirmationDialog({
                      ...confirmationDialog, 
                      code: e.target.value.toUpperCase()
                    })}
                    placeholder="Entrez le code"
                    className="bg-slate-700 border-slate-600 text-white text-center text-lg font-mono tracking-widest"
                    maxLength={4}
                  />
                </div>
                
                <div className="flex space-x-3">
                  <Button
                    onClick={() => setConfirmationDialog({ show: false, payment: null, code: '', action: '' })}
                    variant="outline"
                    className="flex-1 border-slate-600 text-slate-300"
                  >
                    Annuler
                  </Button>
                  <Button
                    onClick={confirmPaymentWithCode}
                    disabled={confirmationDialog.code !== confirmationDialog.generatedCode}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                  >
                    Confirmer Paiement
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Rejection Dialog */}
        {rejectionDialog.show && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4 border border-slate-600">
              <h3 className="text-lg font-bold text-white mb-4">Motif de Rejet</h3>
              <div className="space-y-4">
                <div>
                  <Label className="text-slate-300">Motif du rejet (obligatoire) :</Label>
                  <textarea
                    value={rejectionDialog.reason}
                    onChange={(e) => setRejectionDialog({...rejectionDialog, reason: e.target.value})}
                    placeholder="Expliquez pourquoi ce paiement est rejeté..."
                    rows={4}
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 text-white rounded-md resize-none"
                    required
                  />
                </div>
                
                <div className="flex space-x-3">
                  <Button
                    onClick={() => setRejectionDialog({ show: false, payment: null, reason: '' })}
                    variant="outline"
                    className="flex-1 border-slate-600 text-slate-300"
                  >
                    Annuler
                  </Button>
                  <Button
                    onClick={rejectPaymentWithReason}
                    disabled={!rejectionDialog.reason.trim()}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                  >
                    Rejeter Paiement
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chat Widget */}
      <ChatWidget 
        currentUser={user} 
        onUnreadCountChange={setChatUnreadCount}
      />
    </div>
  );
}
