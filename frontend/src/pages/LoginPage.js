import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { Globe, ArrowLeft } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);

  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    role: 'EMPLOYEE'
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await login(loginData.email, loginData.password);
      toast.success('Connexion réussie !');
      
      if (user.role === 'SUPERADMIN') {
        navigate('/superadmin/dashboard');
      } else if (user.role === 'MANAGER') {
        navigate('/manager/dashboard');
      } else if (user.role === 'EMPLOYEE') {
        navigate('/employee/dashboard');
      } else if (user.role === 'CLIENT') {
        navigate('/client/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Échec de la connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await register(registerData);
      toast.success('Inscription réussie !');
      
      if (user.role === 'MANAGER') {
        navigate('/manager/dashboard');
      } else if (user.role === 'EMPLOYEE') {
        navigate('/employee/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Échec de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-4 text-slate-300 hover:text-white hover:bg-slate-800"
          data-testid="back-to-home-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Retour à l'accueil
        </Button>

        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Globe className="w-10 h-10 text-orange-500" />
            <span className="text-3xl font-bold text-white">ALORIA AGENCY</span>
          </div>
          <p className="text-slate-300">Accédez à votre tableau de bord d'immigration</p>
        </div>

        <div className="w-full">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-orange-500">Connexion</h2>
            <p className="text-slate-400 mt-2">Accédez à votre espace avec vos identifiants</p>
          </div>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Bon Retour</CardTitle>
              <CardDescription className="text-slate-400">Entrez vos identifiants pour accéder à votre compte</CardDescription>
            </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <Label htmlFor="login-email" className="text-slate-300">Adresse Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      data-testid="login-email-input"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      placeholder="votre.email@exemple.com"
                      required
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="login-password" className="text-slate-300">Mot de Passe</Label>
                    <Input
                      id="login-password"
                      type="password"
                      data-testid="login-password-input"
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      placeholder="Entrez votre mot de passe"
                      required
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50"
                    disabled={loading}
                    data-testid="login-submit-btn"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Connexion en cours...
                      </span>
                    ) : (
                      'Se Connecter'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Créer un Compte</CardTitle>
                <CardDescription className="text-slate-400">Inscrivez-vous en tant que gestionnaire ou employé</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <Label htmlFor="register-name" className="text-slate-300">Nom Complet</Label>
                    <Input
                      id="register-name"
                      data-testid="register-name-input"
                      value={registerData.full_name}
                      onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                      placeholder="Entrez votre nom complet"
                      required
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-email" className="text-slate-300">Adresse Email</Label>
                    <Input
                      id="register-email"
                      type="email"
                      data-testid="register-email-input"
                      value={registerData.email}
                      onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                      placeholder="votre.email@exemple.com"
                      required
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-phone" className="text-slate-300">Numéro de Téléphone</Label>
                    <Input
                      id="register-phone"
                      type="tel"
                      data-testid="register-phone-input"
                      value={registerData.phone}
                      onChange={(e) => setRegisterData({ ...registerData, phone: e.target.value })}
                      placeholder="+33 6 12 34 56 78"
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-role" className="text-slate-300">Rôle</Label>
                    <select
                      id="register-role"
                      data-testid="register-role-select"
                      value={registerData.role}
                      onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}
                      className="w-full mt-2 px-3 py-2 bg-[#0F172A] border border-slate-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                      required
                    >
                      <option value="EMPLOYEE">Employé</option>
                      <option value="MANAGER">Gestionnaire</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="register-password" className="text-slate-300">Mot de Passe</Label>
                    <Input
                      id="register-password"
                      type="password"
                      data-testid="register-password-input"
                      value={registerData.password}
                      onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                      placeholder="Créez un mot de passe fort"
                      required
                      className="mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50"
                    disabled={loading}
                    data-testid="register-submit-btn"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Création du compte...
                      </span>
                    ) : (
                      'S\'inscrire'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-4 text-center text-sm text-slate-400">
          <p>Identifiants de démonstration : Utilisez le formulaire d'inscription</p>
        </div>
      </div>
    </div>
  );
}