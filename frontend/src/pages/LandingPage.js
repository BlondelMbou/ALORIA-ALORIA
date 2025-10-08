import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { clientsAPI } from '@/utils/api';
import { Globe, FileText, MessageCircle, CheckCircle, ArrowRight, MapPin } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    country: '',
    visa_type: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);

  const countries = [
    { value: 'Canada', label: 'Canada', flag: '🇨🇦' },
    { value: 'France', label: 'France', flag: '🇫🇷' }
  ];

  const visaTypes = {
    Canada: ['Work Permit', 'Study Permit', 'Permanent Residence (Express Entry)'],
    France: ['Work Permit (Talent Permit)', 'Student Visa', 'Family Reunification']
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.email || !formData.phone || !formData.country || !formData.visa_type) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      await clientsAPI.create(formData);
      toast.success('Your application has been submitted! Check your email for login details.');
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        country: '',
        visa_type: '',
        message: ''
      });
      
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-orange-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Globe className="w-8 h-8 text-orange-500" />
              <span className="text-2xl font-bold text-slate-800">ALORIA AGENCY</span>
            </div>
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#services" className="text-slate-600 hover:text-orange-500 font-medium transition-colors">
                Services
              </a>
              <a href="#countries" className="text-slate-600 hover:text-orange-500 font-medium transition-colors">
                Countries
              </a>
              <a href="#how-it-works" className="text-slate-600 hover:text-orange-500 font-medium transition-colors">
                How It Works
              </a>
              <Button 
                onClick={() => navigate('/login')}
                variant="outline"
                className="border-orange-500 text-orange-500 hover:bg-orange-50"
                data-testid="header-login-btn"
              >
                Login
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Hero Text */}
            <div className="space-y-8 fade-in">
              <div className="inline-block">
                <span className="px-4 py-2 bg-orange-100 text-orange-600 rounded-full text-sm font-semibold">
                  Trusted Immigration Services
                </span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                Your Immigration
                <span className="gradient-text block mt-2">Journey Starts Here</span>
              </h1>
              
              <p className="text-xl text-slate-600 leading-relaxed">
                Expert guidance for your visa applications to Canada, France, Belgium, and Germany. 
                We simplify the complex immigration process with transparency and efficiency.
              </p>

              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-slate-700">Real-time tracking</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-slate-700">Expert counselors</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-slate-700">100% transparency</span>
                </div>
              </div>

              <a 
                href="#start-application" 
                className="inline-block"
              >
                <Button 
                  size="lg" 
                  className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-6 text-lg"
                  data-testid="hero-get-started-btn"
                >
                  Get Started <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </a>
            </div>

            {/* Right Column - Stats Cards */}
            <div className="grid grid-cols-2 gap-6 fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="bg-white p-6 rounded-2xl shadow-lg card-hover">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                  <Globe className="w-6 h-6 text-orange-500" />
                </div>
                <h3 className="text-3xl font-bold text-slate-900">4</h3>
                <p className="text-slate-600 mt-1">Countries</p>
              </div>
              
              <div className="bg-white p-6 rounded-2xl shadow-lg card-hover">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-blue-500" />
                </div>
                <h3 className="text-3xl font-bold text-slate-900">12+</h3>
                <p className="text-slate-600 mt-1">Visa Types</p>
              </div>
              
              <div className="bg-white p-6 rounded-2xl shadow-lg card-hover">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                </div>
                <h3 className="text-3xl font-bold text-slate-900">98%</h3>
                <p className="text-slate-600 mt-1">Success Rate</p>
              </div>
              
              <div className="bg-white p-6 rounded-2xl shadow-lg card-hover">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <MessageCircle className="w-6 h-6 text-purple-500" />
                </div>
                <h3 className="text-3xl font-bold text-slate-900">24/7</h3>
                <p className="text-slate-600 mt-1">Support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Countries Section */}
      <section id="countries" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Countries We Serve</h2>
            <p className="text-xl text-slate-600">Expert immigration services for multiple destinations</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { name: 'Canada', flag: '🇨🇦', desc: 'Work, Study & PR programs' },
              { name: 'France', flag: '🇫🇷', desc: 'Talent permits & student visas' },
              { name: 'Belgium', flag: '🇧🇪', desc: 'Work & family reunification' },
              { name: 'Germany', flag: '🇩🇪', desc: 'EU Blue Card & skilled migration' }
            ].map((country) => (
              <div key={country.name} className="bg-gradient-to-br from-slate-50 to-white p-8 rounded-2xl border border-slate-200 hover:border-orange-500 transition-all card-hover text-center">
                <div className="text-6xl mb-4">{country.flag}</div>
                <h3 className="text-2xl font-bold text-slate-900 mb-2">{country.name}</h3>
                <p className="text-slate-600">{country.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gradient-to-br from-orange-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">How It Works</h2>
            <p className="text-xl text-slate-600">Simple steps to start your immigration journey</p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Submit Application', desc: 'Fill out our simple online form', icon: FileText },
              { step: '2', title: 'Get Assigned', desc: 'Matched with expert counselor', icon: MessageCircle },
              { step: '3', title: 'Track Progress', desc: 'Real-time updates on your case', icon: MapPin },
              { step: '4', title: 'Achieve Goals', desc: 'Receive your visa approval', icon: CheckCircle }
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
                  <div className="w-16 h-16 bg-orange-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                    {item.step}
                  </div>
                  <item.icon className="w-8 h-8 text-orange-500 mx-auto mb-3" />
                  <h3 className="text-xl font-bold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-slate-600">{item.desc}</p>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                    <ArrowRight className="w-6 h-6 text-orange-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Application Form */}
      <section id="start-application" className="py-20 bg-white">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Start Your Application</h2>
            <p className="text-xl text-slate-600">Fill out the form below to begin your immigration journey</p>
          </div>

          <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-xl border border-slate-200">
            <div className="space-y-6">
              <div>
                <Label htmlFor="full_name" className="text-slate-700">Full Name *</Label>
                <Input
                  id="full_name"
                  data-testid="input-full-name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="Enter your full name"
                  className="mt-2"
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="email" className="text-slate-700">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    data-testid="input-email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="your.email@example.com"
                    className="mt-2"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="phone" className="text-slate-700">Phone Number *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    data-testid="input-phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+1 234 567 8900"
                    className="mt-2"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="country" className="text-slate-700">Destination Country *</Label>
                  <Select
                    value={formData.country}
                    onValueChange={(value) => setFormData({ ...formData, country: value, visa_type: '' })}
                  >
                    <SelectTrigger className="mt-2" data-testid="select-country">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      {countries.map((country) => (
                        <SelectItem key={country.value} value={country.value}>
                          <span className="flex items-center">
                            <span className="mr-2">{country.flag}</span>
                            {country.label}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="visa_type" className="text-slate-700">Visa Type *</Label>
                  <Select
                    value={formData.visa_type}
                    onValueChange={(value) => setFormData({ ...formData, visa_type: value })}
                    disabled={!formData.country}
                  >
                    <SelectTrigger className="mt-2" data-testid="select-visa-type">
                      <SelectValue placeholder="Select visa type" />
                    </SelectTrigger>
                    <SelectContent>
                      {formData.country && visaTypes[formData.country]?.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="message" className="text-slate-700">Additional Information (Optional)</Label>
                <Textarea
                  id="message"
                  data-testid="textarea-message"
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Tell us about your immigration goals..."
                  rows={4}
                  className="mt-2"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full bg-orange-500 hover:bg-orange-600 text-white"
                disabled={loading}
                data-testid="submit-application-btn"
              >
                {loading ? (
                  <span className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </span>
                ) : (
                  'Submit Application'
                )}
              </Button>
            </div>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <Globe className="w-8 h-8 text-orange-500" />
                <span className="text-2xl font-bold">ALORIA AGENCY</span>
              </div>
              <p className="text-slate-400 mb-4">
                Your trusted partner for immigration services to Canada, France, Belgium, and Germany.
              </p>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#services" className="hover:text-orange-500 transition-colors">Services</a></li>
                <li><a href="#countries" className="hover:text-orange-500 transition-colors">Countries</a></li>
                <li><a href="/login" className="hover:text-orange-500 transition-colors">Login</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Contact</h3>
              <ul className="space-y-2 text-slate-400">
                <li>Email: info@aloriaagency.com</li>
                <li>Phone: +1 (555) 123-4567</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 ALORIA AGENCY. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
