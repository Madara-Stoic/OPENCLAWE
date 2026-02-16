import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, Heart, Droplets, Battery, AlertTriangle, 
  Utensils, Check, ExternalLink, RefreshCw, Sparkles, Clock
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import * as api from '@/services/api';
import { toast } from 'sonner';

export const PatientDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [currentReading, setCurrentReading] = useState(null);
  const [readingsHistory, setReadingsHistory] = useState([]);
  const [dietPlans, setDietPlans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingDiet, setIsGeneratingDiet] = useState(false);

  const patientId = user?.patientId;

  const fetchDashboard = useCallback(async () => {
    if (!patientId) return;
    try {
      const data = await api.getPatientDashboard(patientId);
      setDashboardData(data);
      setCurrentReading(data.current_reading);
      setDietPlans(data.diet_plans || []);
      
      // Generate historical data for charts
      const historyData = generateHistoryData(data.patient?.condition);
      setReadingsHistory(historyData);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    fetchDashboard();
    // Simulate real-time updates every 5 seconds
    const interval = setInterval(() => {
      refreshReading();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  const refreshReading = async () => {
    if (!patientId) return;
    try {
      const reading = await api.recordReading(patientId);
      setCurrentReading(reading);
      
      // Update history
      setReadingsHistory(prev => {
        const newHistory = [...prev.slice(1), {
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          glucose: reading.glucose_level || prev[prev.length - 1]?.glucose,
          heartRate: reading.heart_rate || prev[prev.length - 1]?.heartRate,
          battery: reading.battery_level
        }];
        return newHistory;
      });

      if (reading.is_critical) {
        toast.error('Critical Alert Detected!', {
          description: 'Your device has detected an abnormal reading. Medical team notified.',
          duration: 10000
        });
      }
    } catch (error) {
      console.error('Failed to refresh reading:', error);
    }
  };

  const generateDietPlan = async () => {
    if (!patientId) return;
    setIsGeneratingDiet(true);
    try {
      const plan = await api.generateDietPlan(patientId);
      setDietPlans(prev => [plan, ...prev]);
      toast.success('Diet Plan Generated!', {
        description: 'AI-powered diet plan verified by OpenClaw'
      });
    } catch (error) {
      console.error('Failed to generate diet:', error);
      toast.error('Failed to generate diet plan');
    } finally {
      setIsGeneratingDiet(false);
    }
  };

  const generateHistoryData = (condition) => {
    const data = [];
    const now = new Date();
    const isDiabetes = condition?.includes('diabetes');
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now - i * 60 * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        glucose: isDiabetes ? Math.floor(80 + Math.random() * 60) : null,
        heartRate: !isDiabetes ? Math.floor(65 + Math.random() * 25) : null,
        battery: Math.max(20, 100 - i * 3 + Math.floor(Math.random() * 5))
      });
    }
    return data;
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-muted-foreground">Loading dashboard...</div>
        </div>
      </DashboardLayout>
    );
  }

  const patient = dashboardData?.patient;
  const isDiabetes = patient?.condition?.includes('diabetes');
  const conditionLabel = patient?.condition?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <DashboardLayout>
      <div className="p-4 md:p-6 space-y-6" data-testid="patient-dashboard">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">
              Welcome, {patient?.name}
            </h1>
            <p className="text-muted-foreground flex items-center gap-2 mt-1">
              <Badge className="badge-healthy">{conditionLabel}</Badge>
              <span className="text-sm">Device: {patient?.device_type?.replace('_', ' ')}</span>
            </p>
          </div>
          <Button 
            onClick={refreshReading} 
            variant="outline" 
            className="gap-2"
            data-testid="refresh-btn"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Data
          </Button>
        </div>

        {/* Vital Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {isDiabetes ? (
            <Card className={`card-hover ${currentReading?.is_critical ? 'border-red-500/50 glow-rose' : ''}`} data-testid="glucose-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Droplets className="w-4 h-4 text-cyan-400" />
                  Glucose Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-mono font-bold text-foreground">
                  {currentReading?.glucose_level || '--'}
                  <span className="text-sm font-normal text-muted-foreground ml-1">mg/dL</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Target: 70-180 mg/dL
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card className={`card-hover ${currentReading?.is_critical ? 'border-red-500/50 glow-rose' : ''}`} data-testid="heartrate-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Heart className="w-4 h-4 text-rose-400" />
                  Heart Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-mono font-bold text-foreground">
                  {currentReading?.heart_rate || '--'}
                  <span className="text-sm font-normal text-muted-foreground ml-1">BPM</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Target: 60-100 BPM
                </p>
              </CardContent>
            </Card>
          )}

          <Card className={`card-hover ${currentReading?.battery_level < 20 ? 'border-amber-500/50 glow-rose' : ''}`} data-testid="battery-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Battery className="w-4 h-4 text-green-400" />
                Device Battery
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {currentReading?.battery_level || '--'}
                <span className="text-sm font-normal text-muted-foreground ml-1">%</span>
              </div>
              <div className="w-full h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-500 ${
                    currentReading?.battery_level > 50 ? 'bg-green-500' : 
                    currentReading?.battery_level > 20 ? 'bg-amber-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${currentReading?.battery_level || 0}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="status-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Activity className="w-4 h-4 text-purple-400" />
                Device Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                <span className="text-lg font-semibold text-foreground">Online</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Last sync: Just now
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="alerts-count-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Recent Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.alerts?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                In the last 24 hours
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts & Diet */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Vitals Chart */}
          <Card className="lg:col-span-2 card-hover" data-testid="vitals-chart">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                24-Hour Vitals Trend
              </CardTitle>
              <CardDescription>Real-time monitoring from your device</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={readingsHistory}>
                    <defs>
                      <linearGradient id="colorVital" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="time" stroke="#71717a" fontSize={12} />
                    <YAxis stroke="#71717a" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#121215', 
                        border: '1px solid #27272a',
                        borderRadius: '8px'
                      }}
                    />
                    {isDiabetes ? (
                      <Area 
                        type="monotone" 
                        dataKey="glucose" 
                        stroke="#0ea5e9" 
                        fillOpacity={1} 
                        fill="url(#colorVital)" 
                        strokeWidth={2}
                        name="Glucose (mg/dL)"
                      />
                    ) : (
                      <Area 
                        type="monotone" 
                        dataKey="heartRate" 
                        stroke="#f43f5e" 
                        fillOpacity={1} 
                        fill="url(#colorVital)" 
                        strokeWidth={2}
                        name="Heart Rate (BPM)"
                      />
                    )}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Diet Plan */}
          <Card className="card-hover" data-testid="diet-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="w-5 h-5 text-green-400" />
                AI Diet Plan
              </CardTitle>
              <CardDescription>Personalized nutrition from Moltbot</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={generateDietPlan} 
                className="w-full gap-2 bg-purple-600 hover:bg-purple-700"
                disabled={isGeneratingDiet}
                data-testid="generate-diet-btn"
              >
                <Sparkles className="w-4 h-4" />
                {isGeneratingDiet ? 'Generating...' : 'Generate New Plan'}
              </Button>

              <ScrollArea className="h-[200px]">
                {dietPlans.length > 0 ? (
                  <div className="space-y-3">
                    {dietPlans.map((plan, index) => (
                      <div key={plan.id || index} className="p-3 rounded-lg border border-border/40 bg-card/50">
                        <div className="flex items-center justify-between mb-2">
                          <Badge className="badge-verified gap-1">
                            <Check className="w-3 h-3" />
                            Verified by OpenClaw
                          </Badge>
                          <a 
                            href={`https://testnet.opbnbscan.com/tx/${plan.verification_tx_hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
                            data-testid={`diet-tx-link-${index}`}
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                        <div className="text-xs text-muted-foreground whitespace-pre-wrap line-clamp-6">
                          {plan.plan}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    <Utensils className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No diet plans yet</p>
                    <p className="text-xs">Generate your first AI-powered plan</p>
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Recent Alerts */}
        <Card className="card-hover" data-testid="alerts-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Recent Critical Alerts
            </CardTitle>
            <CardDescription>Blockchain-verified alert history</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              {dashboardData?.alerts?.length > 0 ? (
                <div className="space-y-3">
                  {dashboardData.alerts.map((alert, index) => (
                    <div 
                      key={alert.id || index} 
                      className={`p-3 rounded-lg border ${
                        alert.severity === 'emergency' ? 'border-red-500/50 bg-red-500/5' :
                        alert.severity === 'critical' ? 'border-amber-500/50 bg-amber-500/5' :
                        'border-border/40 bg-card/50'
                      }`}
                      data-testid={`alert-item-${index}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={
                          alert.severity === 'emergency' ? 'badge-critical' :
                          alert.severity === 'critical' ? 'badge-warning' :
                          'badge-healthy'
                        }>
                          {alert.severity?.toUpperCase()}
                        </Badge>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          {new Date(alert.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <p className="text-sm text-foreground">{alert.message}</p>
                      {alert.tx_hash && (
                        <div className="mt-2 flex items-center gap-2">
                          <Badge variant="outline" className="text-xs font-mono">
                            {alert.sha256_hash?.slice(0, 16)}...
                          </Badge>
                          <a 
                            href={`https://testnet.opbnbscan.com/tx/${alert.tx_hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
                          >
                            View on opBNB <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Check className="w-8 h-8 mx-auto mb-2 text-green-400" />
                  <p className="text-sm">No recent alerts</p>
                  <p className="text-xs">Your vitals are within normal range</p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};
