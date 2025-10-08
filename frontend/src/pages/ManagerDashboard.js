import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { dashboardAPI, clientsAPI, casesAPI, employeesAPI, visitorsAPI } from '@/utils/api';
import { Globe, LogOut, Users, FileText, TrendingUp, CheckCircle, Clock, AlertCircle, UserCheck, Building2, Search, Filter } from 'lucide-react';

export default function ManagerDashboard() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [clients, setClients] = useState([]);
  const [cases, setCases] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [visitors, setVisitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newVisitor, setNewVisitor] = useState({ name: '', company: '', purpose: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCountry, setFilterCountry] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchData();
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

  const handleReassignClient = async (clientId, employeeId) => {
    try {
      await clientsAPI.reassign(clientId, employeeId);
      toast.success('Client reassigned successfully');
      fetchData();
      setSelectedClient(null);
    } catch (error) {
      toast.error('Failed to reassign client');
    }
  };

  const handleAddVisitor = async () => {
    try {
      await visitorsAPI.create(newVisitor);
      toast.success('Visitor registered successfully');
      setNewVisitor({ name: '', company: '', purpose: '' });
      fetchData();
    } catch (error) {
      toast.error('Failed to register visitor');
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
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Globe className="w-8 h-8 text-orange-500" />
              <div>
                <h1 className="text-xl font-bold text-white">ALORIA AGENCY</h1>
                <p className="text-sm text-slate-400">Tableau de Bord Gestionnaire</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-white">{user.full_name}</p>
                <p className="text-xs text-slate-400">{user.role}</p>
              </div>
              <Button
                variant="outline"
                onClick={logout}
                data-testid="logout-btn"
                className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
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
          <TabsList className="grid w-full grid-cols-4 mb-6 bg-[#1E293B] border border-slate-700">
            <TabsTrigger value="clients" data-testid="tab-clients" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Clients</TabsTrigger>
            <TabsTrigger value="employees" data-testid="tab-employees" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Employés</TabsTrigger>
            <TabsTrigger value="cases" data-testid="tab-cases" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white text-slate-300">Dossiers</TabsTrigger>
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
                    <Input
                      placeholder="Rechercher des clients..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                      data-testid="search-clients-input"
                    />
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
                      <Card key={employee.id} className="border-2 hover:border-orange-500 transition-all">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                              <UserCheck className="w-6 h-6 text-orange-600" />
                            </div>
                            <Badge variant={employee.is_active ? "success" : "secondary"}>
                              {employee.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                          <h3 className="font-bold text-lg text-slate-900 mb-1">{employee.full_name}</h3>
                          <p className="text-sm text-slate-600 mb-4">{employee.email}</p>
                          <div className="space-y-2 mb-4">
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Active Cases:</span>
                              <span className="font-semibold text-slate-900">{activeCases}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Completed:</span>
                              <span className="font-semibold text-green-600">{completedCases}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-slate-600">Total Cases:</span>
                              <span className="font-semibold text-slate-900">{employeeCases.length}</span>
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
            <Card>
              <CardHeader>
                <CardTitle>All Cases</CardTitle>
                <CardDescription>Complete overview of all immigration cases</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {cases.map((caseItem) => (
                    <div key={caseItem.id} className="border border-slate-200 rounded-lg p-4 hover:border-orange-500 transition-all">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg text-slate-900">{caseItem.client_name}</h3>
                          <p className="text-sm text-slate-600">{caseItem.country} - {caseItem.visa_type}</p>
                        </div>
                        <Badge className={getStatusColor(caseItem.status)}>{caseItem.status}</Badge>
                      </div>
                      <div className="mb-3">
                        <div className="flex justify-between text-sm text-slate-600 mb-1">
                          <span>Step {caseItem.current_step_index + 1} of {caseItem.workflow_steps.length}</span>
                          <span>{Math.round(((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div
                            className="bg-orange-500 h-2 rounded-full transition-all"
                            style={{ width: `${((caseItem.current_step_index + 1) / caseItem.workflow_steps.length) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <p className="text-sm text-slate-700">
                        <strong>Current Step:</strong> {caseItem.workflow_steps[caseItem.current_step_index]?.title || 'N/A'}
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
              <Card>
                <CardHeader>
                  <CardTitle>Register New Visitor</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Label>Visitor Name</Label>
                      <Input
                        value={newVisitor.name}
                        onChange={(e) => setNewVisitor({ ...newVisitor, name: e.target.value })}
                        placeholder="Enter name"
                        data-testid="visitor-name-input"
                      />
                    </div>
                    <div>
                      <Label>Company</Label>
                      <Input
                        value={newVisitor.company}
                        onChange={(e) => setNewVisitor({ ...newVisitor, company: e.target.value })}
                        placeholder="Enter company"
                        data-testid="visitor-company-input"
                      />
                    </div>
                    <div>
                      <Label>Purpose</Label>
                      <Input
                        value={newVisitor.purpose}
                        onChange={(e) => setNewVisitor({ ...newVisitor, purpose: e.target.value })}
                        placeholder="Purpose of visit"
                        data-testid="visitor-purpose-input"
                      />
                    </div>
                    <Button onClick={handleAddVisitor} className="w-full bg-orange-500 hover:bg-orange-600" data-testid="add-visitor-btn">
                      <Building2 className="w-4 h-4 mr-2" />
                      Register Visitor
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Today's Visitors</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {visitors.slice(0, 10).map((visitor) => (
                      <div key={visitor.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <div>
                          <p className="font-semibold text-slate-900">{visitor.name}</p>
                          <p className="text-sm text-slate-600">{visitor.company} - {visitor.purpose}</p>
                          <p className="text-xs text-slate-500">Arrived: {new Date(visitor.arrival_time).toLocaleTimeString()}</p>
                        </div>
                        {!visitor.departure_time && (
                          <Button variant="outline" size="sm" onClick={() => handleCheckoutVisitor(visitor.id)}>
                            Check Out
                          </Button>
                        )}
                        {visitor.departure_time && (
                          <Badge variant="secondary">Checked Out</Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
