import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { clientsAPI, casesAPI, messagesAPI } from '@/utils/api';
import { Globe, LogOut, Users, FileText, MessageCircle, CheckCircle, Clock, Send } from 'lucide-react';

export default function EmployeeDashboard() {
  const { user, logout } = useAuth();
  const [clients, setClients] = useState([]);
  const [cases, setCases] = useState([]);
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
      const [clientsRes, casesRes] = await Promise.all([
        clientsAPI.getAll(),
        casesAPI.getAll()
      ]);
      setClients(clientsRes.data);
      setCases(casesRes.data);
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

  const handleUpdateCase = async (caseId, updateData) => {
    try {
      await casesAPI.update(caseId, updateData);
      toast.success('Case updated successfully');
      fetchData();
      setSelectedCase(null);
    } catch (error) {
      toast.error('Failed to update case');
    }
  };

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
            <div className="flex items-center space-x-3">
              <Globe className="w-8 h-8 text-orange-500" />
              <div>
                <h1 className="text-xl font-bold text-white">ALORIA AGENCY</h1>
                <p className="text-sm text-slate-400">Tableau de Bord Employé</p>
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
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="border-l-4 border-l-blue-500" data-testid="stat-total-clients">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600 mb-1">My Clients</p>
                  <p className="text-3xl font-bold text-slate-900">{myStats.totalClients}</p>
                </div>
                <Users className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500" data-testid="stat-active-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600 mb-1">Active Cases</p>
                  <p className="text-3xl font-bold text-slate-900">{myStats.activeCases}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500" data-testid="stat-completed-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600 mb-1">Completed</p>
                  <p className="text-3xl font-bold text-slate-900">{myStats.completedCases}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-orange-500" data-testid="stat-pending-cases">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600 mb-1">Pending</p>
                  <p className="text-3xl font-bold text-slate-900">{myStats.pendingCases}</p>
                </div>
                <FileText className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="cases" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="cases" data-testid="tab-my-cases">My Cases</TabsTrigger>
            <TabsTrigger value="clients" data-testid="tab-my-clients">My Clients</TabsTrigger>
            <TabsTrigger value="create" data-testid="tab-create-client">Create Client</TabsTrigger>
          </TabsList>

          {/* My Cases */}
          <TabsContent value="cases">
            <div className="space-y-4">
              {cases.map((caseItem) => {
                const client = clients.find(c => c.id === caseItem.client_id);
                return (
                  <Card key={caseItem.id} className="hover:shadow-lg transition-all">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-bold text-xl text-slate-900 mb-1">{caseItem.client_name}</h3>
                          <p className="text-slate-600">{caseItem.country} - {caseItem.visa_type}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(caseItem.status)}>{caseItem.status}</Badge>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedCase(caseItem)}
                                data-testid={`update-case-${caseItem.id}-btn`}
                              >
                                Update
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle>Update Case Progress</DialogTitle>
                                <DialogDescription>
                                  {caseItem.client_name} - {caseItem.country} {caseItem.visa_type}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4">
                                <div>
                                  <Label>Current Step</Label>
                                  <Select
                                    defaultValue={caseItem.current_step_index.toString()}
                                    onValueChange={(value) => {
                                      handleUpdateCase(caseItem.id, { current_step_index: parseInt(value) });
                                    }}
                                  >
                                    <SelectTrigger>
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {caseItem.workflow_steps.map((step, idx) => (
                                        <SelectItem key={idx} value={idx.toString()}>
                                          Step {idx + 1}: {step.title}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div>
                                  <Label>Status</Label>
                                  <Select
                                    defaultValue={caseItem.status}
                                    onValueChange={(value) => {
                                      handleUpdateCase(caseItem.id, { status: value });
                                    }}
                                  >
                                    <SelectTrigger>
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="New">New</SelectItem>
                                      <SelectItem value="In Progress">In Progress</SelectItem>
                                      <SelectItem value="Documents Pending">Documents Pending</SelectItem>
                                      <SelectItem value="Under Review">Under Review</SelectItem>
                                      <SelectItem value="Approved">Approved</SelectItem>
                                      <SelectItem value="Rejected">Rejected</SelectItem>
                                    </SelectContent>
                                  </Select>
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
                              <DialogContent className="max-w-2xl max-h-[600px]">
                                <DialogHeader>
                                  <DialogTitle>Messages with {caseItem.client_name}</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div className="h-96 overflow-y-auto border border-slate-200 rounded-lg p-4 space-y-3">
                                    {messages[client.id]?.map((msg) => (
                                      <div
                                        key={msg.id}
                                        className={`flex ${msg.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                                      >
                                        <div
                                          className={`max-w-[70%] rounded-lg p-3 ${
                                            msg.sender_id === user.id
                                              ? 'bg-orange-500 text-white'
                                              : 'bg-slate-100 text-slate-900'
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
                                      placeholder="Type a message..."
                                      value={messageText}
                                      onChange={(e) => setMessageText(e.target.value)}
                                      onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                          handleSendMessage(client.id, client.user_id);
                                        }
                                      }}
                                      data-testid="message-input"
                                    />
                                    <Button
                                      onClick={() => handleSendMessage(client.id, client.user_id)}
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
                        <div className="flex justify-between text-sm text-slate-600 mb-2">
                          <span>Step {caseItem.current_step_index + 1} of {caseItem.workflow_steps.length}</span>
                          <span>{Math.round(((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-3">
                          <div
                            className="bg-orange-500 h-3 rounded-full transition-all progress-bar"
                            style={{ width: `${((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Current Step Details */}
                      <div className="bg-slate-50 rounded-lg p-4">
                        <h4 className="font-semibold text-slate-900 mb-2">
                          Current Step: {caseItem.workflow_steps[caseItem.current_step_index]?.title}
                        </h4>
                        <p className="text-sm text-slate-600 mb-3">
                          {caseItem.workflow_steps[caseItem.current_step_index]?.description}
                        </p>
                        <div>
                          <p className="text-sm font-semibold text-slate-700 mb-2">Required Documents:</p>
                          <ul className="space-y-1">
                            {caseItem.workflow_steps[caseItem.current_step_index]?.documents?.map((doc, idx) => (
                              <li key={idx} className="text-sm text-slate-600 flex items-center">
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
          </TabsContent>

          {/* My Clients */}
          <TabsContent value="clients">
            <Card>
              <CardHeader>
                <CardTitle>My Client Portfolio</CardTitle>
                <CardDescription>All clients assigned to you</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {clients.map((client) => {
                    const clientCase = cases.find(c => c.client_id === client.id);
                    return (
                      <Card key={client.id} className="border-2 hover:border-orange-500 transition-all">
                        <CardContent className="p-4">
                          <h3 className="font-bold text-lg text-slate-900 mb-2">{clientCase?.client_name || 'N/A'}</h3>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Country:</span>
                              <Badge variant="outline">{client.country}</Badge>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Visa Type:</span>
                              <span className="text-slate-900 font-medium text-xs">{client.visa_type}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Status:</span>
                              <Badge className={getStatusColor(client.current_status)}>{client.current_status}</Badge>
                            </div>
                            <div>
                              <div className="flex justify-between text-sm text-slate-600 mb-1">
                                <span>Progress:</span>
                                <span>{Math.round(client.progress_percentage)}%</span>
                              </div>
                              <div className="w-full bg-slate-200 rounded-full h-2">
                                <div
                                  className="bg-orange-500 h-2 rounded-full"
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
              </CardContent>
            </Card>
          </TabsContent>

          {/* Create Client */}
          <TabsContent value="create">
            <Card>
              <CardHeader>
                <CardTitle>Create New Client</CardTitle>
                <CardDescription>Add a new client to your portfolio</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateClient} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="client-name">Full Name *</Label>
                      <Input
                        id="client-name"
                        value={newClientForm.full_name}
                        onChange={(e) => setNewClientForm({ ...newClientForm, full_name: e.target.value })}
                        placeholder="Client's full name"
                        required
                        data-testid="create-client-name-input"
                      />
                    </div>
                    <div>
                      <Label htmlFor="client-email">Email *</Label>
                      <Input
                        id="client-email"
                        type="email"
                        value={newClientForm.email}
                        onChange={(e) => setNewClientForm({ ...newClientForm, email: e.target.value })}
                        placeholder="client@example.com"
                        required
                        data-testid="create-client-email-input"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="client-phone">Phone *</Label>
                      <Input
                        id="client-phone"
                        type="tel"
                        value={newClientForm.phone}
                        onChange={(e) => setNewClientForm({ ...newClientForm, phone: e.target.value })}
                        placeholder="+1 234 567 8900"
                        required
                        data-testid="create-client-phone-input"
                      />
                    </div>
                    <div>
                      <Label htmlFor="client-country">Destination Country *</Label>
                      <Select
                        value={newClientForm.country}
                        onValueChange={(value) => setNewClientForm({ ...newClientForm, country: value, visa_type: '' })}
                      >
                        <SelectTrigger data-testid="create-client-country-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Canada">🇨🇦 Canada</SelectItem>
                          <SelectItem value="France">🇫🇷 France</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="client-visa-type">Visa Type *</Label>
                    <Select
                      value={newClientForm.visa_type}
                      onValueChange={(value) => setNewClientForm({ ...newClientForm, visa_type: value })}
                    >
                      <SelectTrigger data-testid="create-client-visa-type-select">
                        <SelectValue placeholder="Select visa type" />
                      </SelectTrigger>
                      <SelectContent>
                        {visaTypes[newClientForm.country]?.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="client-message">Notes (Optional)</Label>
                    <Textarea
                      id="client-message"
                      value={newClientForm.message}
                      onChange={(e) => setNewClientForm({ ...newClientForm, message: e.target.value })}
                      placeholder="Additional information about the client..."
                      rows={4}
                      data-testid="create-client-notes-textarea"
                    />
                  </div>

                  <Button type="submit" className="w-full bg-orange-500 hover:bg-orange-600" data-testid="create-client-submit-btn">
                    Create Client
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
