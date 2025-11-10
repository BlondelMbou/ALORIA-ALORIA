import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { clientsAPI, casesAPI, messagesAPI, visitorsAPI } from '../utils/api';
import api from '../utils/api';
import { Globe, LogOut, Users, FileText, MessageCircle, CheckCircle, Clock, Send, UserPlus, Building2 } from 'lucide-react';
import ChatWidget from '../components/ChatWidget';
import NotificationBell from '../components/NotificationBell';
import MyProspects from '../components/MyProspects';
import SearchAndSort from '../components/SearchAndSort';
import AloriaLogo from '../components/AloriaLogo';
import useSocket from '../hooks/useSocket';

export default function EmployeeDashboard() {
  const { user, logout } = useAuth();
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [cases, setCases] = useState([]);
  const [filteredCases, setFilteredCases] = useState([]);
  const [visitors, setVisitors] = useState([]);
  const [filteredVisitors, setFilteredVisitors] = useState([]);
  const [messages, setMessages] = useState({});
  const [selectedCase, setSelectedCase] = useState(null);
  const [messageText, setMessageText] = useState('');
  const [loading, setLoading] = useState(true);
  const [newClientForm, setNewClientForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    country: 'Canada',
    visa_type: '',
    message: ''
  });
  
  // Visitor registration state
  const [showVisitorForm, setShowVisitorForm] = useState(false);
  const [newVisitor, setNewVisitor] = useState({
    full_name: '',
    phone_number: '',
    purpose: 'Consultation initiale',
    other_purpose: '',
    cni_number: ''
  });
  
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  
  // WebSocket hook
  const { connected } = useSocket(localStorage.getItem('token'));

  const visaTypes = {
    Canada: ['Work Permit', 'Study Permit', 'Permanent Residence (Express Entry)'],
    France: ['Work Permit (Talent Permit)', 'Student Visa', 'Family Reunification']
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [clientsRes, casesRes, visitorsRes] = await Promise.all([
        clientsAPI.getAll(),
        casesAPI.getAll(),
        visitorsAPI.getAll()
      ]);
      setClients(clientsRes.data);
      setCases(casesRes.data);
      setVisitors(visitorsRes.data);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (clientId) => {
    try {
      const response = await messagesAPI.getByClient(clientId);
      setMessages({ ...messages, [clientId]: response.data });
    } catch (error) {
      toast.error('Failed to load messages');
    }
  };

  const handleSendMessage = async (clientId, receiverId) => {
    if (!messageText.trim()) return;

    try {
      await messagesAPI.send({
        receiver_id: receiverId,
        client_id: clientId,
        message: messageText
      });
      toast.success('Message sent');
      setMessageText('');
      fetchMessages(clientId);
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  // Fonction handleUpdateCase supprimée - plus de mise à jour par les employés

  const handleCreateClient = async (e) => {
    e.preventDefault();
    try {
      await clientsAPI.create(newClientForm);
      toast.success('Client created successfully');
      setNewClientForm({
        full_name: '',
        email: '',
        phone: '',
        country: 'Canada',
        visa_type: '',
        message: ''
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create client');
    }
  };
  
  const handleCreateVisitor = async () => {
    // Validation des champs requis
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
      setShowVisitorForm(false);
      // Recharger la liste des visiteurs
      fetchData();
    } catch (error) {
      console.error('Erreur enregistrement visiteur:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement du visiteur');
    }
  };

  const visitorPurposeOptions = [
    'Consultation initiale',
    'Remise de documents', 
    'Mise à jour du dossier',
    'Rendez-vous planifié',
    'Affaire urgente',
    'Demande d\'informations',
    'Paiement',
    'Autre'
  ];

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'nouveau': return 'bg-slate-700/50 text-slate-300 border border-slate-600';
      case 'en cours': return 'bg-orange-500/10 text-orange-400 border border-orange-500/30';
      case 'terminé': return 'bg-green-500/10 text-green-400 border border-green-500/30';
      case 'new': return 'bg-slate-700/50 text-slate-300 border border-slate-600';
      case 'in progress': return 'bg-orange-500/10 text-orange-400 border border-orange-500/30';
      case 'completed': return 'bg-green-500/10 text-green-400 border border-green-500/30';
      default: return 'bg-slate-700/50 text-slate-300 border border-slate-600';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  const myStats = {
    totalClients: clients.length,
    activeCases: cases.filter(c => c.status === 'In Progress' || c.status === 'Under Review').length,
    completedCases: cases.filter(c => c.status === 'Approved' || c.status === 'Completed').length,
    pendingCases: cases.filter(c => c.status === 'New' || c.status === 'Documents Pending').length
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
      {/* Header */}
      <header className="bg-[#1E293B] border-b border-slate-700/50 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <AloriaLogo className="h-10" />
              <div className="text-left">
                <h1 className="text-xl font-bold text-white">Employee Dashboard</h1>
                <p className="text-xs text-slate-400 mt-0.5">Bienvenue, {user?.full_name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Dialog open={showVisitorForm} onOpenChange={setShowVisitorForm}>
                <DialogTrigger asChild>
                  <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                    <Building2 className="w-4 h-4 mr-2" />
                    Visiteur
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#1E293B] border-slate-700 max-w-lg">
                  <DialogHeader>
                    <DialogTitle className="text-white">Enregistrer un Visiteur</DialogTitle>
                    <DialogDescription className="text-slate-400">
                      Enregistrez les informations du visiteur
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    {/* Nom complet */}
                    <div>
                      <Label className="text-slate-300 font-medium">Nom complet du visiteur *</Label>
                      <Input
                        value={newVisitor.full_name}
                        onChange={(e) => setNewVisitor({...newVisitor, full_name: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white mt-2"
                        placeholder="Ex: Jean Dupont"
                        required
                      />
                    </div>

                    {/* Numéro de téléphone */}
                    <div>
                      <Label className="text-slate-300 font-medium">Numéro de téléphone *</Label>
                      <Input
                        value={newVisitor.phone_number}
                        onChange={(e) => setNewVisitor({...newVisitor, phone_number: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white mt-2"
                        placeholder="+237 6XX XX XX XX"
                        type="tel"
                        required
                      />
                    </div>

                    {/* Numéro de CNI */}
                    <div>
                      <Label className="text-slate-300 font-medium">Numéro de CNI (Carte Nationale d'Identité) *</Label>
                      <Input
                        value={newVisitor.cni_number}
                        onChange={(e) => setNewVisitor({...newVisitor, cni_number: e.target.value})}
                        className="bg-slate-800 border-slate-600 text-white mt-2"
                        placeholder="Ex: 123456789"
                        required
                      />
                    </div>

                    {/* Motif de la visite */}
                    <div>
                      <Label className="text-slate-300 font-medium">Motif de la visite *</Label>
                      <Select value={newVisitor.purpose} onValueChange={(value) => setNewVisitor({...newVisitor, purpose: value})}>
                        <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-2">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-800 border-slate-600">
                          {visitorPurposeOptions.map(option => (
                            <SelectItem key={option} value={option} className="text-white hover:bg-slate-700">
                              {option}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Précisions si Autre */}
                    {newVisitor.purpose === 'Autre' && (
                      <div>
                        <Label className="text-slate-300 font-medium">Précisez le motif</Label>
                        <Input
                          value={newVisitor.other_purpose}
                          onChange={(e) => setNewVisitor({...newVisitor, other_purpose: e.target.value})}
                          className="bg-slate-800 border-slate-600 text-white mt-2"
                          placeholder="Veuillez préciser le motif..."
                        />
                      </div>
                    )}
                    <div className="flex space-x-2">
                      <Button 
                        onClick={handleCreateVisitor}
                        className="flex-1 bg-orange-500 hover:bg-orange-600 text-white"
                      >
                        Enregistrer
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowVisitorForm(false)}
                        className="border-slate-600 text-slate-300 hover:bg-slate-800"
                      >
                        Annuler
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              
              <NotificationBell currentUser={user} />
              <div className="text-right">
                <p className="text-sm font-medium text-white">{user.full_name}</p>
                <p className="text-xs text-slate-400">{user.role}</p>
              </div>
              <Button variant="outline" onClick={logout} data-testid="logout-btn" className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white">
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-blue-500 border-slate-700" data-testid="stat-total-clients">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Mes Clients</p>
                  <p className="text-3xl font-bold text-white">{myStats.totalClients}</p>
                </div>
                <Users className="w-8 h-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-yellow-500 border-slate-700" data-testid="stat-active-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Dossiers Actifs</p>
                  <p className="text-3xl font-bold text-white">{myStats.activeCases}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-green-500 border-slate-700" data-testid="stat-completed-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Terminés</p>
                  <p className="text-3xl font-bold text-white">{myStats.completedCases}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-l-4 border-l-orange-500 border-slate-700" data-testid="stat-pending-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">En Attente</p>
                  <p className="text-3xl font-bold text-white">{myStats.pendingCases}</p>
                </div>
                <FileText className="w-8 h-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="cases" className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-6 bg-[#1E293B] border border-slate-700">
            <TabsTrigger value="cases" data-testid="tab-my-cases" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Mes Dossiers</TabsTrigger>
            <TabsTrigger value="clients" data-testid="tab-my-clients" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Mes Clients</TabsTrigger>
            <TabsTrigger value="prospects" data-testid="tab-prospects" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Prospects</TabsTrigger>
            <TabsTrigger value="visitors" data-testid="tab-visitors" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Visiteurs</TabsTrigger>
            <TabsTrigger value="create" data-testid="tab-create-client" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Créer un Client</TabsTrigger>
          </TabsList>

          {/* My Cases */}
          <TabsContent value="cases">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white text-2xl">Mes Dossiers</CardTitle>
                <CardDescription className="text-slate-400">
                  Suivez l'évolution des dossiers de vos clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                {cases.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400 text-lg">Aucun dossier assigné</p>
                  </div>
                ) : (
                  <>
                    {/* Recherche et Tri */}
                    <SearchAndSort
                      data={cases}
                      searchFields={['client_name', 'country', 'visa_type', 'status']}
                      sortOptions={[
                        { value: 'created_at', label: 'Date de création' },
                        { value: 'client_name', label: 'Nom du client' },
                        { value: 'country', label: 'Pays' },
                        { value: 'status', label: 'Statut' }
                      ]}
                      onFilteredDataChange={setFilteredCases}
                      placeholder="Rechercher un dossier (client, pays, type de visa, statut)..."
                    />

                    {/* Liste filtrée */}
                    <div className="space-y-4">
                      {filteredCases.map((caseItem) => {
                const client = clients.find(c => c.id === caseItem.client_id);
                return (
                  <Card key={caseItem.id} className="hover:shadow-lg transition-all bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-bold text-xl text-white mb-1">{caseItem.client_name}</h3>
                          <p className="text-slate-400">{caseItem.country} - {caseItem.visa_type}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(caseItem.status)}>{caseItem.status}</Badge>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                data-testid={`view-case-${caseItem.id}-btn`}
                              >
                                <FileText className="w-4 h-4 mr-2" />
                                Voir Détails
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle className="text-white">Détails du Dossier</DialogTitle>
                                <DialogDescription className="text-slate-400">
                                  {caseItem.client_name} - {caseItem.country} {caseItem.visa_type}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-6">
                                <div className="bg-[#0F172A] p-4 rounded-lg">
                                  <h4 className="font-medium text-white mb-3">État Actuel</h4>
                                  <div className="grid grid-cols-2 gap-4">
                                    <div>
                                      <p className="text-sm text-slate-400">Statut</p>
                                      <Badge className={getStatusColor(caseItem.status)}>{caseItem.status}</Badge>
                                    </div>
                                    <div>
                                      <p className="text-sm text-slate-400">Étape</p>
                                      <p className="text-white font-medium">
                                        {caseItem.current_step_index + 1} sur {caseItem.workflow_steps.length}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="font-medium text-white mb-3">Progression des Étapes</h4>
                                  <div className="space-y-3">
                                    {caseItem.workflow_steps.map((step, idx) => {
                                      const isCompleted = idx < caseItem.current_step_index;
                                      const isCurrent = idx === caseItem.current_step_index;
                                      
                                      return (
                                        <div key={idx} className="flex items-center space-x-3">
                                          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
                                            isCompleted ? 'bg-green-500 text-white' : 
                                            isCurrent ? 'bg-orange-500 text-white' : 
                                            'bg-[#1E293B] text-slate-400 border border-slate-600'
                                          }`}>
                                            {isCompleted ? '✓' : idx + 1}
                                          </div>
                                          <div className="flex-1">
                                            <p className={`font-medium ${
                                              isCompleted ? 'text-green-400' : 
                                              isCurrent ? 'text-orange-400' : 
                                              'text-slate-500'
                                            }`}>
                                              {step.title}
                                            </p>
                                            <p className="text-sm text-slate-400">{step.description}</p>
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                                
                                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                                  <p className="text-slate-300 text-sm">
                                    ℹ️ Les mises à jour de statut sont effectuées par le gestionnaire. 
                                    Vous recevrez une notification en cas de modification.
                                  </p>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                          {client && (
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => fetchMessages(client.id)}
                                  data-testid={`message-client-${caseItem.id}-btn`}
                                >
                                  <MessageCircle className="w-4 h-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-2xl max-h-[600px] bg-[#1E293B] border-slate-700">
                                <DialogHeader>
                                  <DialogTitle className="text-white">Messages with {caseItem.client_name}</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div className="h-96 overflow-y-auto bg-slate-800/50 rounded-lg p-4 space-y-3">
                                    {messages[client.id]?.map((msg) => (
                                      <div
                                        key={msg.id}
                                        className={`flex ${msg.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                                      >
                                        <div
                                          className={`max-w-[70%] rounded-lg p-3 ${
                                            msg.sender_id === user.id
                                              ? 'bg-orange-500 text-white'
                                              : 'bg-slate-700 text-slate-300 border border-slate-600'
                                          }`}
                                        >
                                          <p className="text-sm mb-1">{msg.message}</p>
                                          <p className="text-xs opacity-70">
                                            {new Date(msg.created_at).toLocaleString()}
                                          </p>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                  <div className="flex space-x-2">
                                    <Input
                                      placeholder="Tapez votre message..."
                                      value={messageText}
                                      onChange={(e) => setMessageText(e.target.value)}
                                      onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                          handleSendMessage(client.id, client.user_id);
                                        }
                                      }}
                                      className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500"
                                      data-testid="message-input"
                                    />
                                    <Button
                                      onClick={() => handleSendMessage(client.id, client.user_id)}
                                      className="bg-orange-500 hover:bg-orange-600 text-white"
                                      data-testid="send-message-btn"
                                    >
                                      <Send className="w-4 h-4" />
                                    </Button>
                                  </div>
                                </div>
                              </DialogContent>
                            </Dialog>
                          )}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="flex justify-between text-sm text-slate-400 mb-2">
                          <span>Step {caseItem.current_step_index + 1} of {caseItem.workflow_steps.length}</span>
                          <span>{Math.round(((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-3">
                          <div
                            className="bg-orange-500 h-3 rounded-full transition-all progress-bar"
                            style={{ width: `${((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Current Step Details */}
                      <div className="bg-[#1E293B] border border-slate-600 rounded-lg p-4">
                        <h4 className="font-semibold text-white mb-2">
                          Current Step: {caseItem.workflow_steps[caseItem.current_step_index]?.title}
                        </h4>
                        <p className="text-sm text-slate-400 mb-3">
                          {caseItem.workflow_steps[caseItem.current_step_index]?.description}
                        </p>
                        <div>
                          <p className="text-sm font-semibold text-slate-300 mb-2">Required Documents:</p>
                          <ul className="space-y-1">
                            {caseItem.workflow_steps[caseItem.current_step_index]?.documents?.map((doc, idx) => (
                              <li key={idx} className="text-sm text-slate-400 flex items-center">
                                <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                                {doc}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* My Clients */}
          <TabsContent value="clients">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white text-2xl">Mes Clients</CardTitle>
                <CardDescription className="text-slate-400">Tous les clients qui vous sont assignés</CardDescription>
              </CardHeader>
              <CardContent>
                {clients.length === 0 ? (
                  <div className="text-center py-12">
                    <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400 text-lg">Aucun client assigné</p>
                  </div>
                ) : (
                  <>
                    {/* Recherche et Tri */}
                    <SearchAndSort
                      data={clients}
                      searchFields={['full_name', 'email', 'country', 'visa_type']}
                      sortOptions={[
                        { value: 'created_at', label: 'Date de création' },
                        { value: 'full_name', label: 'Nom' },
                        { value: 'country', label: 'Pays' },
                        { value: 'progress_percentage', label: 'Progression' }
                      ]}
                      onFilteredDataChange={setFilteredClients}
                      placeholder="Rechercher un client (nom, email, pays, type de visa)..."
                    />

                    {/* Liste filtrée */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {filteredClients.map((client) => {
                    const clientCase = cases.find(c => c.client_id === client.id);
                    return (
                      <Card key={client.id} className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-2 border-slate-700 hover:border-orange-500 transition-all">
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
                              {(clientCase?.client_name || 'N')[0].toUpperCase()}
                            </div>
                            <div className="flex-1">
                              <h3 className="font-bold text-lg text-white leading-tight">{clientCase?.client_name || 'N/A'}</h3>
                              <p className="text-xs text-slate-400">{clientCase?.client_email || 'Email N/A'}</p>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Pays:</span>
                              <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">{client.country}</Badge>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Type de Visa:</span>
                              <span className="text-white font-medium text-xs">{client.visa_type}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-400">Statut:</span>
                              <Badge className={getStatusColor(client.current_status)}>{client.current_status}</Badge>
                            </div>
                            <div>
                              <div className="flex justify-between text-sm text-slate-400 mb-1">
                                <span>Progression:</span>
                                <span className="text-orange-400 font-semibold">{Math.round(client.progress_percentage)}%</span>
                              </div>
                              <div className="w-full bg-slate-700 rounded-full h-2.5">
                                <div
                                  className="bg-gradient-to-r from-orange-500 to-orange-600 h-2.5 rounded-full transition-all"
                                  style={{ width: `${client.progress_percentage}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Prospects */}
          <TabsContent value="prospects">
            <MyProspects />
          </TabsContent>

          {/* Visiteurs Tab */}
          <TabsContent value="visitors">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white text-2xl">Liste des Visiteurs</CardTitle>
                <CardDescription className="text-slate-400">
                  Tous les visiteurs enregistrés au bureau
                </CardDescription>
              </CardHeader>
              <CardContent>
                {visitors.length === 0 ? (
                  <div className="text-center py-12">
                    <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400 text-lg">Aucun visiteur enregistré</p>
                    <p className="text-slate-500 text-sm mt-2">Les visiteurs apparaîtront ici une fois enregistrés</p>
                  </div>
                ) : (
                  <>
                    {/* Recherche et Tri */}
                    <SearchAndSort
                      data={visitors}
                      searchFields={['full_name', 'phone_number', 'purpose', 'cni_number']}
                      sortOptions={[
                        { value: 'arrival_time', label: 'Date d\'arrivée' },
                        { value: 'full_name', label: 'Nom' },
                        { value: 'purpose', label: 'Motif' }
                      ]}
                      onFilteredDataChange={setFilteredVisitors}
                      placeholder="Rechercher un visiteur (nom, téléphone, motif, CNI)..."
                    />

                    {/* Liste filtrée */}
                    <div className="space-y-3">
                      {filteredVisitors.map((visitor) => (
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
                            {visitor.departure_time && (
                              <p className="text-xs text-slate-500">
                                <span className="font-semibold">Départ:</span> {new Date(visitor.departure_time).toLocaleString('fr-FR')}
                              </p>
                            )}
                            {visitor.registered_by && (
                              <p className="text-xs text-slate-600 mt-1">
                                Enregistré par: {visitor.registered_by}
                              </p>
                            )}
                          </div>
                          <div className="ml-4">
                            {visitor.departure_time ? (
                              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                ✓ Parti
                              </Badge>
                            ) : (
                              <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                                ⏰ Présent
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Create Client */}
          <TabsContent value="create">
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader className="border-b border-slate-700 pb-6">
                <CardTitle className="text-2xl font-bold text-white flex items-center gap-2">
                  <UserPlus className="w-6 h-6 text-orange-500" />
                  Créer un nouveau client
                </CardTitle>
                <CardDescription className="text-slate-400 mt-2">
                  Ajouter un nouveau client à votre portefeuille
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <form onSubmit={handleCreateClient} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="client-name" className="text-slate-300 font-medium">Nom complet *</Label>
                      <Input
                        id="client-name"
                        value={newClientForm.full_name}
                        onChange={(e) => setNewClientForm({ ...newClientForm, full_name: e.target.value })}
                        placeholder="Nom complet du client"
                        required
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="create-client-name-input"
                      />
                    </div>
                    <div>
                      <Label htmlFor="client-email" className="text-slate-300 font-medium">Email *</Label>
                      <Input
                        id="client-email"
                        type="email"
                        value={newClientForm.email}
                        onChange={(e) => setNewClientForm({ ...newClientForm, email: e.target.value })}
                        placeholder="client@exemple.com"
                        required
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="create-client-email-input"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="client-phone" className="text-slate-300 font-medium">Téléphone *</Label>
                      <Input
                        id="client-phone"
                        type="tel"
                        value={newClientForm.phone}
                        onChange={(e) => setNewClientForm({ ...newClientForm, phone: e.target.value })}
                        placeholder="+237 6XX XX XX XX"
                        required
                        className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                        data-testid="create-client-phone-input"
                      />
                    </div>
                    <div>
                      <Label htmlFor="client-country" className="text-slate-300 font-medium">Pays de destination *</Label>
                      <Select
                        value={newClientForm.country}
                        onValueChange={(value) => setNewClientForm({ ...newClientForm, country: value, visa_type: '' })}
                      >
                        <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-2" data-testid="create-client-country-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-800 border-slate-600">
                          <SelectItem value="Canada" className="text-white hover:bg-slate-700">🇨🇦 Canada</SelectItem>
                          <SelectItem value="France" className="text-white hover:bg-slate-700">🇫🇷 France</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="client-visa-type" className="text-slate-300 font-medium">Type de visa *</Label>
                    <Select
                      value={newClientForm.visa_type}
                      onValueChange={(value) => setNewClientForm({ ...newClientForm, visa_type: value })}
                    >
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-2" data-testid="create-client-visa-type-select">
                        <SelectValue placeholder="Sélectionner le type de visa" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-600">
                        {visaTypes[newClientForm.country]?.map((type) => (
                          <SelectItem key={type} value={type} className="text-white hover:bg-slate-700">
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="client-message" className="text-slate-300 font-medium">Notes (Optionnel)</Label>
                    <Textarea
                      id="client-message"
                      value={newClientForm.message}
                      onChange={(e) => setNewClientForm({ ...newClientForm, message: e.target.value })}
                      placeholder="Informations supplémentaires sur le client..."
                      rows={4}
                      className="bg-slate-800 border-slate-600 text-white placeholder:text-slate-500 mt-2"
                      data-testid="create-client-notes-textarea"
                    />
                  </div>

                  <Button type="submit" className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg" data-testid="create-client-submit-btn">
                    <UserPlus className="w-5 h-5 mr-2" />
                    Créer le Client
                  </Button>
                </form>
              </CardContent>
            </Card>
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
