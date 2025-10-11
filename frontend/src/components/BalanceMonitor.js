import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { TrendingUp, TrendingDown, Wallet, RefreshCw, Eye, BarChart3 } from 'lucide-react';

const BalanceMonitor = () => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    fetchBalance();
  }, []);

  useEffect(() => {
    let interval = null;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchBalance();
      }, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchBalance = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/balance/current`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBalance(data);
      } else {
        throw new Error('Erreur lors du chargement du solde');
      }
    } catch (error) {
      console.error('Error fetching balance:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const getBalanceStatus = () => {
    if (!balance) return { color: 'text-slate-400', bgColor: 'bg-slate-500/20', label: 'Non disponible' };
    
    if (balance.current_balance > 10000) {
      return { color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Excellent' };
    } else if (balance.current_balance > 5000) {
      return { color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Bon' };
    } else if (balance.current_balance > 1000) {
      return { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Modéré' };
    } else if (balance.current_balance > 0) {
      return { color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Faible' };
    } else {
      return { color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Attention' };
    }
  };

  const balanceStatus = getBalanceStatus();

  return (
    <div className="space-y-6">
      {/* Real-time Balance Card */}
      <Card className="bg-gradient-to-r from-slate-700 to-slate-800 border-slate-600">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-white flex items-center space-x-2">
                <Wallet className="h-6 w-6 text-orange-500" />
                <span>Solde Temps Réel</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Solde actualisé automatiquement
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={balanceStatus.bgColor + ' ' + balanceStatus.color}>
                {balanceStatus.label}
              </Badge>
              <Button
                onClick={() => setAutoRefresh(!autoRefresh)}
                variant="outline"
                size="sm"
                className={`border-slate-600 ${autoRefresh ? 'bg-green-600 text-white' : 'text-slate-300'}`}
              >
                <Eye className="h-4 w-4 mr-1" />
                {autoRefresh ? 'Actif' : 'Manuel'}
              </Button>
              <Button
                onClick={fetchBalance}
                disabled={loading}
                variant="outline"
                size="sm"
                className="border-slate-600 text-slate-300"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {balance ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Current Balance */}
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <div className={`p-3 rounded-full ${balanceStatus.bgColor}`}>
                    <Wallet className={`h-8 w-8 ${balanceStatus.color}`} />
                  </div>
                </div>
                <h3 className="text-sm font-medium text-slate-400 mb-1">Solde Actuel</h3>
                <p className={`text-2xl font-bold ${balanceStatus.color}`}>
                  {formatCurrency(balance.current_balance)}
                </p>
              </div>

              {/* Total Payments */}
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <div className="p-3 rounded-full bg-green-500/20">
                    <TrendingUp className="h-8 w-8 text-green-400" />
                  </div>
                </div>
                <h3 className="text-sm font-medium text-slate-400 mb-1">Total Encaissements</h3>
                <p className="text-2xl font-bold text-green-400">
                  {formatCurrency(balance.total_payments)}
                </p>
              </div>

              {/* Total Withdrawals */}
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <div className="p-3 rounded-full bg-red-500/20">
                    <TrendingDown className="h-8 w-8 text-red-400" />
                  </div>
                </div>
                <h3 className="text-sm font-medium text-slate-400 mb-1">Total Retraits</h3>
                <p className="text-2xl font-bold text-red-400">
                  {formatCurrency(balance.total_withdrawals)}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="animate-pulse">
                <div className="w-16 h-16 bg-slate-600 rounded-full mx-auto mb-4"></div>
                <div className="w-32 h-4 bg-slate-600 rounded mx-auto mb-2"></div>
                <div className="w-24 h-4 bg-slate-600 rounded mx-auto"></div>
              </div>
            </div>
          )}

          {balance && (
            <div className="mt-6 pt-6 border-t border-slate-600">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Dernière mise à jour:</span>
                <span className="text-slate-300">
                  {new Date(balance.last_updated).toLocaleString('fr-FR')}
                </span>
              </div>
              {autoRefresh && (
                <div className="flex justify-center mt-2">
                  <Badge className="bg-green-500/20 text-green-400">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
                    Actualisation automatique (30s)
                  </Badge>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Balance Analytics */}
      <Card className="bg-slate-700 border-slate-600">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-orange-500" />
            <span>Analyse Financière</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {balance && (
            <div className="space-y-4">
              {/* Ratio Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-600 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">Ratio Encaissements/Retraits</h4>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{
                          width: `${Math.min((balance.total_payments / (balance.total_payments + balance.total_withdrawals)) * 100, 100)}%`
                        }}
                      ></div>
                    </div>
                    <span className="text-green-400 text-sm font-medium">
                      {Math.round((balance.total_payments / (balance.total_payments + balance.total_withdrawals)) * 100)}%
                    </span>
                  </div>
                </div>

                <div className="bg-slate-600 rounded-lg p-4">
                  <h4 className="text-white font-medium mb-2">Marge Opérationnelle</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`text-2xl font-bold ${
                      balance.current_balance > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {balance.total_payments > 0 ? Math.round((balance.current_balance / balance.total_payments) * 100) : 0}%
                    </span>
                    {balance.current_balance > 0 ? (
                      <TrendingUp className="h-5 w-5 text-green-400" />
                    ) : (
                      <TrendingDown className="h-5 w-5 text-red-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Quick Financial Health Indicators */}
              <div className="bg-slate-600 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">Indicateurs de Santé Financière</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Liquidité immédiate:</span>
                    <Badge className={balance.current_balance > 5000 ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'}>
                      {balance.current_balance > 5000 ? 'Bonne' : 'Attention'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Capacité de paiement:</span>
                    <Badge className={balance.current_balance > 2000 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                      {balance.current_balance > 2000 ? 'Sécurisée' : 'Risque'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Rentabilité:</span>
                    <Badge className={balance.current_balance > balance.total_payments * 0.3 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
                      {balance.current_balance > balance.total_payments * 0.3 ? 'Excellente' : 'À améliorer'}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BalanceMonitor;