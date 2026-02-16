import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, Heart, Utensils, TrendingUp, Calendar, 
  Play, Check, ExternalLink, AlertTriangle, Sparkles, Clock
} from 'lucide-react';
import * as api from '@/services/api';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const OpenClawSkillsPanel = ({ patientId, patientName }) => {
  const [isRunning, setIsRunning] = useState({});
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState('overview');

  const skills = [
    {
      id: 'critical-monitor',
      name: 'Critical Condition Monitor',
      description: 'Monitors vitals for critical conditions, triggers blockchain verification',
      icon: AlertTriangle,
      color: 'text-rose-400',
      endpoint: `/api/openclaw/skill/critical-monitor/${patientId}`
    },
    {
      id: 'diet-suggestion',
      name: 'AI Diet Suggestion',
      description: 'Generates personalized diet plans based on condition',
      icon: Utensils,
      color: 'text-green-400',
      endpoint: `/api/openclaw/skill/diet-suggestion/${patientId}`
    },
    {
      id: 'realtime-feedback',
      name: 'Real-time Feedback',
      description: 'Provides immediate coaching based on current vitals',
      icon: TrendingUp,
      color: 'text-cyan-400',
      endpoint: `/api/openclaw/skill/realtime-feedback/${patientId}`
    },
    {
      id: 'daily-progress',
      name: 'Daily Progress Tracker',
      description: 'Generates comprehensive daily health reports',
      icon: Calendar,
      color: 'text-purple-400',
      endpoint: `/api/openclaw/skill/daily-progress/${patientId}`
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
      
      if (data.status === 'alert_generated') {
        toast.error('Critical Alert Detected!', {
          description: data.alert?.message || 'Immediate attention required'
        });
      } else {
        toast.success(`${skill.name} Complete`, {
          description: 'Verified by OpenClaw'
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
      const response = await fetch(`${BACKEND_URL}/api/openclaw/run-all/${patientId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      setResults(prev => ({ ...prev, all: data }));
      
      toast.success('All OpenClaw Skills Executed', {
        description: `${data.skills_executed?.length || 0} skills completed`
      });
    } catch (error) {
      console.error('Failed to run all skills:', error);
      toast.error('Failed to run all skills');
    } finally {
      setIsRunning(prev => ({ ...prev, all: false }));
    }
  };

  const renderSkillResult = (skillId) => {
    const result = results[skillId];
    if (!result) return null;

    switch (skillId) {
      case 'critical-monitor':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge className={result.status === 'alert_generated' ? 'badge-critical' : 'badge-healthy'}>
                {result.status === 'alert_generated' ? 'ALERT' : 'NORMAL'}
              </Badge>
              {result.verified_by_openclaw && (
                <Badge className="badge-verified gap-1">
                  <Check className="w-3 h-3" /> Verified
                </Badge>
              )}
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
                {result.explorer_url && (
                  <a 
                    href={result.explorer_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1 mt-1"
                  >
                    View on opBNB <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            )}
          </div>
        );

      case 'diet-suggestion':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge className="badge-healthy">Generated</Badge>
              <Badge className="badge-verified gap-1">
                <Check className="w-3 h-3" /> Verified by OpenClaw
              </Badge>
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
            {result.explorer_url && (
              <a 
                href={result.explorer_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
              >
                View verification on opBNB <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        );

      case 'realtime-feedback':
        return (
          <div className="space-y-2">
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

      case 'daily-progress':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-foreground">
                  {result.overall_health_score?.toFixed(1)}
                </div>
                <div className="text-xs text-muted-foreground">Health Score</div>
              </div>
              <div className="flex-1 grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded bg-secondary/50">
                  <div className="text-muted-foreground">Readings</div>
                  <div className="font-mono">{result.total_readings}</div>
                </div>
                <div className="p-2 rounded bg-secondary/50">
                  <div className="text-muted-foreground">Alerts</div>
                  <div className="font-mono">{result.critical_events}</div>
                </div>
              </div>
            </div>
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="p-2 rounded bg-purple-500/10 border border-purple-500/30 text-sm">
                {result.recommendations[0]}
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
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          OpenClaw Skills
        </CardTitle>
        <CardDescription>
          Autonomous AI agent for {patientName}
        </CardDescription>
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
              className="w-full gap-2 bg-purple-600 hover:bg-purple-700"
              disabled={isRunning.all}
              data-testid="run-all-skills-btn"
            >
              <Play className="w-4 h-4" />
              {isRunning.all ? 'Running All Skills...' : 'Run All Skills'}
            </Button>

            <div className="space-y-2">
              {skills.map((skill) => (
                <div 
                  key={skill.id}
                  className="p-3 rounded-lg border border-border/40 bg-card/50 flex items-center justify-between"
                  data-testid={`skill-${skill.id}`}
                >
                  <div className="flex items-center gap-3">
                    <skill.icon className={`w-5 h-5 ${skill.color}`} />
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
                <div className="mb-4 p-3 rounded-lg border border-purple-500/30 bg-purple-500/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className="badge-verified gap-1">
                      <Check className="w-3 h-3" /> All Skills Complete
                    </Badge>
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
                        <skill.icon className={`w-4 h-4 ${skill.color}`} />
                        <span className="font-medium text-sm">{skill.name}</span>
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
