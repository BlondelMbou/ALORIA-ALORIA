import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { clientsAPI, casesAPI, messagesAPI } from '../utils/api';
import { Globe, LogOut, CheckCircle, Clock, FileText, MessageCircle, Send, User, Mail, Phone, Calendar, ArrowRight, CheckSquare, Square } from 'lucide-react';
import ChatWidget from '../components/ChatWidget';
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
  
  // WebSocket hook  
  const { connected } = useSocket(localStorage.getItem('token'));

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const clientsRes = await clientsAPI.getAll();
      if (clientsRes.data.length > 0) {
        const myClient = clientsRes.data[0];
        setClient(myClient);

        const casesRes = await casesAPI.getAll();
        const myCase = casesRes.data.find(c => c.client_id === myClient.id);
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

        await fetchMessages();
      }
    } catch (error) {
      toast.error('Erreur lors du chargement');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const toggleDocumentComplete = (docName) => {
    setDocumentChecklist(prev => ({
      ...prev,
      [docName]: !prev[docName]
    }));
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

  const currentStep = caseData.workflow_steps[caseData.current_step_index];
  const progressPercentage = ((caseData.current_step_index + 1) / caseData.workflow_steps.length) * 100;
  const nextSteps = caseData.workflow_steps.slice(caseData.current_step_index + 1, caseData.current_step_index + 4);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
      {/* Header */}
      <header className="bg-[#1E293B] border-b border-slate-700/50 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Globe className="w-8 h-8 text-orange-500" />
              <div>
                <h1 className="text-xl font-bold text-white">ALORIA AGENCY</h1>
                <p className="text-sm text-slate-400">Mon Profil Client</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
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
        {/* Profile Overview */}
        <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700 mb-8">
          <CardContent className="p-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <Avatar className="w-20 h-20">
                  <AvatarFallback className="bg-orange-500 text-white text-2xl font-bold">
                    {user.full_name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">Bonjour, {user.full_name}</h1>
                  <p className="text-slate-300 text-lg mb-1">{caseData.country} - {caseData.visa_type}</p>
                  <div className="flex items-center space-x-4">
                    <Badge className={getStatusColor(caseData.status)} data-testid="case-status-badge">
                      {caseData.status}
                    </Badge>
                    {counselor && (
                      <div className="flex items-center text-slate-300">
                        <User className="w-4 h-4 mr-1" />
                        Conseiller: {counselor.name}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold text-orange-500 mb-1">
                  {Math.round(progressPercentage)}%
                </div>
                <p className="text-slate-400">Progression</p>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-6">
              <div className="flex justify-between text-sm text-slate-400 mb-2">
                <span>Étape {caseData.current_step_index + 1} sur {caseData.workflow_steps.length}</span>
                <span className="text-orange-500">{Math.round(progressPercentage)}% terminé</span>
              </div>
              <Progress value={progressPercentage} className="h-3" />
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6 bg-[#1E293B] border border-slate-700">
            <TabsTrigger value="progress" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">
              Progression
            </TabsTrigger>
            <TabsTrigger value="documents" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">
              Documents
            </TabsTrigger>
            <TabsTrigger value="timeline" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">
              Étapes À Venir
            </TabsTrigger>
            <TabsTrigger value="profile" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">
              Mon Profil
            </TabsTrigger>
          </TabsList>

          {/* Progress Tab */}
          <TabsContent value="progress">
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white text-xl">Étape Actuelle</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/10 border border-orange-500/20 rounded-lg p-6">
                      <div className="flex items-start space-x-4 mb-4">
                        <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                          {caseData.current_step_index + 1}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-bold text-xl text-white mb-2">{currentStep.title}</h3>
                          <p className="text-slate-300 mb-4">{currentStep.description}</p>
                          {currentStep.duration && (
                            <div className="flex items-center text-sm text-slate-400">
                              <Clock className="w-4 h-4 mr-2" />
                              Durée estimée: {currentStep.duration}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Statistiques</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Étapes terminées:</span>
                      <span className="text-green-500 font-semibold">{caseData.current_step_index}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Étapes restantes:</span>
                      <span className="text-orange-500 font-semibold">{caseData.workflow_steps.length - caseData.current_step_index}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Temps écoulé:</span>
                      <span className="text-slate-300">{formatDistanceToNow(new Date(caseData.created_at), { addSuffix: true, locale: fr })}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
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
                    {caseData.workflow_steps.map((step, stepIdx) => (
                      step.documents && step.documents.length > 0 && (
                        <div key={stepIdx} className="bg-[#0F172A] border border-slate-700 rounded-lg p-4">
                          <h5 className="font-medium text-slate-200 mb-2">
                            Étape {stepIdx + 1}: {step.title}
                          </h5>
                          <ul className="space-y-1 text-sm">
                            {step.documents.map((doc, docIdx) => (
                              <li key={docIdx} className="flex items-center text-slate-400">
                                {stepIdx < caseData.current_step_index ? (
                                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                                ) : stepIdx === caseData.current_step_index ? (
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
                  {nextSteps.map((step, idx) => (
                    <div key={idx} className="flex items-start space-x-4 p-4 bg-[#0F172A] border border-slate-700 rounded-lg">
                      <div className="w-10 h-10 bg-slate-700 text-slate-400 rounded-full flex items-center justify-center font-semibold">
                        {caseData.current_step_index + idx + 2}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-white mb-2">{step.title}</h4>
                        <p className="text-slate-300 mb-3">{step.description}</p>
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
