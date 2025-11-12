import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { toast } from 'sonner';
import { UserPlus, Eye, EyeOff, Copy, CheckCircle } from 'lucide-react';

const HierarchicalUserCreation = ({ onUserCreated }) => {
  const { user } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    phone: '',
    role: ''
  });
  const [loading, setLoading] = useState(false);
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);
  const [newUserCredentials, setNewUserCredentials] = useState(null);

  // Determine available roles based on current user role
  const getAvailableRoles = () => {
    switch (user?.role) {
      case 'SUPERADMIN':
        return [
          { value: 'MANAGER', label: 'Manager', description: 'Gère les employés et clients' },
          { value: 'CONSULTANT', label: 'Consultant', description: 'Consultation prospects payants' },
          { value: 'EMPLOYEE', label: 'Employé', description: 'Gère les clients assignés' }
        ];
      case 'MANAGER':
        return [
          { value: 'EMPLOYEE', label: 'Employé', description: 'Gère les clients assignés' },
          { value: 'CLIENT', label: 'Client', description: 'Accès au suivi de dossier' }
        ];
      case 'EMPLOYEE':
        return [
          { value: 'CLIENT', label: 'Client', description: 'Accès au suivi de dossier' }
        ];
      case 'CONSULTANT':
        return []; // Consultant ne peut créer personne
      default:
        return [];
    }
  };

  const availableRoles = getAvailableRoles();

  const generateRandomPassword = () => {
    const length = 12;
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
    let password = "";
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return password;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const password = generateRandomPassword();
      const userData = {
        ...formData,
        password: password
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedPassword(password);
        
        // Afficher le dialog avec les credentials
        setNewUserCredentials({
          email: formData.email,
          password: password,
          full_name: formData.full_name,
          role: formData.role
        });
        setShowCredentialsDialog(true);
        
        toast.success(`Utilisateur ${formData.role.toLowerCase()} créé avec succès !`);
        
        // Reset form
        setFormData({
          email: '',
          full_name: '',
          phone: '',
          role: ''
        });

        if (onUserCreated) {
          onUserCreated(result);
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de la création');
      }
    } catch (error) {
      toast.error(error.message || 'Erreur lors de la création de l\'utilisateur');
      console.error('Error creating user:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleHierarchy = () => {
    const roles = ['SUPERADMIN', 'MANAGER', 'EMPLOYEE', 'CLIENT'];
    const currentIndex = roles.indexOf(user?.role);
    
    return (
      <div className="flex items-center justify-center space-x-2 mb-6">
        {roles.map((role, index) => {
          const isCurrentUser = role === user?.role;
          const isAbove = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isBelow = index > currentIndex;

          return (
            <React.Fragment key={role}>
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                isCurrentUser 
                  ? 'bg-orange-500/20 text-orange-400 ring-2 ring-orange-400' 
                  : isAbove
                  ? 'bg-red-500/20 text-red-400'
                  : isBelow
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-slate-500/20 text-slate-400'
              }`}>
                {role}
                {isCurrentUser && <span className="ml-1">👤</span>}
              </div>
              {index < roles.length - 1 && (
                <span className="text-slate-500">→</span>
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  if (availableRoles.length === 0) {
    return (
      <Card className="bg-slate-700 border-slate-600">
        <CardContent className="p-6 text-center">
          <UserPlus className="h-12 w-12 text-slate-500 mx-auto mb-3" />
          <p className="text-slate-400">Vous n'avez pas les permissions pour créer d'autres utilisateurs.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-700 border-slate-600">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <UserPlus className="h-6 w-6 text-orange-500" />
          <span>Création d'Utilisateur Hiérarchique</span>
        </CardTitle>
        <CardDescription className="text-slate-400">
          Créez des utilisateurs selon la hiérarchie organisationnelle
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Role Hierarchy Visualization */}
        <div className="mb-6">
          <h4 className="text-slate-300 text-sm font-medium mb-3">Hiérarchie des Rôles:</h4>
          {getRoleHierarchy()}
          <p className="text-xs text-slate-500 text-center">
            Vous pouvez créer uniquement les rôles inférieurs ou égaux au vôtre
          </p>
        </div>

        {/* User Creation Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="full_name" className="text-slate-300">Nom Complet *</Label>
              <Input
                id="full_name"
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                placeholder="Jean Dupont"
                required
                className="bg-slate-600 border-slate-500 text-white"
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-slate-300">Email *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="jean.dupont@aloria.com"
                required
                className="bg-slate-600 border-slate-500 text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="phone" className="text-slate-300">Téléphone</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                placeholder="+33 1 23 45 67 89"
                className="bg-slate-600 border-slate-500 text-white"
              />
            </div>

            <div>
              <Label htmlFor="role" className="text-slate-300">Rôle *</Label>
              <select
                id="role"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                required
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
              >
                <option value="">Sélectionner un rôle</option>
                {availableRoles.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label} - {role.description}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4">
            <div className="text-xs text-slate-400">
              <p>* Un mot de passe temporaire sera généré automatiquement</p>
              <p>* L'utilisateur devra le changer lors de sa première connexion</p>
            </div>
            
            <Button 
              type="submit" 
              disabled={loading || !formData.email || !formData.full_name || !formData.role}
              className="bg-orange-600 hover:bg-orange-700 text-white"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Création...
                </>
              ) : (
                <>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Créer l'Utilisateur
                </>
              )}
            </Button>
          </div>
        </form>

        {/* Generated Password Display */}
        {generatedPassword && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <h4 className="text-green-400 font-medium mb-2">✅ Utilisateur créé avec succès !</h4>
            <div className="space-y-2">
              <p className="text-slate-300 text-sm">
                <strong>Email:</strong> {formData.email}
              </p>
              <div className="flex items-center space-x-2">
                <p className="text-slate-300 text-sm">
                  <strong>Mot de passe temporaire:</strong>
                </p>
                <div className="flex items-center space-x-2 bg-slate-800 rounded px-3 py-1">
                  <code className="text-orange-400 font-mono text-sm">
                    {showPassword ? generatedPassword : '••••••••••••'}
                  </code>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPassword(!showPassword)}
                    className="h-auto p-1 text-slate-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
              <p className="text-xs text-slate-500">
                ⚠️ Partagez ces informations de connexion de manière sécurisée avec le nouvel utilisateur
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>

    {/* Dialog des identifiants */}
    <Dialog open={showCredentialsDialog} onOpenChange={setShowCredentialsDialog}>
      <DialogContent className="bg-[#1E293B] border-slate-700 max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <CheckCircle className="w-6 h-6 text-green-500" />
            Utilisateur Créé!
          </DialogTitle>
        </DialogHeader>
        
        {newUserCredentials && (
          <div className="space-y-4 mt-4">
            <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-lg">
              <p className="text-green-400 text-sm font-semibold mb-2">
                ✅ L'utilisateur a été créé avec succès
              </p>
              <p className="text-slate-400 text-xs">
                Veuillez noter ces identifiants et les transmettre de manière sécurisée
              </p>
            </div>

            <div className="bg-slate-800 p-4 rounded-lg space-y-3">
              <div>
                <p className="text-slate-400 text-xs mb-1">Nom complet</p>
                <p className="text-white font-semibold">{newUserCredentials.full_name}</p>
              </div>
              
              <div>
                <p className="text-slate-400 text-xs mb-1">Rôle</p>
                <Badge className="bg-blue-500">{newUserCredentials.role}</Badge>
              </div>

              <div>
                <p className="text-slate-400 text-xs mb-1">📧 Email de connexion</p>
                <div className="flex items-center gap-2">
                  <code className="text-white bg-slate-900 px-3 py-2 rounded flex-1 font-mono text-sm">
                    {newUserCredentials.email}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-slate-600"
                    onClick={() => {
                      navigator.clipboard.writeText(newUserCredentials.email);
                      toast.success('Email copié!');
                    }}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div>
                <p className="text-slate-400 text-xs mb-1">🔑 Mot de passe temporaire</p>
                <div className="flex items-center gap-2">
                  <code className="text-orange-400 bg-slate-900 px-3 py-2 rounded flex-1 font-mono text-sm font-bold">
                    {newUserCredentials.password}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-slate-600"
                    onClick={() => {
                      navigator.clipboard.writeText(newUserCredentials.password);
                      toast.success('Mot de passe copié!');
                    }}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="bg-orange-500/10 border border-orange-500/30 p-3 rounded-lg">
              <p className="text-orange-400 text-xs">
                ⚠️ <strong>Important:</strong> Ces identifiants ne seront plus affichés. Assurez-vous de les sauvegarder maintenant.
              </p>
            </div>

            <Button 
              className="w-full bg-blue-500 hover:bg-blue-600"
              onClick={() => {
                setShowCredentialsDialog(false);
                setNewUserCredentials(null);
              }}
            >
              J'ai noté les identifiants
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  </div>
  );
};

export default HierarchicalUserCreation;