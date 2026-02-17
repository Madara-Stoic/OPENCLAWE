import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, Heart, Utensils, TrendingUp, Calendar, 
  Play, Check, ExternalLink, AlertTriangle, Sparkles, Clock,
  Shield, Database, Cpu
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// OpenClaw Badge Component
const OpenClawBadge = ({ className = '' }) => (
  <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-gradient-to-r from-purple-600/20 to-cyan-600/20 border border-purple-500/30 ${className}`}>
    <Shield className="w-3 h-3 text-purple-400" />
    <span className="text-xs font-medium bg-gradient-to-r from-purple-400 to-cyan-400 text-transparent bg-clip-text">
      Verified by OpenClaw
    </span>
    <Check className="w-3 h-3 text-cyan-400" />
  </div>
);

// Moltbot Gateway Status Badge
const MoltbotBadge = ({ status = 'active' }) => (
  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">
    <Cpu className="w-3 h-3 text-emerald-400" />
    <span className="text-xs text-emerald-400">Moltbot Gateway</span>
    <span className={`w-1.5 h-1.5 rounded-full ${status === 'active' ? 'bg-emerald-400 animate-pulse' : 'bg-gray-400'}`} />
  </div>
);

export const OpenClawSkillsPanel = ({ patientId, patientName }) => {
  const [isRunning, setIsRunning] = useState({});
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState('overview');
  const [gatewayInfo, setGatewayInfo] = useState(null);

  // Fetch gateway info on mount
  useEffect(() => {
    const fetchGatewayInfo = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/moltbot/gateway`);
        const data = await response.json();
        setGatewayInfo(data);
      } catch (error) {
        console.error('Failed to fetch gateway info:', error);
      }
    };
    fetchGatewayInfo();
  }, []);

  const skills = [
    {
      id: 'critical_condition_monitor',
      name: 'Critical Condition Monitor',
      description: 'Monitors vitals for critical conditions, triggers blockchain verification',
      icon: AlertTriangle,
      color: 'text-rose-400',
      emoji: '🚨',
      endpoint: `/api/moltbot/skill/critical-monitor/${patientId}`
    },
    {
      id: 'ai_diet_suggestion',
      name: 'AI Diet Suggestion',
      description: 'Generates personalized diet plans based on condition',
      icon: Utensils,
      color: 'text-green-400',
      emoji: '🥗',
      endpoint: `/api/moltbot/skill/diet-suggestion/${patientId}`
    },
    {
      id: 'realtime_feedback',
      name: 'Real-time Feedback',
      description: 'Provides immediate coaching based on current vitals',
      icon: TrendingUp,
      color: 'text-cyan-400',
      emoji: '💬',
      endpoint: `/api/moltbot/skill/realtime-feedback/${patientId}`
    },
    {
      id: 'daily_progress_tracker',
      name: 'Daily Progress Tracker',
      description: 'Generates comprehensive daily health reports',
      icon: Calendar,
      color: 'text-purple-400',
      emoji: '📊',
      endpoint: `/api/moltbot/skill/daily-progress/${patientId}`
    }
  ];

  const runSkill = async (skill) => {
    setIsRunning(prev => ({ ...prev, [skill.id]: true }));
    
    try {
      const response = await fetch(`${BACKEND_URL}${skill.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      setResults(prev => ({ ...prev, [skill.id]: data }));
      
      // Check if it's a Moltbot Gateway response
      if (data.result?.status === 'alert_generated') {
        toast.error('Critical Alert Detected!', {
          description: data.result.alert?.message || 'Immediate attention required'
        });
      } else {
        toast.success(`${skill.emoji} ${skill.name} Complete`, {
          description: 'Verified by OpenClaw • Moltbot Gateway'
        });
      }
    } catch (error) {
      console.error(`Failed to run ${skill.name}:`, error);
      toast.error(`Failed to run ${skill.name}`);
    } finally {
      setIsRunning(prev => ({ ...prev, [skill.id]: false }));
    }
  };

  const runAllSkills = async () => {
    setIsRunning(prev => ({ ...prev, all: true }));
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/moltbot/run-all/${patientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      setResults(prev => ({ ...prev, all: data }));
      
      toast.success('All Moltbot Skills Executed', {
        description: `${data.skills_executed?.length || 0} skills completed via OpenClaw Gateway`
      });
    } catch (error) {
      console.error('Failed to run all skills:', error);
      toast.error('Failed to run all skills');
    } finally {
      setIsRunning(prev => ({ ...prev, all: false }));
    }
  };

  const renderSkillResult = (skillId) => {
    const data = results[skillId];
    if (!data) return null;
    
    // Moltbot Gateway returns results wrapped in `result`
    const result = data.result || data;

    switch (skillId) {
      case 'critical_condition_monitor':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={result.status === 'alert_generated' ? 'badge-critical' : 'badge-healthy'}>
                {result.status === 'alert_generated' ? 'ALERT' : 'NORMAL'}
              </Badge>
              {data.verified_by_openclaw && <OpenClawBadge />}
            </div>
            {result.vitals && (
              <div className="grid grid-cols-3 gap-2 text-sm">
                {result.vitals.glucose_level && (
                  <div className="p-2 rounded bg-secondary/50">
                    <div className="text-muted-foreground text-xs">Glucose</div>
                    <div className="font-mono font-bold">{result.vitals.glucose_level} mg/dL</div>
                  </div>
                )}
                {result.vitals.heart_rate && (
                  <div className="p-2 rounded bg-secondary/50">
                    <div className="text-muted-foreground text-xs">Heart Rate</div>
                    <div className="font-mono font-bold">{result.vitals.heart_rate} BPM</div>
                  </div>
                )}
                <div className="p-2 rounded bg-secondary/50">
                  <div className="text-muted-foreground text-xs">Battery</div>
                  <div className="font-mono font-bold">{result.vitals.battery_level}%</div>
                </div>
              </div>
            )}
            {result.alert && (
              <div className="p-2 rounded bg-red-500/10 border border-red-500/30 text-sm">
                <p className="text-red-400">{result.alert.message}</p>
                {result.blockchain?.explorer_url && (
                  <a 
                    href={result.blockchain.explorer_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1 mt-1"
                  >
                    View on opBNB <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            )}
            {data.tx_hash && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Database className="w-3 h-3" />
                <span className="font-mono truncate">{data.tx_hash.slice(0, 20)}...</span>
              </div>
            )}
          </div>
        );

      case 'ai_diet_suggestion':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className="badge-healthy">Generated</Badge>
              {data.verified_by_openclaw && <OpenClawBadge />}
            </div>
            {result.diet_plan && (
              <div className="space-y-2 text-sm">
                {Object.entries(result.diet_plan).slice(0, 2).map(([meal, plan]) => {
                  if (typeof plan !== 'object' || !plan.foods) return null;
                  return (
                    <div key={meal} className="p-2 rounded bg-secondary/50">
                      <div className="font-semibold capitalize text-foreground">{meal}</div>
                      <div className="text-xs text-muted-foreground">
                        {plan.foods?.slice(0, 2).join(', ')}...
                      </div>
                      <div className="text-xs text-green-400 mt-1">{plan.calories} cal</div>
                    </div>
                  );
                })}
              </div>
            )}
            {result.verification?.explorer_url && (
              <a 
                href={result.verification.explorer_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
              >
                View verification on opBNB <ExternalLink className="w-3 h-3" />
              </a>
            )}
            {result.greenfield_cid && (
              <div className="flex items-center gap-2 text-xs text-emerald-400">
                <Database className="w-3 h-3" />
                <span>Stored on BNB Greenfield</span>
              </div>
            )}
          </div>
        );

      case 'realtime_feedback':
        return (
          <div className="space-y-2">
            {data.verified_by_openclaw && (
              <div className="mb-2">
                <OpenClawBadge />
              </div>
            )}
            {result.feedback && (
              <div className="space-y-1">
                {result.feedback.map((fb, i) => (
                  <div key={i} className="p-2 rounded bg-secondary/50 text-sm">
                    {fb}
                  </div>
                ))}
              </div>
            )}
            {result.coaching_tips && result.coaching_tips.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">Coaching Tips:</div>
                {result.coaching_tips.slice(0, 2).map((tip, i) => (
                  <div key={i} className="text-xs text-cyan-400">{tip}</div>
                ))}
              </div>
            )}
          </div>
        );

      case 'daily_progress_tracker':
        return (
          <div className="space-y-2">
            {data.verified_by_openclaw && (
              <div className="mb-2">
                <OpenClawBadge />
              </div>
            )}
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-foreground">
                  {result.health_score?.toFixed(1) || result.overall_health_score?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-xs text-muted-foreground">Health Score</div>
              </div>
              <div className="flex-1 grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded bg-secondary/50">
                  <div className="text-muted-foreground">Readings</div>
                  <div className="font-mono">{result.metrics?.total_readings || result.total_readings || 0}</div>
                </div>
                <div className="p-2 rounded bg-secondary/50">
                  <div className="text-muted-foreground">Alerts</div>
                  <div className="font-mono">{result.metrics?.critical_events || result.critical_events || 0}</div>
                </div>
              </div>
            </div>
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="p-2 rounded bg-purple-500/10 border border-purple-500/30 text-sm">
                {result.recommendations[0]}
              </div>
            )}
            {result.greenfield_cid && (
              <div className="flex items-center gap-2 text-xs text-emerald-400">
                <Database className="w-3 h-3" />
                <span>Stored on BNB Greenfield</span>
              </div>
            )}
          </div>
        );

      default:
        return <pre className="text-xs overflow-auto">{JSON.stringify(result, null, 2)}</pre>;
    }
  };

  return (
    <Card className="card-hover" data-testid="openclaw-skills-panel">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              Moltbot Skills
            </CardTitle>
            <CardDescription>
              OpenClaw-powered AI agent for {patientName}
            </CardDescription>
          </div>
          <MoltbotBadge status={gatewayInfo?.status || 'active'} />
        </div>
        {gatewayInfo && (
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="text-xs">
              v{gatewayInfo.version}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {gatewayInfo.skills_loaded} skills loaded
            </Badge>
            <Badge variant="outline" className="text-xs text-emerald-400 border-emerald-500/30">
              {gatewayInfo.storage}
            </Badge>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-3">
            <Button 
              onClick={runAllSkills}
              className="w-full gap-2 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700"
              disabled={isRunning.all}
              data-testid="run-all-skills-btn"
            >
              <Play className="w-4 h-4" />
              {isRunning.all ? 'Running All Skills...' : 'Run All Moltbot Skills'}
            </Button>

            <div className="space-y-2">
              {skills.map((skill) => (
                <div 
                  key={skill.id}
                  className="p-3 rounded-lg border border-border/40 bg-card/50 flex items-center justify-between"
                  data-testid={`skill-${skill.id}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="text-xl">{skill.emoji}</div>
                    <div>
                      <div className="font-medium text-sm text-foreground">{skill.name}</div>
                      <div className="text-xs text-muted-foreground">{skill.description}</div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => runSkill(skill)}
                    disabled={isRunning[skill.id]}
                    data-testid={`run-${skill.id}-btn`}
                  >
                    {isRunning[skill.id] ? (
                      <Activity className="w-4 h-4 animate-spin" />
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="results">
            <ScrollArea className="h-[300px]">
              {results.all && (
                <div className="mb-4 p-3 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/5 to-cyan-500/5">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <OpenClawBadge />
                    <span className="text-xs text-muted-foreground">
                      {results.all.skills_executed?.length} skills executed
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(results.all.timestamp).toLocaleString()}
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {skills.map((skill) => (
                  results[skill.id] && (
                    <div 
                      key={skill.id}
                      className="p-3 rounded-lg border border-border/40 bg-card/50"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">{skill.emoji}</span>
                        <span className="font-medium text-sm">{skill.name}</span>
                        {results[skill.id].execution_time_ms && (
                          <span className="text-xs text-muted-foreground ml-auto">
                            {results[skill.id].execution_time_ms}ms
                          </span>
                        )}
                      </div>
                      {renderSkillResult(skill.id)}
                    </div>
                  )
                ))}
              </div>

              {Object.keys(results).length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No results yet</p>
                  <p className="text-xs">Run skills to see results here</p>
                </div>
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
