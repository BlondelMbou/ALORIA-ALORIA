import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { Euro, Receipt, TrendingDown, Calendar } from 'lucide-react';

const WithdrawalManager = () => {
  const [withdrawals, setWithdrawals] = useState([]);
  const [expenseCategories, setExpenseCategories] = useState({});
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    subcategory: '',
    description: '',
    receipt_url: ''
  });

  useEffect(() => {
    fetchWithdrawals();
    fetchExpenseCategories();
  }, []);

  const fetchWithdrawals = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/withdrawals`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setWithdrawals(data);
      }
    } catch (error) {
      console.error('Error fetching withdrawals:', error);
    }
  };

  const fetchExpenseCategories = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/expense-categories`);
      if (response.ok) {
        const data = await response.json();
        setExpenseCategories(data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/withdrawals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount)
        })
      });

      if (response.ok) {
        toast.success('Retrait déclaré avec succès !');
        setFormData({
          amount: '',
          category: '',
          subcategory: '',
          description: '',
          receipt_url: ''
        });
        setShowForm(false);
        fetchWithdrawals();
      } else {
        throw new Error('Erreur lors de la déclaration du retrait');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error creating withdrawal:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedCategoryData = expenseCategories[formData.category];

  return (
    <div className="space-y-6">
      {/* Header with New Withdrawal Button */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-white">Gestion des Retraits</h3>
          <p className="text-slate-400 text-sm">Déclarez et suivez les dépenses de l'entreprise</p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="bg-orange-600 hover:bg-orange-700 text-white"
        >
          <TrendingDown className="h-4 w-4 mr-2" />
          {showForm ? 'Fermer' : 'Nouveau Retrait'}
        </Button>
      </div>

      {/* Withdrawal Form */}
      {showForm && (
        <Card className="bg-slate-700 border-slate-600">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Euro className="h-5 w-5 text-orange-500" />
              <span>Déclarer un Retrait</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Remplissez les détails du retrait pour le comptabiliser
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="amount" className="text-slate-300">Montant (CFA) *</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    placeholder="0.00"
                    required
                    className="bg-slate-600 border-slate-500 text-white"
                  />
                </div>

                <div>
                  <Label htmlFor="category" className="text-slate-300">Catégorie *</Label>
                  <select
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value, subcategory: ''})}
                    required
                    className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                  >
                    <option value="">Sélectionner une catégorie</option>
                    {Object.entries(expenseCategories).map(([key, categoryData]) => (
                      <option key={key} value={key}>
                        {categoryData.icon} {categoryData.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {formData.category && selectedCategoryData && (
                <div>
                  <Label htmlFor="subcategory" className="text-slate-300">Sous-catégorie *</Label>
                  <select
                    id="subcategory"
                    value={formData.subcategory}
                    onChange={(e) => setFormData({...formData, subcategory: e.target.value})}
                    required
                    className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                  >
                    <option value="">Sélectionner une sous-catégorie</option>
                    {selectedCategoryData.subcategories.map((sub) => (
                      <option key={sub} value={sub}>{sub}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <Label htmlFor="description" className="text-slate-300">Description *</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Détaillez l'objet de cette dépense..."
                  rows={3}
                  required
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md resize-none"
                />
              </div>

              <div>
                <Label htmlFor="receipt_url" className="text-slate-300">URL du Justificatif</Label>
                <Input
                  id="receipt_url"
                  type="url"
                  value={formData.receipt_url}
                  onChange={(e) => setFormData({...formData, receipt_url: e.target.value})}
                  placeholder="https://exemple.com/justificatif.pdf"
                  className="bg-slate-600 border-slate-500 text-white"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowForm(false)}
                  className="border-slate-600 text-slate-300"
                >
                  Annuler
                </Button>
                <Button
                  type="submit"
                  disabled={loading || !formData.amount || !formData.category || !formData.subcategory || !formData.description}
                  className="bg-orange-600 hover:bg-orange-700 text-white"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Déclaration...
                    </>
                  ) : (
                    <>
                      <Receipt className="h-4 w-4 mr-2" />
                      Déclarer le Retrait
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Withdrawals History */}
      <Card className="bg-slate-700 border-slate-600">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-orange-500" />
            <span>Historique des Retraits</span>
          </CardTitle>
          <CardDescription className="text-slate-400">
            Vos déclarations de retraits récentes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {withdrawals.length === 0 ? (
            <div className="text-center py-8">
              <TrendingDown className="h-12 w-12 text-slate-500 mx-auto mb-3" />
              <p className="text-slate-400">Aucun retrait déclaré</p>
              <p className="text-slate-500 text-sm">Utilisez le bouton ci-dessus pour déclarer votre premier retrait</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {withdrawals.map((withdrawal) => {
                const categoryData = expenseCategories[withdrawal.category];
                return (
                  <div key={withdrawal.id} className="bg-slate-600 rounded-lg p-4 border border-slate-500">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-2xl">{categoryData?.icon || '💼'}</span>
                          <div>
                            <h4 className="text-white font-medium">{categoryData?.name || withdrawal.category}</h4>
                            <p className="text-slate-400 text-sm">{withdrawal.subcategory}</p>
                          </div>
                        </div>
                        <p className="text-slate-300 text-sm">{withdrawal.description}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-red-400 font-bold text-lg">-{withdrawal.amount} €</p>
                        <Badge 
                          className="bg-red-500/20 text-red-400 mt-1"
                        >
                          Retrait
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center text-xs text-slate-500 border-t border-slate-500 pt-2 mt-2">
                      <span>Déclaré le: {new Date(withdrawal.created_at).toLocaleDateString('fr-FR')}</span>
                      {withdrawal.receipt_url && (
                        <a 
                          href={withdrawal.receipt_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-orange-400 hover:text-orange-300"
                        >
                          Voir justificatif →
                        </a>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default WithdrawalManager;