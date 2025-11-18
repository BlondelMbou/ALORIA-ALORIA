import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'sonner';
import NotificationBell from '../components/NotificationBell';
import HierarchicalUserCreation from '../components/HierarchicalUserCreation';
import BalanceMonitor from '../components/BalanceMonitor';
import ActivityHistory from '../components/ActivityHistory';
import ProspectManagement from '../components/ProspectManagement';
import SearchAndSort from '../components/SearchAndSort';
import ProfileSettings from '../components/ProfileSettings';
import AloriaLogo from '../components/AloriaLogo';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import api from '../utils/api';

const SuperAdminDashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showUserDetails, setShowUserDetails] = useState(false);
  const [userTempPassword, setUserTempPassword] = useState(null);
  const [visitors, setVisitors] = useState([]);
  const [filteredVisitors, setFilteredVisitors] = useState([]);
  const [showProfileSettings, setShowProfileSettings] = useState(false);

  // useCallback pour stabiliser les fonctions de callback
  const handleFilteredUsersChange = React.useCallback((data) => {
    setFilteredUsers(data);
  }, []);

  const handleFilteredActivitiesChange = React.useCallback((data) => {
    setFilteredActivities(data);
  }, []);

  const handleFilteredVisitorsChange = React.useCallback((data) => {
    setFilteredVisitors(data);
  }, []);

  // Calcul dynamique des stats à partir des données locales pour mise à jour en temps réel
  const calculatedStats = React.useMemo(() => {
    const managers = users.filter(u => u.role === 'MANAGER').length;
    const employeesCount = users.filter(u => u.role === 'EMPLOYEE').length;
    const clientsCount = users.filter(u => u.role === 'CLIENT').length;
    
    return {
      users: {
        total: users.length,
        managers: managers,
        employees: employeesCount,
        clients: clientsCount
      },
      business: stats?.business || {},
      consultations: stats?.consultations || { total_count: 0, total_amount: 0, currency: 'CFA' },
      activity: stats?.activity || {}
    };
  }, [users, stats]);

  // Utiliser les stats calculées si disponibles
  const displayStats = users.length > 0 ? calculatedStats : stats;

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh toutes les 2 minutes pour SuperAdmin
    const refreshInterval = setInterval(() => {
      fetchDashboardData();
    }, 120000); // 2 minutes
    
    return () => clearInterval(refreshInterval);
  }, []);

  // NOTE: Pas besoin d'initialiser filteredUsers/filteredActivities ici
  // car SearchAndSort le fait automatiquement via son useEffect

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, usersRes, activitiesRes] = await Promise.all([
        api.get('/admin/dashboard-stats'),
        api.get('/admin/users'),
        api.get('/admin/activities')
      ]);
      
      setStats(statsRes.data);
      setUsers(usersRes.data);
      
      console.log('📊 Activities loaded:', activitiesRes.data.length, 'activities');
      console.log('📊 First 3 activities:', activitiesRes.data.slice(0, 3));
      setActivities(activitiesRes.data);
      
      // Charger les visiteurs (messages de contact du site web)
      try {
        const visitorsResponse = await api.get('/contact-messages');
        console.log('📊 Visiteurs (Contact Messages) loaded:', visitorsResponse.data.length);
        setVisitors(visitorsResponse.data);
        setFilteredVisitors(visitorsResponse.data);
      } catch (error) {
        console.error('Error loading visitors:', error);
        toast.error('Erreur lors du chargement des visiteurs');
      }
    } catch (error) {
      toast.error('Erreur lors du chargement des données');
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImpersonate = async (userId) => {
    try {
      const response = await api.post(`/admin/impersonate`, { user_id: userId });
      toast.success(`Impersonnification de l'utilisateur réussie`);
      
      // Store the impersonation token and redirect
      localStorage.setItem('impersonation_token', response.data.impersonation_token);
      window.location.href = '/dashboard'; // Redirect to appropriate dashboard
    } catch (error) {
      toast.error('Erreur lors de l\'impersonnification');
      console.error('Error impersonating user:', error);
    }
  };

  const StatsCard = ({ title, value, icon, color, subtitle }) => (
    <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
          {subtitle && <p className="text-slate-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`${color} opacity-20`}>
          {icon}
        </div>
      </div>
    </div>
  );

  const UsersTab = () => (
    <div className="bg-slate-700 rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-4">Gestion des Utilisateurs</h3>
        
        {/* Recherche et Tri */}
        <SearchAndSort
          data={users}
          searchFields={['full_name', 'email', 'role']}
          sortOptions={[
            { value: 'created_at', label: 'Date de création' },
            { value: 'full_name', label: 'Nom' },
            { value: 'role', label: 'Rôle' },
            { value: 'email', label: 'Email' }
          ]}
          onFilteredDataChange={handleFilteredUsersChange}
          placeholder="Rechercher un utilisateur (nom, email, rôle)..."
        />
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-slate-600">
              <th className="pb-3 text-slate-300 font-medium">Utilisateur</th>
              <th className="pb-3 text-slate-300 font-medium">Rôle</th>
              <th className="pb-3 text-slate-300 font-medium">Email</th>
              <th className="pb-3 text-slate-300 font-medium">Statut</th>
              <th className="pb-3 text-slate-300 font-medium">Dernière Connexion</th>
              <th className="pb-3 text-slate-300 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user) => (
              <tr key={user.id} className="border-b border-slate-600/50">
                <td className="py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {user.full_name?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <span className="text-white font-medium">{user.full_name || 'Nom non défini'}</span>
                  </div>
                </td>
                <td className="py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.role === 'SUPERADMIN' ? 'bg-red-500/20 text-red-400' :
                    user.role === 'MANAGER' ? 'bg-blue-500/20 text-blue-400' :
                    user.role === 'EMPLOYEE' ? 'bg-green-500/20 text-green-400' :
                    'bg-orange-500/20 text-orange-400'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-4 text-slate-300">{user.email}</td>
                <td className="py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.is_active 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {user.is_active ? 'Actif' : 'Inactif'}
                  </span>
                </td>
                <td className="py-4 text-slate-300">
                  {user.last_login 
                    ? new Date(user.last_login).toLocaleDateString('fr-FR')
                    : 'Jamais'
                  }
                </td>
                <td className="py-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleImpersonate(user.id)}
                      className="px-3 py-1 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded transition-colors"
                      disabled={user.role === 'SUPERADMIN'}
                    >
                      Impersonner
                    </button>
                    <button
                      onClick={() => {
                        setSelectedUser(user);
                        setShowUserDetails(true);
                        setUserTempPassword(user.temporary_password || null);
                      }}
                      className="px-3 py-1 bg-slate-600 hover:bg-slate-500 text-white text-sm rounded transition-colors"
                    >
                      Voir
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const ActivitiesTab = () => {
    const getActivityIcon = (action) => {
      switch (action) {
        case 'LOGIN': return '🔐';
        case 'CREATE_USER': return '👤';
        case 'CREATE_CLIENT': return '🤝';
        case 'PAYMENT_CONFIRMED': return '💰';
        case 'PAYMENT_DECLARED': return '💳';
        case 'CASE_UPDATED': return '📂';
        case 'CASE_CREATED': return '📋';
        case 'WITHDRAWAL_DECLARED': return '💸';
        case 'RESPOND_TO_CONTACT': return '📧';
        default: return '⚡';
      }
    };

    const getActivityColor = (action) => {
      switch (action) {
        case 'LOGIN': return 'bg-blue-500/20 text-blue-400';
        case 'CREATE_USER': 
        case 'CREATE_CLIENT': return 'bg-green-500/20 text-green-400';
        case 'PAYMENT_CONFIRMED': 
        case 'PAYMENT_DECLARED': return 'bg-orange-500/20 text-orange-400';
        case 'CASE_UPDATED':
        case 'CASE_CREATED': return 'bg-purple-500/20 text-purple-400';
        case 'WITHDRAWAL_DECLARED': return 'bg-red-500/20 text-red-400';
        default: return 'bg-slate-500/20 text-slate-400';
      }
    };

    return (
      <div className="bg-[#1E293B] border border-slate-600 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Activités Récentes</h3>
          <button
            onClick={fetchDashboardData}
            className="px-3 py-1 bg-orange-500 hover:bg-orange-600 text-white text-sm rounded transition-colors"
          >
            🔄 Actualiser
          </button>
        </div>
        
        {activities.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <span className="text-4xl mb-2 block">📊</span>
            <p>Aucune activité récente</p>
          </div>
        ) : (
          <>
            {/* Recherche et Tri */}
            <SearchAndSort
              data={activities}
              searchFields={['user_name', 'action', 'details']}
              sortOptions={[
                { value: 'timestamp', label: 'Date' },
                { value: 'user_name', label: 'Utilisateur' },
                { value: 'action', label: 'Action' }
              ]}
              onFilteredDataChange={handleFilteredActivitiesChange}
              placeholder="Rechercher une activité (utilisateur, action, détails)..."
            />

            <div className="space-y-3">
              {filteredActivities.map((activity, index) => (
              <div key={activity.id || index} className="flex items-start space-x-4 p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700/70 transition-colors">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getActivityColor(activity.action)}`}>
                  <span className="text-lg">{getActivityIcon(activity.action)}</span>
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-white font-medium">
                        {activity.user_name || activity.user_id}
                      </p>
                      <p className="text-slate-300 text-sm mt-1">
                        {activity.action === 'LOGIN' && 'Connexion au système'}
                        {activity.action === 'CREATE_USER' && `Création d'utilisateur ${activity.details?.role || ''}`}
                        {activity.action === 'CREATE_CLIENT' && 'Création d\'un nouveau client'}
                        {activity.action === 'PAYMENT_CONFIRMED' && `Paiement confirmé (${activity.details?.amount || 'N/A'} CFA)`}
                        {activity.action === 'PAYMENT_DECLARED' && `Paiement déclaré (${activity.details?.amount || 'N/A'} CFA)`}
                        {activity.action === 'CASE_UPDATED' && 'Mise à jour de dossier'}
                        {activity.action === 'CASE_CREATED' && 'Création de dossier'}
                        {activity.action === 'WITHDRAWAL_DECLARED' && `Retrait déclaré (${activity.details?.amount || 'N/A'} CFA)`}
                        {activity.action === 'RESPOND_TO_CONTACT' && 'Réponse à un prospect'}
                        {!['LOGIN', 'CREATE_USER', 'CREATE_CLIENT', 'PAYMENT_CONFIRMED', 'PAYMENT_DECLARED', 'CASE_UPDATED', 'CASE_CREATED', 'WITHDRAWAL_DECLARED', 'RESPOND_TO_CONTACT'].includes(activity.action) && activity.action}
                      </p>
                      {activity.details && (
                        <div className="text-xs text-slate-400 mt-2">
                          {activity.details.client_email && <span>Client: {activity.details.client_email} • </span>}
                          {activity.details.resource_type && <span>Type: {activity.details.resource_type} • </span>}
                          {activity.resource_id && <span>ID: {activity.resource_id.slice(0, 8)}...</span>}
                        </div>
                      )}
                    </div>
                    <div className="text-right text-xs text-slate-400">
                      <div>{new Date(activity.timestamp).toLocaleDateString('fr-FR')}</div>
                      <div>{new Date(activity.timestamp).toLocaleTimeString('fr-FR')}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            </div>
          </>
        )}
        
        {activities.length > 0 && (
          <div className="text-center mt-4">
            <button
              onClick={() => window.open('/admin/activities', '_blank')}
              className="text-orange-400 hover:text-orange-300 text-sm underline"
            >
              Voir toutes les activités →
            </button>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <AloriaLogo />
            <span className="text-slate-400">SuperAdmin Console</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <NotificationBell />
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{user?.full_name}</span>
              <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">SUPERADMIN</span>
            </div>
            <button
              onClick={() => setShowProfileSettings(!showProfileSettings)}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              <span>👤</span>
              <span>Mon Profil</span>
            </button>
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              <span>🚪</span>
              <span>Déconnexion</span>
            </button>
          </div>
        </div>
      </header>

      <div className="p-6">
        {/* Stats Cards */}
        {activeTab === 'overview' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <StatsCard
                title="Total Utilisateurs"
                value={displayStats?.users?.total || 0}
                icon={<span className="text-2xl">👥</span>}
                color="text-blue-400"
              />
              <StatsCard
                title="Managers"
                value={displayStats?.users?.managers || 0}
                icon={<span className="text-2xl">👨‍💼</span>}
                color="text-green-400"
              />
              <StatsCard
                title="Employés"
                value={displayStats?.users?.employees || 0}
                icon={<span className="text-2xl">👨‍💻</span>}
                color="text-yellow-400"
              />
              <StatsCard
                title="Clients"
                value={displayStats?.users?.clients || 0}
                icon={<span className="text-2xl">👥</span>}
                color="text-orange-400"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <StatsCard
                title="Total Dossiers"
                value={displayStats?.business?.total_cases || 0}
                icon={<span className="text-2xl">📂</span>}
                color="text-purple-400"
              />
              <StatsCard
                title="Paiements Confirmés"
                value={displayStats?.business?.total_payments || 0}
                icon={<span className="text-2xl">💰</span>}
                color="text-green-400"
              />
              <StatsCard
                title="Connexions (24h)"
                value={displayStats?.activity?.daily_logins || 0}
                icon={<span className="text-2xl">⚡</span>}
                color="text-blue-400"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <StatsCard
                title="Paiements Consultation"
                value={displayStats?.consultations?.total_count || 0}
                subtitle={`${(displayStats?.consultations?.total_amount || 0).toLocaleString()} CFA`}
                icon={<span className="text-2xl">💼</span>}
                color="text-orange-400"
              />
              <StatsCard
                title="Revenus Consultations"
                value={`${(displayStats?.consultations?.total_amount || 0).toLocaleString()} CFA`}
                subtitle={`${displayStats?.consultations?.total_count || 0} paiements`}
                icon={<span className="text-2xl">💵</span>}
                color="text-emerald-400"
              />
            </div>
          </>
        )}

        {/* Navigation Tabs */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'overview'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Vue d'ensemble
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'users'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Utilisateurs
          </button>
          <button
            onClick={() => setActiveTab('activities')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'activities'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Activités
          </button>
          <button
            onClick={() => setActiveTab('prospects')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'prospects'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Prospects
          </button>
          <button
            onClick={() => setActiveTab('visitors')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'visitors'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Visiteurs
          </button>
          <button
            onClick={() => setActiveTab('users-creation')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'users-creation'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Créer Utilisateur
          </button>
          <button
            onClick={() => setActiveTab('balance')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'balance'
                ? 'bg-orange-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Solde & Finances
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'activities' && <ActivityHistory />}
        {activeTab === 'prospects' && <ProspectManagement userRole="SUPERADMIN" />}
        {activeTab === 'visitors' && (
          <div className="bg-[#1E293B] rounded-lg p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Liste des Visiteurs</h2>
              <p className="text-slate-400">Total: {visitors.length}</p>
            </div>
            
            <SearchAndSort
              data={visitors}
              searchFields={['name', 'email', 'phone', 'country', 'visa_type', 'message']}
              sortOptions={[
                { value: 'created_at', label: 'Date de visite' },
                { value: 'name', label: 'Nom' },
                { value: 'email', label: 'Email' },
                { value: 'country', label: 'Pays' }
              ]}
              onFilteredDataChange={handleFilteredVisitorsChange}
            />

            <div className="mt-6 overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Date</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Email</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Téléphone</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Pays</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Type de Visa</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-medium">Message</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredVisitors.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="text-center py-8 text-slate-400">
                        Aucun visiteur trouvé
                      </td>
                    </tr>
                  ) : (
                    filteredVisitors.map((visitor) => (
                      <tr key={visitor.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                        <td className="py-3 px-4 text-slate-300">
                          {visitor.created_at ? new Date(visitor.created_at).toLocaleDateString('fr-FR') : 'N/A'}
                        </td>
                        <td className="py-3 px-4 text-slate-300">{visitor.email || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-300">{visitor.phone || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-300">{visitor.country || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-300">{visitor.visa_type || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-300">
                          <div className="max-w-xs truncate" title={visitor.message}>
                            {visitor.message || 'Aucun message'}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        {activeTab === 'users-creation' && <HierarchicalUserCreation onUserCreated={fetchDashboardData} />}
        {activeTab === 'balance' && <BalanceMonitor />}
      </div>

      {/* User Details Modal */}
      {showUserDetails && selectedUser && (
        <Dialog open={showUserDetails} onOpenChange={setShowUserDetails}>
          <DialogContent className="bg-[#1E293B] border-slate-700 max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-white text-xl">Détails Utilisateur</DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              {/* Avatar & Nom */}
              <div className="flex items-center space-x-4 pb-4 border-b border-slate-700">
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">
                    {selectedUser.full_name?.charAt(0)}
                  </span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedUser.full_name}</h3>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    selectedUser.role === 'SUPERADMIN' ? 'bg-purple-500/20 text-purple-400' :
                    selectedUser.role === 'MANAGER' ? 'bg-blue-500/20 text-blue-400' :
                    selectedUser.role === 'CONSULTANT' ? 'bg-green-500/20 text-green-400' :
                    selectedUser.role === 'EMPLOYEE' ? 'bg-orange-500/20 text-orange-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {selectedUser.role}
                  </span>
                </div>
              </div>

              {/* Informations */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/50 p-4 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Email</p>
                  <p className="text-white font-medium">{selectedUser.email}</p>
                </div>

                <div className="bg-slate-800/50 p-4 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Statut</p>
                  <p className={`font-medium ${selectedUser.is_active ? 'text-green-400' : 'text-red-400'}`}>
                    {selectedUser.is_active ? '✅ Actif' : '❌ Inactif'}
                  </p>
                </div>

                <div className="bg-slate-800/50 p-4 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Créé le</p>
                  <p className="text-white">
                    {new Date(selectedUser.created_at).toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </p>
                </div>

                <div className="bg-slate-800/50 p-4 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Dernière connexion</p>
                  <p className="text-white">
                    {selectedUser.last_login 
                      ? new Date(selectedUser.last_login).toLocaleDateString('fr-FR')
                      : 'Jamais'
                    }
                  </p>
                </div>
              </div>

              {/* Mot de passe temporaire */}
              {userTempPassword && (
                <div className="bg-orange-500/10 border border-orange-500/30 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-orange-400 font-semibold">🔑 Mot de passe temporaire</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <code className="flex-1 px-4 py-2 bg-slate-800 rounded text-white font-mono">
                      {userTempPassword}
                    </code>
                    <Button
                      onClick={() => {
                        navigator.clipboard.writeText(userTempPassword);
                        toast.success('Mot de passe copié!');
                      }}
                      className="bg-orange-500 hover:bg-orange-600"
                    >
                      📋 Copier
                    </Button>
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    ⚠️ Ce mot de passe a été généré lors de la création du compte
                  </p>
                </div>
              )}

              {!userTempPassword && (
                <div className="bg-slate-800/50 p-4 rounded-lg text-center">
                  <p className="text-slate-400 text-sm">
                    ℹ️ Mot de passe temporaire non disponible (déjà changé par l'utilisateur)
                  </p>
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-4 border-t border-slate-700">
              <Button
                onClick={() => setShowUserDetails(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600"
              >
                Fermer
              </Button>
              {selectedUser.role !== 'SUPERADMIN' && (
                <Button
                  onClick={() => {
                    setShowUserDetails(false);
                    handleImpersonate(selectedUser.id);
                  }}
                  className="flex-1 bg-orange-500 hover:bg-orange-600"
                >
                  🎭 Impersonner
                </Button>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Profile Settings Overlay */}
      {showProfileSettings && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-end p-6">
          <div className="bg-[#0F172A] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-slate-700">
            <div className="sticky top-0 bg-[#1E293B] border-b border-slate-700 p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">⚙️ Paramètres du Profil</h2>
              <button
                onClick={() => setShowProfileSettings(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="p-6">
              <ProfileSettings user={user} onUpdate={fetchDashboardData} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuperAdminDashboard;