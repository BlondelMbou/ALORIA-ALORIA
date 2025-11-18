import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { clientsAPI, casesAPI, messagesAPI } from '../utils/api';
import { Globe, LogOut, CheckCircle, Clock, FileText, MessageCircle, Send, User, Mail, Phone, Calendar, ArrowRight, CheckSquare, Square, Lock, Euro, CreditCard, Download } from 'lucide-react';
import ChatWidget from '../components/ChatWidget';
import NotificationBell from '../components/NotificationBell';
import AloriaLogo from '../components/AloriaLogo';
import useSocket from '../hooks/useSocket';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function ClientDashboard() {
  const { user, logout } = useAuth();
  const [client, setClient] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [loading, setLoading] = useState(true);
  const [counselor, setCounselor] = useState(null);
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [documentChecklist, setDocumentChecklist] = useState({});
  const [activeTab, setActiveTab] = useState('progress');
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [payments, setPayments] = useState([]);
  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    currency: 'CFA',
    description: '',
    payment_method: 'Virement bancaire'
  });
  
  // WebSocket hook  
  const { connected, socket } = useSocket(localStorage.getItem('token'));

  useEffect(() => {
    fetchData();
    fetchPayments(); // Charger l'historique des paiements au démarrage
  }, []);

  // Écouter les notifications de paiement pour rafraîchir automatiquement
  useEffect(() => {
    if (socket) {
      socket.on('notification', (notification) => {
        if (notification.type === 'payment_confirmed' || notification.type === 'payment_rejected') {
          // Rafraîchir les paiements automatiquement
          fetchPayments();
        }
      });
      
      return () => {
        socket.off('notification');
      };
    }
  }, [socket]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const clientsRes = await clientsAPI.getAll();
      if (clientsRes.data.length > 0) {
        const myClient = clientsRes.data[0];
        setClient(myClient);

        const casesRes = await casesAPI.getAll();
        // Le case.client_id correspond au user_id du client
        const myCase = casesRes.data.find(c => c.client_id === myClient.user_id);
        setCaseData(myCase);

        if (myClient.assigned_employee_id) {
          setCounselor({
            id: myClient.assigned_employee_id,
            name: myClient.assigned_employee_name || 'Votre Conseiller'
          });
        }
        
        // Initialize document checklist based on current step
        if (myCase && myCase.workflow_steps) {
          const checklist = {};
          myCase.workflow_steps.forEach((step, index) => {
            if (step.documents) {
              step.documents.forEach(doc => {
                checklist[doc] = index < myCase.current_step_index;
              });
            }
          });
          setDocumentChecklist(checklist);
        }

        // Messages and payments will be loaded separately
      }
    } catch (error) {
      toast.error('Erreur lors du chargement');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPayments = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/client-history`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPayments(data);
      }
    } catch (error) {
      console.error('Error fetching payments:', error);
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

  const handlePaymentDeclaration = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/declare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(paymentForm)
      });

      if (response.ok) {
        toast.success('Déclaration de paiement envoyée avec succès !');
        setPaymentForm({
          amount: '',
          currency: 'CFA',
          description: '',
          payment_method: 'Virement bancaire'
        });
        await fetchPayments();
      } else {
        throw new Error('Erreur lors de la déclaration');
      }
    } catch (error) {
      toast.error('Erreur lors de la déclaration de paiement');
      console.error(error);
    }
  };
  
  const toggleDocumentComplete = (docName) => {
    setDocumentChecklist(prev => ({
      ...prev,
      [docName]: !prev[docName]
    }));
  };

  const handleChangePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    try {
      const response = await api.patch('/auth/change-password', {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      });
      
      toast.success('Mot de passe mis à jour avec succès');
      setShowPasswordChange(false);
      setPasswordForm({
        old_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la mise à jour du mot de passe');
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'nouveau': case 'new': return 'bg-blue-500 text-white';
      case 'en cours': case 'in progress': return 'bg-yellow-500 text-white';
      case 'approuvé': case 'terminé': case 'approved': case 'completed': return 'bg-green-500 text-white';
      case 'rejeté': case 'rejected': return 'bg-red-500 text-white';
      default: return 'bg-slate-500 text-white';
    }
  };
  
  const getStepIcon = (stepIndex, currentStepIndex) => {
    if (stepIndex < currentStepIndex) {
      return <CheckCircle className="w-6 h-6 text-green-500" />;
    } else if (stepIndex === currentStepIndex) {
      return <Clock className="w-6 h-6 text-orange-500" />;
    } else {
      return <div className="w-6 h-6 rounded-full border-2 border-slate-600"></div>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!client || !caseData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
        <Card className="max-w-md bg-[#1E293B] border-slate-700">
          <CardContent className="p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Aucun Dossier Actif</h2>
            <p className="text-slate-400 mb-6">Vous n'avez pas encore de dossier d'immigration actif.</p>
            <Button onClick={logout} className="bg-orange-500 hover:bg-orange-600">Déconnexion</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Vérifier que workflow_steps existe et contient des données
  const workflowSteps = caseData.workflow_steps || [];
  const currentStepIndex = caseData.current_step_index || 0;
  const currentStep = workflowSteps[currentStepIndex] || {
    title: 'Étape en cours',
    description: 'Votre dossier est en cours de traitement',
    documents: []
  };
  const progressPercentage = workflowSteps.length > 0 
    ? ((currentStepIndex + 1) / workflowSteps.length) * 100 
    : 0;
  const nextSteps = workflowSteps.slice(currentStepIndex + 1, currentStepIndex + 4);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
      {/* Header - Mobile-First Responsive */}
      <header className="bg-[#1E293B] border-b border-slate-700/50 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-16 sm:h-18 md:h-20">
            {/* Logo Section - Mobile optimized */}
            <div className="flex items-center gap-2 sm:gap-3">
              <AloriaLogo className="h-8 sm:h-10" />
              <div className="hidden sm:block">
                <h1 className="text-base sm:text-lg md:text-xl font-bold text-white leading-tight">Espace Client</h1>
                <p className="text-xs sm:text-sm text-slate-400 truncate max-w-[120px] sm:max-w-none">{user?.full_name}</p>
              </div>
            </div>

            {/* Right side - Mobile responsive */}
            <div className="flex items-center gap-2 sm:gap-3">
              <NotificationBell currentUser={user} />
              
              {/* User info - Hidden on mobile, shown on tablet+ */}
              <div className="hidden lg:block text-right">
                <p className="text-sm font-medium text-white">{user.full_name}</p>
                <p className="text-xs text-slate-400">{user.role}</p>
              </div>

              {/* Logout button - Mobile optimized */}
              <Button 
                variant="outline" 
                onClick={logout} 
                data-testid="logout-btn" 
                className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-xs sm:text-sm px-2 sm:px-3 md:px-4 py-2 sm:py-2.5 touch-manipulation min-h-[44px]"
              >
                <LogOut className="w-4 h-4 sm:mr-1 md:mr-2" />
                <span className="hidden sm:inline">Déconnexion</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-5 md:py-6 lg:py-8">
        {/* Profile Overview - Mobile Responsive */}
        <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700 mb-4 sm:mb-5 md:mb-6 lg:mb-8 shadow-xl">
          <CardContent className="p-4 sm:p-5 md:p-6 lg:p-8">
            
            {/* Mobile Layout - Stack vertically */}
            <div className="block lg:hidden space-y-5">
              {/* User Info Row - Mobile Optimized */}
              <div className="flex items-start gap-3 sm:gap-4">
                <Avatar className="w-14 h-14 sm:w-16 sm:h-16 flex-shrink-0">
                  <AvatarFallback className="bg-orange-500 text-white text-xl sm:text-2xl font-bold">
                    {user.full_name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <h1 className="text-xl sm:text-2xl font-bold text-white mb-1.5 leading-tight">
                    Bonjour, {user.full_name.split(' ')[0]} 👋
                  </h1>
                  <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                    {caseData.country} - {caseData.visa_type}
                  </p>
                </div>
              </div>

              {/* Progress Card - Mobile First */}
              <div className="bg-gradient-to-r from-orange-500/10 to-orange-600/10 border border-orange-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-slate-300">Votre Progression</span>
                  <div className="text-3xl font-bold text-orange-500">
                    {Math.round(progressPercentage)}%
                  </div>
                </div>
                <div className="w-full bg-slate-700/50 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-orange-600 h-full transition-all duration-500 ease-out"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-2 text-center">
                  Étape {caseData.current_step_index + 1} sur {caseData.workflow_steps.length}
                </p>
              </div>

              {/* Status and Counselor Row - Mobile Optimized */}
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Statut:</span>
                  <Badge className={`${getStatusColor(caseData.status)} text-sm px-3 py-1`} data-testid="case-status-badge">
                    {caseData.status}
                  </Badge>
                </div>
                {counselor && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Conseiller:</span>
                    <div className="flex items-center text-slate-200 text-sm font-medium">
                      <User className="w-4 h-4 mr-1.5 text-orange-400" />
                      {counselor.name}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Desktop Layout - Side by side */}
            <div className="hidden lg:flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <Avatar className="w-20 h-20">
                  <AvatarFallback className="bg-orange-500 text-white text-2xl font-bold">
                    {user.full_name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">Bonjour, {user.full_name} 👋</h1>
                  <p className="text-slate-300 text-lg mb-2">{caseData.country} - {caseData.visa_type}</p>
                  <div className="flex items-center space-x-4">
                    <Badge className={`${getStatusColor(caseData.status)} px-3 py-1`} data-testid="case-status-badge">
                      {caseData.status}
                    </Badge>
                    {counselor && (
                      <div className="flex items-center text-slate-300">
                        <User className="w-4 h-4 mr-2 text-orange-400" />
                        <span className="font-medium">Conseiller: {counselor.name}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-5xl font-bold text-orange-500 mb-2">
                  {Math.round(progressPercentage)}%
                </div>
                <p className="text-slate-400 text-lg">Progression</p>
              </div>
            </div>
            
            {/* Progress Bar - Desktop Only */}
            <div className="hidden lg:block mt-8">
              <div className="flex justify-between text-sm text-slate-400 mb-3">
                <span>Étape {caseData.current_step_index + 1} sur {caseData.workflow_steps.length}</span>
                <span className="text-orange-500 font-medium">{Math.round(progressPercentage)}% terminé</span>
              </div>
              <Progress value={progressPercentage} className="h-3" />
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs - Mobile Optimized */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Mobile: Scrollable Tabs */}
          <div className="mb-5 sm:mb-6 -mx-3 sm:mx-0">
            <TabsList className="flex w-full overflow-x-auto md:grid md:grid-cols-5 bg-[#1E293B] border border-slate-700 p-1 scrollbar-hide gap-1 md:gap-0">
              <TabsTrigger 
                value="progress" 
                className="flex-shrink-0 min-w-[110px] sm:min-w-[120px] md:min-w-0 data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap rounded-lg md:rounded-none transition-all touch-manipulation"
              >
                📊 Progression
              </TabsTrigger>
              <TabsTrigger 
                value="documents" 
                className="flex-shrink-0 min-w-[110px] sm:min-w-[120px] md:min-w-0 data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap rounded-lg md:rounded-none transition-all touch-manipulation"
              >
                📄 Documents
              </TabsTrigger>
              <TabsTrigger 
                value="timeline" 
                className="flex-shrink-0 min-w-[110px] sm:min-w-[120px] md:min-w-0 data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap rounded-lg md:rounded-none transition-all touch-manipulation"
              >
                🗓️ À Venir
              </TabsTrigger>
              <TabsTrigger 
                value="payments" 
                className="flex-shrink-0 min-w-[110px] sm:min-w-[120px] md:min-w-0 data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap rounded-lg md:rounded-none transition-all touch-manipulation"
              >
                💳 Paiements
              </TabsTrigger>
              <TabsTrigger 
                value="profile" 
                className="flex-shrink-0 min-w-[110px] sm:min-w-[120px] md:min-w-0 data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap rounded-lg md:rounded-none transition-all touch-manipulation"
              >
                👤 Profil
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Progress Tab - Mobile Optimized */}
          <TabsContent value="progress" className="space-y-4 sm:space-y-5 md:space-y-6">
            {/* Current Step Card - Full Width on Mobile */}
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700 shadow-lg">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg sm:text-xl flex items-center gap-2">
                  <span className="text-2xl">🎯</span>
                  Étape Actuelle
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/10 border border-orange-500/30 rounded-xl p-4 sm:p-5 md:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                    <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-2xl flex items-center justify-center font-bold text-2xl shadow-lg flex-shrink-0">
                      {caseData.current_step_index + 1}
                    </div>
                    <div className="flex-1 space-y-3">
                      <h3 className="font-bold text-xl sm:text-2xl text-white leading-tight">{currentStep.title}</h3>
                      <p className="text-slate-300 text-sm sm:text-base leading-relaxed">{currentStep.description}</p>
                      {currentStep.duration && (
                        <div className="flex items-center text-sm text-slate-400 bg-slate-800/30 rounded-lg px-3 py-2 w-fit">
                          <Clock className="w-4 h-4 mr-2 text-orange-400" />
                          <span className="font-medium">Durée estimée: {currentStep.duration}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Statistics Card - Full Width on Mobile */}
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700 shadow-lg">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-lg sm:text-xl flex items-center gap-2">
                  <span className="text-2xl">📈</span>
                  Statistiques
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 text-center">
                    <div className="text-3xl sm:text-4xl font-bold text-green-400 mb-1">{caseData.current_step_index}</div>
                    <p className="text-slate-400 text-sm">Étapes terminées</p>
                  </div>
                  <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4 text-center">
                    <div className="text-3xl sm:text-4xl font-bold text-orange-400 mb-1">{caseData.workflow_steps.length - caseData.current_step_index}</div>
                    <p className="text-slate-400 text-sm">Étapes restantes</p>
                  </div>
                  <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 text-center sm:col-span-1">
                    <div className="text-lg sm:text-xl font-bold text-blue-400 mb-1">
                      {formatDistanceToNow(new Date(caseData.created_at), { addSuffix: false, locale: fr })}
                    </div>
                    <p className="text-slate-400 text-sm">Temps écoulé</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <FileText className="w-6 h-6 mr-2 text-orange-500" />
                  Documents Requis - Étape Actuelle
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Cochez les documents que vous avez préparés
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {currentStep.documents?.map((doc, idx) => (
                    <div key={idx} className="flex items-center space-x-3 p-3 bg-[#0F172A] border border-slate-700 rounded-lg">
                      <button
                        onClick={() => toggleDocumentComplete(doc)}
                        className="flex-shrink-0"
                      >
                        {documentChecklist[doc] ? (
                          <CheckSquare className="w-6 h-6 text-green-500" />
                        ) : (
                          <Square className="w-6 h-6 text-slate-400 hover:text-slate-300" />
                        )}
                      </button>
                      <span className={`flex-1 ${documentChecklist[doc] ? 'text-green-400 line-through' : 'text-white'}`}>
                        {doc}
                      </span>
                    </div>
                  )) || (
                    <p className="text-slate-400 text-center py-8">Aucun document requis pour cette étape</p>
                  )}
                </div>
                
                {/* All Documents Overview */}
                <div className="mt-8">
                  <h4 className="text-white font-semibold mb-4">Tous les Documents du Processus</h4>
                  <div className="grid md:grid-cols-2 gap-4">
                    {workflowSteps.map((step, stepIdx) => (
                      step && step.documents && step.documents.length > 0 && (
                        <div key={stepIdx} className="bg-[#0F172A] border border-slate-700 rounded-lg p-4">
                          <h5 className="font-medium text-slate-200 mb-2">
                            Étape {stepIdx + 1}: {step.title || 'Étape'}
                          </h5>
                          <ul className="space-y-1 text-sm">
                            {step.documents.map((doc, docIdx) => (
                              <li key={docIdx} className="flex items-center text-slate-400">
                                {stepIdx < currentStepIndex ? (
                                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                                ) : stepIdx === currentStepIndex ? (
                                  <Clock className="w-4 h-4 mr-2 text-orange-500" />
                                ) : (
                                  <div className="w-4 h-4 mr-2 rounded-full border border-slate-600"></div>
                                )}
                                {doc}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Calendar className="w-6 h-6 mr-2 text-orange-500" />
                  Prochaines Étapes
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Voici ce qui vous attend dans votre parcours d'immigration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {nextSteps.map((step, idx) => step && (
                    <div key={idx} className="flex items-start space-x-4 p-4 bg-[#0F172A] border border-slate-700 rounded-lg">
                      <div className="w-10 h-10 bg-slate-700 text-slate-400 rounded-full flex items-center justify-center font-semibold">
                        {currentStepIndex + idx + 2}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-white mb-2">{step.title || 'Étape à venir'}</h4>
                        <p className="text-slate-300 mb-3">{step.description || 'Détails à venir'}</p>
                        {step.duration && (
                          <div className="flex items-center text-sm text-slate-400 mb-2">
                            <Clock className="w-4 h-4 mr-2" />
                            Durée: {step.duration}
                          </div>
                        )}
                        {step.documents && step.documents.length > 0 && (
                          <div className="text-sm">
                            <p className="text-slate-400 mb-1">Documents requis:</p>
                            <ul className="list-disc list-inside text-slate-500 space-y-1">
                              {step.documents.slice(0, 3).map((doc, docIdx) => (
                                <li key={docIdx}>{doc}</li>
                              ))}
                              {step.documents.length > 3 && (
                                <li>... et {step.documents.length - 3} autres</li>
                              )}
                            </ul>
                          </div>
                        )}
                      </div>
                      <ArrowRight className="w-5 h-5 text-slate-500 mt-2" />
                    </div>
                  ))}
                  
                  {nextSteps.length === 0 && (
                    <div className="text-center py-12">
                      <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-white mb-2">Félicitations!</h3>
                      <p className="text-slate-400">Vous êtes à la dernière étape de votre processus d'immigration.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payments Tab - Mobile Optimized */}
          <TabsContent value="payments">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 md:gap-6">
              {/* Payment Declaration Form */}
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Euro className="h-6 w-6 text-orange-500" />
                    <span>Déclarer un Paiement</span>
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Déclarez vos paiements pour traitement et confirmation par votre gestionnaire
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePaymentDeclaration} className="space-y-4 sm:space-y-5">
                    {/* Mobile: Full width, Desktop: Side by side */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="amount" className="text-slate-300 font-medium mb-2 block">Montant</Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={paymentForm.amount}
                          onChange={(e) => setPaymentForm({...paymentForm, amount: e.target.value})}
                          required
                          className="bg-slate-600 border-slate-500 text-white h-12 text-base"
                        />
                      </div>
                      <div>
                        <Label htmlFor="currency" className="text-slate-300 font-medium mb-2 block">Devise</Label>
                        <select
                          id="currency"
                          value={paymentForm.currency}
                          onChange={(e) => setPaymentForm({...paymentForm, currency: e.target.value})}
                          className="w-full px-3 py-3 bg-slate-600 border border-slate-500 text-white rounded-md h-12 text-base"
                        >
                          <option value="CFA">CFA (FCFA)</option>
                          <option value="EUR">EUR (€)</option>
                          <option value="CAD">CAD ($)</option>
                          <option value="USD">USD ($)</option>
                        </select>
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="payment_method" className="text-slate-300">Méthode de Paiement</Label>
                      <select
                        id="payment_method"
                        value={paymentForm.payment_method}
                        onChange={(e) => setPaymentForm({...paymentForm, payment_method: e.target.value})}
                        className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                      >
                        <option value="Virement bancaire">Virement bancaire</option>
                        <option value="Carte bancaire">Carte bancaire</option>
                        <option value="Chèque">Chèque</option>
                        <option value="Espèces">Espèces</option>
                        <option value="PayPal">PayPal</option>
                      </select>
                    </div>

                    <div>
                      <Label htmlFor="description" className="text-slate-300">Description (optionnelle)</Label>
                      <textarea
                        id="description"
                        placeholder="Décrivez le paiement (ex: Frais de dossier, Honoraires consultation...)"
                        value={paymentForm.description}
                        onChange={(e) => setPaymentForm({...paymentForm, description: e.target.value})}
                        rows={3}
                        className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md resize-none"
                      />
                    </div>

                    <Button 
                      type="submit"
                      className="w-full bg-orange-600 hover:bg-orange-700 text-white"
                    >
                      <CreditCard className="h-4 w-4 mr-2" />
                      Déclarer le Paiement
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <FileText className="h-6 w-6 text-orange-500" />
                    <span>Historique des Paiements</span>
                  </CardTitle>
                  <CardDescription className="text-slate-400">
                    Suivez le statut de vos paiements déclarés
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {payments.length === 0 ? (
                      <div className="text-center py-8">
                        <Euro className="h-12 w-12 text-slate-500 mx-auto mb-3" />
                        <p className="text-slate-400">Aucun paiement déclaré</p>
                        <p className="text-slate-500 text-sm">Utilisez le formulaire pour déclarer votre premier paiement</p>
                      </div>
                    ) : (
                      payments.map((payment) => (
                        <div key={payment.id} className="bg-slate-600 rounded-lg p-4 border border-slate-500">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="text-white font-medium">
                                {payment.amount} {payment.currency}
                              </p>
                              <p className="text-slate-400 text-sm">{payment.payment_method}</p>
                            </div>
                            <Badge 
                              className={`${
                                payment.status === 'CONFIRMED' 
                                  ? 'bg-green-500/20 text-green-400' 
                                  : payment.status === 'REJECTED'
                                  ? 'bg-red-500/20 text-red-400'
                                  : 'bg-yellow-500/20 text-yellow-400'
                              }`}
                            >
                              {payment.status === 'CONFIRMED' ? 'Confirmé' : 
                               payment.status === 'REJECTED' ? 'Rejeté' : 'En attente'}
                            </Badge>
                          </div>
                          
                          {payment.description && (
                            <p className="text-slate-300 text-sm mb-2">{payment.description}</p>
                          )}
                          
                          <div className="flex justify-between items-center text-xs text-slate-500 mb-2">
                            <span>Déclaré le: {new Date(payment.created_at).toLocaleDateString('fr-FR')}</span>
                            {payment.invoice_number && (
                              <span>Facture: {payment.invoice_number}</span>
                            )}
                          </div>
                          
                          {payment.confirmation_date && (
                            <div className="mt-2 text-xs text-slate-400">
                              <CheckCircle className="h-3 w-3 inline mr-1" />
                              Confirmé le: {new Date(payment.confirmation_date).toLocaleDateString('fr-FR')}
                            </div>
                          )}
                          
                          {/* Bouton télécharger facture */}
                          {payment.status === 'CONFIRMED' && payment.invoice_number && (
                            <button
                              onClick={() => downloadInvoice(payment.id, payment.invoice_number)}
                              className="mt-3 w-full flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded text-sm transition-colors"
                            >
                              <Download className="w-4 h-4" />
                              Télécharger la facture
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

          {/* Profile Tab */}
          <TabsContent value="profile">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Informations Personnelles</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <User className="w-5 h-5 text-orange-500" />
                      <div>
                        <p className="text-slate-400 text-sm">Nom complet</p>
                        <p className="text-white font-medium">{user.full_name}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Mail className="w-5 h-5 text-orange-500" />
                      <div>
                        <p className="text-slate-400 text-sm">Email</p>
                        <p className="text-white font-medium">{user.email}</p>
                      </div>
                    </div>
                    {user.phone && (
                      <div className="flex items-center space-x-3">
                        <Phone className="w-5 h-5 text-orange-500" />
                        <div>
                          <p className="text-slate-400 text-sm">Téléphone</p>
                          <p className="text-white font-medium">{user.phone}</p>
                        </div>
                      </div>
                    )}
                    
                    {/* Change Password Section */}
                    <div className="pt-4 border-t border-slate-600">
                      <Dialog open={showPasswordChange} onOpenChange={setShowPasswordChange}>
                        <DialogTrigger asChild>
                          <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                            <Lock className="w-4 h-4 mr-2" />
                            Changer le mot de passe
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-[#1E293B] border-slate-700">
                          <DialogHeader>
                            <DialogTitle className="text-white">Changer le mot de passe</DialogTitle>
                            <DialogDescription className="text-slate-400">
                              Entrez votre mot de passe actuel et votre nouveau mot de passe
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label className="text-slate-300">Mot de passe actuel</Label>
                              <Input
                                type="password"
                                value={passwordForm.old_password}
                                onChange={(e) => setPasswordForm({...passwordForm, old_password: e.target.value})}
                                className="bg-[#0F172A] border-slate-600 text-white"
                              />
                            </div>
                            <div>
                              <Label className="text-slate-300">Nouveau mot de passe</Label>
                              <Input
                                type="password"
                                value={passwordForm.new_password}
                                onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                                className="bg-[#0F172A] border-slate-600 text-white"
                                placeholder="Minimum 8 caractères"
                              />
                            </div>
                            <div>
                              <Label className="text-slate-300">Confirmer le nouveau mot de passe</Label>
                              <Input
                                type="password"
                                value={passwordForm.confirm_password}
                                onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                                className="bg-[#0F172A] border-slate-600 text-white"
                              />
                            </div>
                            <div className="flex space-x-2">
                              <Button 
                                onClick={handleChangePassword}
                                className="flex-1 bg-orange-500 hover:bg-orange-600 text-white"
                              >
                                Mettre à jour
                              </Button>
                              <Button 
                                variant="outline" 
                                onClick={() => setShowPasswordChange(false)}
                                className="border-slate-600 text-slate-300 hover:bg-slate-800"
                              >
                                Annuler
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Détails du Dossier</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-slate-400 text-sm">Pays de destination</p>
                      <p className="text-white font-medium">{caseData.country}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Type de visa</p>
                      <p className="text-white font-medium">{caseData.visa_type}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Date de création</p>
                      <p className="text-white font-medium">{new Date(caseData.created_at).toLocaleDateString('fr-FR')}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Dernière mise à jour</p>
                      <p className="text-white font-medium">{formatDistanceToNow(new Date(caseData.updated_at), { addSuffix: true, locale: fr })}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Chat Widget */}
      <ChatWidget 
        currentUser={user} 
        onUnreadCountChange={setChatUnreadCount}
      />
    </div>
  );
}
