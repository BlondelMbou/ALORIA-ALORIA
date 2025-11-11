import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  Activity,
  Users, 
  FileText, 
  Eye, 
  Filter,
  Download,
  Calendar,
  Clock,
  Search
} from 'lucide-react';

const ActivityHistory = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    limit: 50
  });

  useEffect(() => {
    fetchActivities();
  }, [filters]);

  const fetchActivities = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.action) params.append('action', filters.action);
      params.append('limit', filters.limit.toString());
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/activities?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setActivities(data);
      }
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    if (action.includes('login') || action.includes('auth')) return <Users className="h-4 w-4" />;
    if (action.includes('payment')) return <FileText className="h-4 w-4" />;
    if (action.includes('client') || action.includes('user')) return <Users className="h-4 w-4" />;
    if (action.includes('case')) return <FileText className="h-4 w-4" />;
    if (action.includes('withdrawal')) return <FileText className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  const getActionColor = (action) => {
    if (action.includes('created')) return 'bg-green-500/20 text-green-400';
    if (action.includes('updated') || action.includes('modified')) return 'bg-blue-500/20 text-blue-400';
    if (action.includes('deleted') || action.includes('rejected')) return 'bg-red-500/20 text-red-400';
    if (action.includes('login')) return 'bg-purple-500/20 text-purple-400';
    if (action.includes('confirmed')) return 'bg-green-500/20 text-green-400';
    return 'bg-slate-500/20 text-slate-400';
  };

  const formatActionText = (action) => {
    const actionMap = {
      'user_login': 'Connexion utilisateur',
      'client_created': 'Client créé',
      'payment_confirmed': 'Paiement confirmé',
      'payment_rejected': 'Paiement rejeté',
      'payment_declared': 'Paiement déclaré',
      'withdrawal_created': 'Retrait déclaré',
      'case_updated': 'Dossier mis à jour',
      'case_progress_updated': 'Progression dossier',
      'user_created': 'Utilisateur créé',
      'contact_message_created': 'Message de contact',
      'visitor_registered': 'Visiteur enregistré'
    };
    
    return actionMap[action] || action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const exportActivities = () => {
    if (activities.length === 0) return;
    
    const csv = [
      ['Date/Heure', 'Utilisateur', 'Action', 'Détails'].join(','),
      ...activities.map(activity => [
        new Date(activity.timestamp).toLocaleString('fr-FR'),
        activity.user_name,
        formatActionText(activity.action),
        JSON.stringify(activity.details).replace(/"/g, '""')
      ].map(field => `"${field}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `activites_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center space-x-2">
            <Activity className="h-6 w-6 text-orange-500" />
            <span>Historique des Activités</span>
          </h3>
          <p className="text-slate-400 text-sm">Suivi des actions utilisateurs et événements système</p>
        </div>
        
        <Button
          onClick={exportActivities}
          disabled={activities.length === 0}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          <Download className="h-4 w-4 mr-2" />
          Exporter CSV
        </Button>
      </div>

      {/* Filters */}
      <Card className="bg-slate-700 border-slate-600">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Filter className="h-5 w-5 text-orange-500" />
            <span>Filtres</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label className="text-slate-300">Recherche par action</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  type="text"
                  value={filters.action}
                  onChange={(e) => setFilters({...filters, action: e.target.value})}
                  placeholder="Ex: payment, client, login..."
                  className="pl-10 bg-slate-600 border-slate-500 text-white"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-slate-300">ID Utilisateur</Label>
              <Input
                type="text"
                value={filters.user_id}
                onChange={(e) => setFilters({...filters, user_id: e.target.value})}
                placeholder="ID utilisateur"
                className="bg-slate-600 border-slate-500 text-white"
              />
            </div>
            
            <div>
              <Label className="text-slate-300">Limite</Label>
              <select
                value={filters.limit}
                onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
              >
                <option value={25}>25 activités</option>
                <option value={50}>50 activités</option>
                <option value={100}>100 activités</option>
                <option value={200}>200 activités</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Activities List */}
      <Card className="bg-slate-700 border-slate-600">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-white">
              Activités Récentes ({activities.length})
            </CardTitle>
            {loading && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-orange-500"></div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {activities.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-slate-500 mx-auto mb-3" />
              <p className="text-slate-400">Aucune activité trouvée</p>
              <p className="text-slate-500 text-sm">Modifiez vos filtres pour voir plus d'activités</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {activities.map((activity, index) => (
                <div key={activity.id || index} className="bg-slate-600 rounded-lg p-4 border border-slate-500">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-full ${getActionColor(activity.action)}`}>
                        {getActionIcon(activity.action)}
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{formatActionText(activity.action)}</h4>
                        <p className="text-slate-400 text-sm">Par: {activity.user_name}</p>
                        {activity.resource_type && (
                          <Badge className="mt-1 bg-slate-500/20 text-slate-300 text-xs">
                            {activity.resource_type}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-slate-400 text-sm">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(activity.timestamp).toLocaleDateString('fr-FR')}</span>
                      </div>
                      <div className="flex items-center space-x-1 text-slate-500 text-xs mt-1">
                        <Clock className="h-3 w-3" />
                        <span>{new Date(activity.timestamp).toLocaleTimeString('fr-FR')}</span>
                      </div>
                    </div>
                  </div>
                  
                  {activity.details && Object.keys(activity.details).length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-500">
                      <details>
                        <summary className="text-slate-300 text-sm cursor-pointer hover:text-orange-400 flex items-center space-x-1">
                          <Eye className="h-3 w-3" />
                          <span>Voir les détails</span>
                        </summary>
                        <div className="mt-2 bg-slate-700 rounded p-3">
                          <pre className="text-xs text-slate-300 overflow-x-auto">
                            {JSON.stringify(activity.details, null, 2)}
                          </pre>
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ActivityHistory;