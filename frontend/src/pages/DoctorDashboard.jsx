import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  Activity, Heart, Users, AlertTriangle, 
  ExternalLink, RefreshCw, Clock, User, Droplets
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import * as api from '@/services/api';
import { toast } from 'sonner';

export const DoctorDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [telemetryData, setTelemetryData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const doctorId = user?.doctorId;

  const fetchDashboard = useCallback(async () => {
    if (!doctorId) return;
    try {
      const [data, telemetry] = await Promise.all([
        api.getDoctorDashboard(doctorId),
        api.getLiveTelemetry()
      ]);
      setDashboardData(data);
      setTelemetryData(telemetry);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, [doctorId]);

  useEffect(() => {
    fetchDashboard();
    // Refresh telemetry every 5 seconds
    const interval = setInterval(async () => {
      try {
        const telemetry = await api.getLiveTelemetry();
        setTelemetryData(telemetry);
      } catch (error) {
        console.error('Failed to refresh telemetry:', error);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-muted-foreground">Loading dashboard...</div>
        </div>
      </DashboardLayout>
    );
  }

  const doctor = dashboardData?.doctor;
  const patients = dashboardData?.patients || [];
  const alerts = dashboardData?.alerts || [];

  // Prepare chart data
  const conditionDistribution = [
    { name: 'Type 1', count: patients.filter(p => p.condition === 'diabetes_type1').length },
    { name: 'Type 2', count: patients.filter(p => p.condition === 'diabetes_type2').length },
    { name: 'Heart', count: patients.filter(p => p.condition === 'heart_condition').length }
  ];

  return (
    <DashboardLayout>
      <div className="p-4 md:p-6 space-y-6" data-testid="doctor-dashboard">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">
              {doctor?.name}
            </h1>
            <p className="text-muted-foreground flex items-center gap-2 mt-1">
              <Badge className="badge-healthy">{doctor?.specialization}</Badge>
            </p>
          </div>
          <Button 
            onClick={fetchDashboard} 
            variant="outline" 
            className="gap-2"
            data-testid="refresh-btn"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Data
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="card-hover" data-testid="total-patients-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                Total Patients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {patients.length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Under your care
              </p>
            </CardContent>
          </Card>

          <Card className={`card-hover ${dashboardData?.critical_patients > 0 ? 'border-red-500/50' : ''}`} data-testid="critical-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                Critical Patients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.critical_patients || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Requiring attention
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="alerts-today-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Activity className="w-4 h-4 text-amber-400" />
                Alerts Today
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {alerts.length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Verified on blockchain
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="devices-online-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Heart className="w-4 h-4 text-green-400" />
                Devices Online
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {patients.length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                All devices connected
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Live Patient Telemetry */}
          <Card className="lg:col-span-2 card-hover" data-testid="live-telemetry-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                Live Patient Telemetry
              </CardTitle>
              <CardDescription>Real-time device readings (updates every 5s)</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[350px]">
                <div className="space-y-3">
                  {telemetryData.map((reading, index) => {
                    const isDiabetes = reading.condition?.includes('diabetes');
                    return (
                      <div 
                        key={reading.patient_id || index}
                        className={`p-4 rounded-lg border ${
                          reading.is_critical ? 'border-red-500/50 bg-red-500/5 animate-pulse-alert' : 
                          'border-border/40 bg-card/50'
                        } card-hover`}
                        data-testid={`telemetry-item-${index}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10 border border-border">
                              <AvatarFallback className="bg-secondary text-foreground">
                                {reading.patient_name?.split(' ').map(n => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium text-foreground">{reading.patient_name}</div>
                              <div className="text-xs text-muted-foreground">
                                {reading.condition?.replace(/_/g, ' ')}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            {isDiabetes && reading.glucose_level && (
                              <div className="text-right">
                                <div className="flex items-center gap-1 text-cyan-400">
                                  <Droplets className="w-4 h-4" />
                                  <span className="font-mono font-bold">{reading.glucose_level}</span>
                                </div>
                                <div className="text-xs text-muted-foreground">mg/dL</div>
                              </div>
                            )}
                            {!isDiabetes && reading.heart_rate && (
                              <div className="text-right">
                                <div className="flex items-center gap-1 text-rose-400">
                                  <Heart className="w-4 h-4" />
                                  <span className="font-mono font-bold">{reading.heart_rate}</span>
                                </div>
                                <div className="text-xs text-muted-foreground">BPM</div>
                              </div>
                            )}
                            <div className="text-right">
                              <div className={`font-mono font-bold ${
                                reading.battery_level > 50 ? 'text-green-400' :
                                reading.battery_level > 20 ? 'text-amber-400' : 'text-red-400'
                              }`}>
                                {reading.battery_level}%
                              </div>
                              <div className="text-xs text-muted-foreground">Battery</div>
                            </div>
                            {reading.is_critical && (
                              <Badge className="badge-critical">CRITICAL</Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Condition Distribution */}
          <Card className="card-hover" data-testid="condition-chart-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-400" />
                Patient Conditions
              </CardTitle>
              <CardDescription>Distribution by condition type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={conditionDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="name" stroke="#71717a" fontSize={12} />
                    <YAxis stroke="#71717a" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#121215', 
                        border: '1px solid #27272a',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Alert Logs */}
        <Card className="card-hover" data-testid="alert-logs-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Alert Logs
            </CardTitle>
            <CardDescription>Blockchain-verified critical events</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[250px]">
              {alerts.length > 0 ? (
                <div className="space-y-3">
                  {alerts.map((alert, index) => (
                    <div 
                      key={alert.id || index}
                      className={`p-4 rounded-lg border ${
                        alert.severity === 'emergency' ? 'border-red-500/50 bg-red-500/5' :
                        alert.severity === 'critical' ? 'border-amber-500/50 bg-amber-500/5' :
                        'border-border/40 bg-card/50'
                      }`}
                      data-testid={`alert-log-${index}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Avatar className="h-8 w-8 border border-border">
                            <AvatarFallback className="bg-secondary text-foreground text-xs">
                              {alert.patient_name?.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <span className="font-medium text-foreground">{alert.patient_name}</span>
                            <Badge className={`ml-2 ${
                              alert.severity === 'emergency' ? 'badge-critical' :
                              alert.severity === 'critical' ? 'badge-warning' :
                              'badge-healthy'
                            }`}>
                              {alert.severity?.toUpperCase()}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          {new Date(alert.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <p className="text-sm text-foreground mb-2">{alert.message}</p>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-xs font-mono">
                          Hash: {alert.sha256_hash?.slice(0, 20)}...
                        </Badge>
                        {alert.tx_hash && (
                          <a 
                            href={`https://testnet.opbnbscan.com/tx/${alert.tx_hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
                          >
                            Verify on opBNB <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                      {alert.nearest_hospital && (
                        <div className="mt-2 p-2 rounded bg-secondary/50 text-xs">
                          <span className="text-muted-foreground">Nearest Hospital: </span>
                          <span className="text-foreground">{alert.nearest_hospital.name}</span>
                          <span className="text-muted-foreground"> ({alert.nearest_hospital.distance})</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Activity className="w-8 h-8 mx-auto mb-2 text-green-400" />
                  <p className="text-sm">No alerts recorded</p>
                  <p className="text-xs">All patients are stable</p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};
