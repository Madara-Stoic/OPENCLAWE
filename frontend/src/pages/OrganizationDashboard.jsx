import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, Heart, Users, Building2, AlertTriangle, 
  Server, Database, Cpu, RefreshCw, Check, Clock
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import * as api from '@/services/api';
import { toast } from 'sonner';

export const OrganizationDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [moltbotStats, setMoltbotStats] = useState(null);
  const [moltbotActivities, setMoltbotActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboard = useCallback(async () => {
    try {
      const [orgData, stats, activities] = await Promise.all([
        api.getOrganizationDashboard(),
        api.getMoltbotStats(),
        api.getMoltbotActivities(20)
      ]);
      setDashboardData(orgData);
      setMoltbotStats(stats);
      setMoltbotActivities(activities);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    // Refresh every 10 seconds
    const interval = setInterval(fetchDashboard, 10000);
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

  const deviceData = dashboardData?.device_analytics ? [
    { name: 'Insulin Pumps', value: dashboardData.device_analytics.insulin_pumps, color: '#0ea5e9' },
    { name: 'Pacemakers', value: dashboardData.device_analytics.pacemakers, color: '#f43f5e' },
    { name: 'Glucose Monitors', value: dashboardData.device_analytics.glucose_monitors, color: '#10b981' }
  ] : [];

  const hospitalData = dashboardData?.hospitals?.slice(0, 10).map(h => ({
    name: h.name.split(' ')[0],
    devices: h.active_devices,
    capacity: h.capacity
  })) || [];

  const systemHealth = dashboardData?.system_health;

  return (
    <DashboardLayout>
      <div className="p-4 md:p-6 space-y-6" data-testid="organization-dashboard">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">
              Organization Dashboard
            </h1>
            <p className="text-muted-foreground flex items-center gap-2 mt-1">
              <Badge className="badge-healthy">System Healthy</Badge>
              <span className="text-sm">Last updated: Just now</span>
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

        {/* Overview Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="card-hover" data-testid="patients-stat-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                Total Patients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.total_patients || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="doctors-stat-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Activity className="w-4 h-4 text-purple-400" />
                Total Doctors
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.total_doctors || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="hospitals-stat-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Building2 className="w-4 h-4 text-green-400" />
                Hospitals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.total_hospitals || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover" data-testid="alerts-stat-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Total Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-mono font-bold text-foreground">
                {dashboardData?.total_alerts || 0}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Device Distribution */}
          <Card className="card-hover" data-testid="device-chart-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-rose-400" />
                Device Distribution
              </CardTitle>
              <CardDescription>Active medical IoT devices</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[220px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={deviceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {deviceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#121215', 
                        border: '1px solid #27272a',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend 
                      verticalAlign="bottom" 
                      height={36}
                      formatter={(value) => <span className="text-xs text-muted-foreground">{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Hospital Capacity */}
          <Card className="lg:col-span-2 card-hover" data-testid="hospital-chart-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-green-400" />
                Hospital Device Deployment
              </CardTitle>
              <CardDescription>Active devices per hospital (top 10)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[220px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hospitalData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="name" stroke="#71717a" fontSize={10} />
                    <YAxis stroke="#71717a" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#121215', 
                        border: '1px solid #27272a',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="devices" fill="#10b981" radius={[4, 4, 0, 0]} name="Active Devices" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Health & Moltbot */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* System Health */}
          <Card className="card-hover" data-testid="system-health-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="w-5 h-5 text-cyan-400" />
                System Health
              </CardTitle>
              <CardDescription>Infrastructure status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-2">
                    <Cpu className="w-4 h-4" /> Uptime
                  </span>
                  <span className="font-mono text-green-400">{systemHealth?.uptime}</span>
                </div>
                <Progress value={99.9} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-2">
                    <Activity className="w-4 h-4" /> Active Connections
                  </span>
                  <span className="font-mono text-foreground">{systemHealth?.active_connections}</span>
                </div>
                <Progress value={(systemHealth?.active_connections / 300) * 100} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="p-3 rounded-lg border border-border/40 bg-card/50">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                    <Database className="w-3 h-3" /> Data Sync
                  </div>
                  <Badge className="badge-healthy">{systemHealth?.data_sync_status}</Badge>
                </div>
                <div className="p-3 rounded-lg border border-border/40 bg-card/50">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                    <Server className="w-3 h-3" /> Blockchain
                  </div>
                  <Badge className="badge-verified">{systemHealth?.blockchain_sync}</Badge>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-border/40 bg-card/50">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Last Block</span>
                  <span className="font-mono text-cyan-400">#{systemHealth?.last_block?.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Moltbot Activity Feed */}
          <Card className="card-hover" data-testid="moltbot-activity-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-400" />
                Moltbot Activity Feed
              </CardTitle>
              <CardDescription>AI agent actions and verifications</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="p-2 rounded-lg border border-border/40 bg-card/50 text-center">
                  <div className="text-lg font-mono font-bold text-foreground">{moltbotStats?.total_activities || 0}</div>
                  <div className="text-xs text-muted-foreground">Total</div>
                </div>
                <div className="p-2 rounded-lg border border-border/40 bg-card/50 text-center">
                  <div className="text-lg font-mono font-bold text-green-400">{moltbotStats?.diet_suggestions || 0}</div>
                  <div className="text-xs text-muted-foreground">Diets</div>
                </div>
                <div className="p-2 rounded-lg border border-border/40 bg-card/50 text-center">
                  <div className="text-lg font-mono font-bold text-amber-400">{moltbotStats?.alert_verifications || 0}</div>
                  <div className="text-xs text-muted-foreground">Alerts</div>
                </div>
              </div>

              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {moltbotActivities.map((activity, index) => (
                    <div 
                      key={activity.id || index}
                      className="p-3 rounded-lg border border-border/40 bg-card/50"
                      data-testid={`moltbot-activity-${index}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <Badge className={
                          activity.activity_type === 'diet_suggestion' ? 'badge-healthy' :
                          activity.activity_type === 'alert_verification' ? 'badge-warning' :
                          'badge-verified'
                        }>
                          {activity.activity_type?.replace('_', ' ')}
                        </Badge>
                        {activity.verified && (
                          <Badge className="badge-verified gap-1">
                            <Check className="w-3 h-3" /> Verified
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">{activity.description}</p>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        {new Date(activity.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};
