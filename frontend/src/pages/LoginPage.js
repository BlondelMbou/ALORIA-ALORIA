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
      toast.success('Login successful!');
      
      // Redirect based on role
      if (user.role === 'MANAGER') {
        navigate('/manager/dashboard');
      } else if (user.role === 'EMPLOYEE') {
        navigate('/employee/dashboard');
      } else if (user.role === 'CLIENT') {
        navigate('/client/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await register(registerData);
      toast.success('Registration successful!');
      
      // Redirect based on role
      if (user.role === 'MANAGER') {
        navigate('/manager/dashboard');
      } else if (user.role === 'EMPLOYEE') {
        navigate('/employee/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-orange-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-4"
          data-testid="back-to-home-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Globe className="w-10 h-10 text-orange-500" />
            <span className="text-3xl font-bold text-slate-800">ALORIA AGENCY</span>
          </div>
          <p className="text-slate-600">Access your immigration dashboard</p>
        </div>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login" data-testid="tab-login">Login</TabsTrigger>
            <TabsTrigger value="register" data-testid="tab-register">Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <Card>
              <CardHeader>
                <CardTitle>Welcome Back</CardTitle>
                <CardDescription>Enter your credentials to access your account</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <Label htmlFor="login-email">Email Address</Label>
                    <Input
                      id="login-email"
                      type="email"
                      data-testid="login-email-input"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      required
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="login-password">Password</Label>
                    <Input
                      id="login-password"
                      type="password"
                      data-testid="login-password-input"
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      placeholder="Enter your password"
                      required
                      className="mt-2"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-orange-500 hover:bg-orange-600"
                    disabled={loading}
                    data-testid="login-submit-btn"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Logging in...
                      </span>
                    ) : (
                      'Login'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="register">
            <Card>
              <CardHeader>
                <CardTitle>Create Account</CardTitle>
                <CardDescription>Register as a manager or employee</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <Label htmlFor="register-name">Full Name</Label>
                    <Input
                      id="register-name"
                      data-testid="register-name-input"
                      value={registerData.full_name}
                      onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                      placeholder="Enter your full name"
                      required
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-email">Email Address</Label>
                    <Input
                      id="register-email"
                      type="email"
                      data-testid="register-email-input"
                      value={registerData.email}
                      onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                      placeholder="your.email@example.com"
                      required
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-phone">Phone Number</Label>
                    <Input
                      id="register-phone"
                      type="tel"
                      data-testid="register-phone-input"
                      value={registerData.phone}
                      onChange={(e) => setRegisterData({ ...registerData, phone: e.target.value })}
                      placeholder="+1 234 567 8900"
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="register-role">Role</Label>
                    <select
                      id="register-role"
                      data-testid="register-role-select"
                      value={registerData.role}
                      onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}
                      className="w-full mt-2 px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                      required
                    >
                      <option value="EMPLOYEE">Employee</option>
                      <option value="MANAGER">Manager</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="register-password">Password</Label>
                    <Input
                      id="register-password"
                      type="password"
                      data-testid="register-password-input"
                      value={registerData.password}
                      onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                      placeholder="Create a strong password"
                      required
                      className="mt-2"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-orange-500 hover:bg-orange-600"
                    disabled={loading}
                    data-testid="register-submit-btn"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Creating account...
                      </span>
                    ) : (
                      'Register'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-4 text-center text-sm text-slate-600">
          <p>Demo credentials: Use the registration form or contact admin</p>
        </div>
      </div>
    </div>
  );
}
