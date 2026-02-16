import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Activity, Heart, Shield, Zap, User, Stethoscope, Building2, ArrowRight, Check, ExternalLink } from 'lucide-react';
import * as api from '@/services/api';
import { toast } from 'sonner';

export const LandingPage = () => {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    role: 'patient'
  });
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [patientsData, doctorsData] = await Promise.all([
        api.getPatients(),
        api.getDoctors()
      ]);
      setPatients(patientsData);
      setDoctors(doctorsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      let name = formData.name;
      let email = formData.email;

      // Use selected patient/doctor if available
      if (formData.role === 'patient' && selectedPatient) {
        const patient = patients.find(p => p.id === selectedPatient);
        if (patient) {
          name = patient.name;
          email = `${patient.name.toLowerCase().replace(' ', '.')}@patient.omnihealth.io`;
        }
      } else if (formData.role === 'doctor' && selectedDoctor) {
        const doctor = doctors.find(d => d.id === selectedDoctor);
        if (doctor) {
          name = doctor.name;
          email = `${doctor.name.toLowerCase().replace(' ', '.')}@doctor.omnihealth.io`;
        }
      }

      const response = await api.login(
        email || `demo.${formData.role}@omnihealth.io`,
        name || `Demo ${formData.role.charAt(0).toUpperCase() + formData.role.slice(1)}`,
        formData.role
      );

      // Store patient/doctor ID for dashboard
      const userData = {
        ...response.user,
        role: formData.role,
        wallet: response.wallet,
        patientId: formData.role === 'patient' ? selectedPatient || patients[0]?.id : null,
        doctorId: formData.role === 'doctor' ? selectedDoctor || doctors[0]?.id : null
      };

      toast.success('Welcome to OmniHealth Guardian!', {
        description: `Smart Contract Wallet created: ${response.wallet.address.slice(0, 10)}...`
      });

      login(userData);
    } catch (error) {
      toast.error('Login failed', {
        description: error.message
      });
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: Activity,
      title: 'Real-Time Monitoring',
      description: 'Continuous tracking of vital signs from insulin pumps and pacemakers'
    },
    {
      icon: Shield,
      title: 'Blockchain Verified',
      description: 'All critical alerts are hashed and stored on opBNB for tamper-proof records'
    },
    {
      icon: Zap,
      title: 'AI-Powered Insights',
      description: 'OpenClaw agent provides personalized diet plans and health recommendations'
    },
    {
      icon: Heart,
      title: 'Emergency Response',
      description: 'Automatic nearest hospital notifications for critical events'
    }
  ];

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-transparent to-transparent" />
        
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Hero Content */}
            <div className="space-y-8">
              <div className="space-y-4">
                <Badge className="badge-verified px-3 py-1 text-sm" data-testid="hero-badge">
                  <Check className="w-3 h-3 mr-1" />
                  Powered by opBNB & OpenClaw
                </Badge>
                
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-foreground">
                  OmniHealth
                  <span className="block text-cyan-400">Guardian</span>
                </h1>
                
                <p className="text-base md:text-lg text-muted-foreground max-w-lg">
                  Decentralized AI-IoT Medical Monitoring Platform. Real-time vital tracking, 
                  blockchain-verified alerts, and AI-powered health insights.
                </p>
              </div>

              {/* Features Grid */}
              <div className="grid grid-cols-2 gap-4">
                {features.map((feature, index) => (
                  <div 
                    key={index}
                    className="p-4 rounded-lg border border-border/40 bg-card/50 card-hover"
                    data-testid={`feature-card-${index}`}
                  >
                    <feature.icon className="w-8 h-8 text-cyan-400 mb-2" />
                    <h3 className="font-semibold text-sm text-foreground">{feature.title}</h3>
                    <p className="text-xs text-muted-foreground mt-1">{feature.description}</p>
                  </div>
                ))}
              </div>

              {/* Stats */}
              <div className="flex gap-8 pt-4">
                <div>
                  <div className="text-3xl font-black text-foreground font-mono">10+</div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Patients</div>
                </div>
                <div>
                  <div className="text-3xl font-black text-foreground font-mono">20+</div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Doctors</div>
                </div>
                <div>
                  <div className="text-3xl font-black text-foreground font-mono">30+</div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">Hospitals</div>
                </div>
              </div>
            </div>

            {/* Right: Login Form */}
            <div className="lg:pl-8">
              <Card className="border-border/40 bg-card/80 backdrop-blur-sm glow-purple" data-testid="login-card">
                <CardHeader className="space-y-1">
                  <CardTitle className="text-2xl font-bold">Get Started</CardTitle>
                  <CardDescription>
                    Sign in with social auth to create your Smart Contract Wallet
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <Tabs defaultValue="patient" onValueChange={(value) => setFormData({ ...formData, role: value })}>
                      <TabsList className="grid grid-cols-3 w-full" data-testid="role-tabs">
                        <TabsTrigger value="patient" className="gap-1" data-testid="tab-patient">
                          <User className="w-4 h-4" />
                          Patient
                        </TabsTrigger>
                        <TabsTrigger value="doctor" className="gap-1" data-testid="tab-doctor">
                          <Stethoscope className="w-4 h-4" />
                          Doctor
                        </TabsTrigger>
                        <TabsTrigger value="organization" className="gap-1" data-testid="tab-organization">
                          <Building2 className="w-4 h-4" />
                          Org
                        </TabsTrigger>
                      </TabsList>

                      <TabsContent value="patient" className="space-y-4 mt-4">
                        <div className="space-y-2">
                          <Label htmlFor="patient-select">Select Patient Profile</Label>
                          <Select value={selectedPatient} onValueChange={setSelectedPatient}>
                            <SelectTrigger data-testid="patient-select">
                              <SelectValue placeholder="Choose a patient profile" />
                            </SelectTrigger>
                            <SelectContent>
                              {patients.map((patient) => (
                                <SelectItem key={patient.id} value={patient.id}>
                                  {patient.name} - {patient.condition?.replace('_', ' ')}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </TabsContent>

                      <TabsContent value="doctor" className="space-y-4 mt-4">
                        <div className="space-y-2">
                          <Label htmlFor="doctor-select">Select Doctor Profile</Label>
                          <Select value={selectedDoctor} onValueChange={setSelectedDoctor}>
                            <SelectTrigger data-testid="doctor-select">
                              <SelectValue placeholder="Choose a doctor profile" />
                            </SelectTrigger>
                            <SelectContent>
                              {doctors.map((doctor) => (
                                <SelectItem key={doctor.id} value={doctor.id}>
                                  {doctor.name} - {doctor.specialization}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </TabsContent>

                      <TabsContent value="organization" className="space-y-4 mt-4">
                        <div className="space-y-2">
                          <Label htmlFor="org-email">Organization Email</Label>
                          <Input
                            id="org-email"
                            type="email"
                            placeholder="admin@hospital.org"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            data-testid="org-email-input"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="org-name">Organization Name</Label>
                          <Input
                            id="org-name"
                            placeholder="Metropolitan Healthcare"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            data-testid="org-name-input"
                          />
                        </div>
                      </TabsContent>
                    </Tabs>

                    <div className="space-y-3 pt-2">
                      <Button 
                        type="submit" 
                        className="w-full bg-white text-black hover:bg-white/90 font-semibold"
                        disabled={isLoading}
                        data-testid="google-login-btn"
                      >
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                          <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                          <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                          <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                          <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Continue with Google
                      </Button>
                      
                      <Button 
                        type="button"
                        variant="outline" 
                        className="w-full"
                        onClick={handleLogin}
                        disabled={isLoading}
                        data-testid="demo-login-btn"
                      >
                        {isLoading ? 'Creating Wallet...' : 'Quick Demo Login'}
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </div>

                    <div className="pt-4 border-t border-border/40">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Account Abstraction Enabled</span>
                        <Badge variant="outline" className="text-xs">
                          <Zap className="w-3 h-3 mr-1" />
                          Gas-Free
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        Paymaster sponsors all critical alert transactions on opBNB
                      </p>
                    </div>
                  </form>
                </CardContent>
              </Card>

              {/* Network Info */}
              <div className="mt-4 p-4 rounded-lg border border-border/40 bg-card/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-muted-foreground">opBNB Testnet</span>
                  </div>
                  <a 
                    href="https://testnet.opbnbscan.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
                    data-testid="explorer-link"
                  >
                    Explorer <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
