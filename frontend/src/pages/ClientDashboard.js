import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { clientsAPI, casesAPI, messagesAPI } from '@/utils/api';
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
                <p className="text-sm text-slate-400">Portail Client</p>
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
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Progress Card */}
            <Card className="border-t-4 border-t-orange-500" data-testid="case-progress-card">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl mb-2">Your Immigration Case</CardTitle>
                    <CardDescription className="text-base">
                      {caseData.country} - {caseData.visa_type}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(caseData.status)} data-testid="case-status-badge">
                    {caseData.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {/* Progress Bar */}
                <div className="mb-8">
                  <div className="flex justify-between text-sm text-slate-400 mb-3">
                    <span className="font-semibold">Overall Progress</span>
                    <span className="font-bold text-orange-600">{Math.round(progressPercentage)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-4 mb-4">
                    <div
                      className="bg-gradient-to-r from-orange-500 to-orange-600 h-4 rounded-full transition-all progress-bar"
                      style={{ width: `${progressPercentage}%` }}
                    ></div>
                  </div>
                  <p className="text-center text-sm text-slate-400">
                    Step {caseData.current_step_index + 1} of {caseData.workflow_steps.length}
                  </p>
                </div>

                {/* Current Step */}
                <div className="bg-gradient-to-br from-orange-50 to-white border border-orange-200 rounded-lg p-6 mb-6">
                  <div className="flex items-start space-x-3 mb-4">
                    <div className="w-10 h-10 bg-orange-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                      {caseData.current_step_index + 1}
                    </div>
                    <div>
                      <h3 className="font-bold text-lg text-white mb-1">{currentStep.title}</h3>
                      <p className="text-slate-400">{currentStep.description}</p>
                    </div>
                  </div>

                  {/* Required Documents Checklist */}
                  <div className="bg-gradient-to-br from-[#1E293B] to-[#334155] rounded-lg p-4">
                    <h4 className="font-semibold text-white mb-3 flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-orange-500" />
                      Required Documents
                    </h4>
                    <ul className="space-y-2">
                      {currentStep.documents?.map((doc, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-sm">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-slate-300">{doc}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {currentStep.duration && (
                    <div className="mt-4 flex items-center text-sm text-slate-400">
                      <Clock className="w-4 h-4 mr-2" />
                      Estimated duration: {currentStep.duration}
                    </div>
                  )}
                </div>

                {/* Timeline */}
                <div>
                  <h3 className="font-bold text-lg text-white mb-4">Complete Journey</h3>
                  <div className="space-y-3">
                    {caseData.workflow_steps.map((step, idx) => {
                      const isCompleted = idx < caseData.current_step_index;
                      const isCurrent = idx === caseData.current_step_index;
                      const isPending = idx > caseData.current_step_index;

                      return (
                        <div key={idx} className="flex items-start space-x-3">
                          <div className="flex flex-col items-center">
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
                                isCompleted
                                  ? 'bg-green-500 text-white'
                                  : isCurrent
                                  ? 'bg-orange-500 text-white'
                                  : 'bg-slate-700 text-slate-400'
                              }`}
                            >
                              {isCompleted ? <CheckCircle className="w-5 h-5" /> : idx + 1}
                            </div>
                            {idx < caseData.workflow_steps.length - 1 && (
                              <div
                                className={`w-0.5 h-8 ${
                                  isCompleted ? 'bg-green-500' : 'bg-slate-700'
                                }`}
                              ></div>
                            )}
                          </div>
                          <div className={`flex-1 pb-4 ${isPending ? 'opacity-50' : ''}`}>
                            <h4 className="font-semibold text-white">{step.title}</h4>
                            <p className="text-sm text-slate-400">{step.description}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Counselor Card */}
            {counselor && (
              <Card data-testid="counselor-card">
                <CardHeader>
                  <CardTitle className="text-lg">Your Immigration Counselor</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-4">
                    <Avatar className="w-20 h-20 mx-auto mb-3">
                      <AvatarFallback className="bg-orange-100 text-orange-600 text-2xl font-bold">
                        {counselor.name.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <h3 className="font-bold text-lg text-white">{counselor.name}</h3>
                    <p className="text-sm text-slate-400">Immigration Counselor</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-slate-400">
                      <User className="w-4 h-4 mr-2" />
                      <span>Assigned to your case</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Messaging Card */}
            <Card data-testid="messaging-card">
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-orange-500" />
                  Messages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="h-96 overflow-y-auto border border-slate-200 rounded-lg p-3 space-y-3 bg-[#0F172A]">
                    {messages.length === 0 ? (
                      <p className="text-center text-slate-500 py-8">No messages yet. Start a conversation!</p>
                    ) : (
                      messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${msg.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg p-3 ${
                              msg.sender_id === user.id
                                ? 'bg-orange-500 text-white'
                                : 'bg-gradient-to-br from-[#1E293B] to-[#334155] text-white border border-slate-200'
                            }`}
                          >
                            <p className="text-sm mb-1">{msg.message}</p>
                            <p className="text-xs opacity-70">
                              {new Date(msg.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <Input
                      placeholder="Type your message..."
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleSendMessage();
                        }
                      }}
                      data-testid="client-message-input"
                    />
                    <Button onClick={handleSendMessage} className="bg-orange-500 hover:bg-orange-600" data-testid="client-send-message-btn">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
