import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'sonner';
import NotificationBell from '../components/NotificationBell';
import HierarchicalUserCreation from '../components/HierarchicalUserCreation';
import BalanceMonitor from '../components/BalanceMonitor';
import api from '../utils/api';

const SuperAdminDashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

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
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-white">Gestion des Utilisateurs</h3>
        <input
          type="text"
          placeholder="Rechercher un utilisateur..."
          className="px-4 py-2 bg-slate-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
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
            {users.map((user) => (
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

  const ActivitiesTab = () => (
    <div className="bg-slate-700 rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6">Activités Récentes</h3>
      <div className="space-y-4">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-start space-x-4 p-4 bg-slate-600 rounded-lg">
            <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <p className="text-white font-medium">{activity.description}</p>
              <div className="flex items-center space-x-4 mt-2 text-sm text-slate-400">
                <span>Utilisateur: {activity.user_email}</span>
                <span>•</span>
                <span>{new Date(activity.timestamp).toLocaleString('fr-FR')}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

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
                value={stats.total_users || 0}
                icon={<span className="text-2xl">👥</span>}
                color="text-blue-400"
              />
              <StatsCard
                title="Managers"
                value={stats.managers_count || 0}
                icon={<span className="text-2xl">👨‍💼</span>}
                color="text-green-400"
              />
              <StatsCard
                title="Employés"
                value={stats.employees_count || 0}
                icon={<span className="text-2xl">👨‍💻</span>}
                color="text-yellow-400"
              />
              <StatsCard
                title="Clients"
                value={stats.clients_count || 0}
                icon={<span className="text-2xl">👥</span>}
                color="text-orange-400"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <StatsCard
                title="Total Dossiers"
                value={stats.total_cases || 0}
                icon={<span className="text-2xl">📂</span>}
                color="text-purple-400"
              />
              <StatsCard
                title="Paiements Confirmés"
                value={stats.confirmed_payments || 0}
                icon={<span className="text-2xl">💰</span>}
                color="text-green-400"
              />
              <StatsCard
                title="Activités (24h)"
                value={stats.recent_activities || 0}
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
        {activeTab === 'activities' && <ActivitiesTab />}
        {activeTab === 'users-creation' && <HierarchicalUserCreation onUserCreated={fetchDashboardData} />}
        {activeTab === 'users-creation' && <HierarchicalUserCreation />}
      </div>
    </div>
  );
};

export default SuperAdminDashboard;