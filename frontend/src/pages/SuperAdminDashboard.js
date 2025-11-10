import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'sonner';
import NotificationBell from '../components/NotificationBell';
import HierarchicalUserCreation from '../components/HierarchicalUserCreation';
import BalanceMonitor from '../components/BalanceMonitor';
import ActivityHistory from '../components/ActivityHistory';
import ProspectManagement from '../components/ProspectManagement';
import SearchAndSort from '../components/SearchAndSort';
import AloriaLogo from '../components/AloriaLogo';
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

  // Initialiser les filtered lists quand les données sont chargées
  useEffect(() => {
    if (users.length > 0 && filteredUsers.length === 0) {
      setFilteredUsers(users);
    }
  }, [users]);

  useEffect(() => {
    if (activities.length > 0 && filteredActivities.length === 0) {
      setFilteredActivities(activities);
    }
  }, [activities]);

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
      setActivities(activitiesRes.data);
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

  const StatsCard = ({ title, value, icon, color }) => (
    <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
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
          onFilteredDataChange={setFilteredUsers}
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
                      onClick={() => setSelectedUser(user)}
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
              onFilteredDataChange={setFilteredActivities}
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
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">🔥</span>
              </div>
              <span className="text-orange-500 text-xl font-bold">ALORIA AGENCY</span>
            </div>
            <span className="text-slate-400">SuperAdmin Console</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <NotificationBell />
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{user?.full_name}</span>
              <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">SUPERADMIN</span>
            </div>
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
        {activeTab === 'users-creation' && <HierarchicalUserCreation onUserCreated={fetchDashboardData} />}
        {activeTab === 'balance' && <BalanceMonitor />}
      </div>
    </div>
  );
};

export default SuperAdminDashboard;