import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { ArrowLeft, KeyRound } from 'lucide-react';
import AloriaLogo from '@/components/AloriaLogo';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);

  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  // Registration removed - only SuperAdmin can create users via hierarchy

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
      } else if (user.role === 'CONSULTANT') {
        navigate('/consultant/dashboard');
      } else if (user.role === 'CLIENT') {
        navigate('/client/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Échec de la connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setResetLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: resetEmail })
      });

      const data = await response.json();
      
      if (response.ok) {
        toast.success('Un nouveau mot de passe temporaire a été envoyé par email et notification', {
          duration: 8000
        });
        
        // Afficher le mot de passe temporaire (EN PRODUCTION: retirer)
        if (data.temporary_password) {
          toast.info(
            <div>
              <p className="font-semibold">Mot de passe temporaire:</p>
              <p className="font-mono text-lg">{data.temporary_password}</p>
            </div>,
            { duration: 15000 }
          );
        }
        
        setShowForgotPassword(false);
        setResetEmail('');
      } else {
        toast.error(data.detail || 'Erreur lors de la réinitialisation');
      }
    } catch (error) {
      toast.error('Erreur de connexion au serveur');
    } finally {
      setResetLoading(false);
    }
  };

  // Registration function removed - hierarchical user creation only

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-sm sm:max-w-md">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-3 sm:mb-4 text-slate-300 hover:text-white hover:bg-slate-800 text-sm sm:text-base touch-manipulation"
          data-testid="back-to-home-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          <span className="hidden xs:inline">Retour à l'accueil</span>
          <span className="xs:hidden">Retour</span>
        </Button>

        <div className="text-center mb-6 sm:mb-8">
          <div className="flex items-center justify-center mb-3 sm:mb-4">
            <AloriaLogo className="h-12 sm:h-14" showText={true} />
          </div>
          <p className="text-slate-300 text-sm sm:text-base">Accédez à votre tableau de bord d'immigration</p>
        </div>

        <div className="w-full">
          <div className="text-center mb-4 sm:mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-orange-500">Connexion</h2>
            <p className="text-slate-400 mt-1 sm:mt-2 text-sm sm:text-base">Accédez à votre espace avec vos identifiants</p>
          </div>

          <Card className="bg-gradient-to-br from-[#1E293B] to-[#334155] border-slate-700">
            <CardHeader className="pb-4 sm:pb-6">
              <CardTitle className="text-white text-lg sm:text-xl">Bon Retour</CardTitle>
              <CardDescription className="text-slate-400 text-sm sm:text-base">Entrez vos identifiants pour accéder à votre compte</CardDescription>
            </CardHeader>
              <CardContent className="pt-0">
                <form onSubmit={handleLogin} className="space-y-3 sm:space-y-4">
                  <div>
                    <Label htmlFor="login-email" className="text-slate-300 text-sm sm:text-base">Adresse Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      data-testid="login-email-input"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      placeholder="votre.email@exemple.com"
                      required
                      className="mt-1 sm:mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 h-10 sm:h-11 text-sm sm:text-base touch-manipulation"
                    />
                  </div>

                  <div>
                    <Label htmlFor="login-password" className="text-slate-300 text-sm sm:text-base">Mot de Passe</Label>
                    <Input
                      id="login-password"
                      type="password"
                      data-testid="login-password-input"
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      placeholder="Entrez votre mot de passe"
                      required
                      className="mt-1 sm:mt-2 bg-[#0F172A] border-slate-600 text-white placeholder:text-slate-500 h-10 sm:h-11 text-sm sm:text-base touch-manipulation"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <button
                      type="button"
                      onClick={() => setShowForgotPassword(true)}
                      className="text-sm text-orange-400 hover:text-orange-300 underline"
                    >
                      Mot de passe oublié ?
                    </button>
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/50 h-10 sm:h-11 text-sm sm:text-base touch-manipulation"
                    disabled={loading}
                    data-testid="login-submit-btn"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white mr-2"></div>
                        <span className="hidden xs:inline">Connexion en cours...</span>
                        <span className="xs:hidden">Connexion...</span>
                      </span>
                    ) : (
                      'Se Connecter'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
        </div>

        <div className="mt-3 sm:mt-4 text-center text-xs sm:text-sm text-slate-400">
          <p className="hidden sm:block">Identifiants de démonstration : Utilisez le formulaire d'inscription</p>
          <p className="sm:hidden">Identifiants de démo disponibles</p>
        </div>
      </div>
    </div>
  );
}