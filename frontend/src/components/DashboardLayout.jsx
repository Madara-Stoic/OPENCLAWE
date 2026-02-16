import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { 
  Activity, Heart, LogOut, Menu, User, Stethoscope, 
  Building2, Wallet, ExternalLink, Bell, Check, Clock
} from 'lucide-react';
import * as api from '@/services/api';

export const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const [moltbotActivities, setMoltbotActivities] = useState([]);
  const [isActivityOpen, setIsActivityOpen] = useState(false);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const activities = await api.getMoltbotActivities(10);
        setMoltbotActivities(activities);
      } catch (error) {
        console.error('Failed to fetch activities:', error);
      }
    };
    fetchActivities();
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
  }, []);

  const getRoleIcon = () => {
    switch (user?.role) {
      case 'patient':
        return <User className="w-4 h-4" />;
      case 'doctor':
        return <Stethoscope className="w-4 h-4" />;
      case 'organization':
        return <Building2 className="w-4 h-4" />;
      default:
        return <User className="w-4 h-4" />;
    }
  };

  const getRoleColor = () => {
    switch (user?.role) {
      case 'patient':
        return 'text-cyan-400';
      case 'doctor':
        return 'text-green-400';
      case 'organization':
        return 'text-purple-400';
      default:
        return 'text-foreground';
    }
  };

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                  <Heart className="w-5 h-5 text-cyan-400" />
                </div>
                <span className="font-bold text-lg text-foreground hidden sm:inline">
                  OmniHealth
                </span>
              </div>
              <Badge className={`${getRoleColor()} bg-transparent border-current/30`}>
                {getRoleIcon()}
                <span className="ml-1 capitalize">{user?.role}</span>
              </Badge>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              {/* Moltbot Activity */}
              <Sheet open={isActivityOpen} onOpenChange={setIsActivityOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="relative" data-testid="moltbot-btn">
                    <Activity className="w-5 h-5 text-purple-400" />
                    {moltbotActivities.length > 0 && (
                      <span className="absolute -top-1 -right-1 w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-[350px] bg-card border-border">
                  <SheetHeader>
                    <SheetTitle className="flex items-center gap-2 text-foreground">
                      <Activity className="w-5 h-5 text-purple-400" />
                      Moltbot Activity
                    </SheetTitle>
                  </SheetHeader>
                  <ScrollArea className="h-[calc(100vh-100px)] mt-4">
                    <div className="space-y-3 pr-4">
                      {moltbotActivities.map((activity, index) => (
                        <div 
                          key={activity.id || index}
                          className="p-3 rounded-lg border border-border/40 bg-background/50"
                          data-testid={`activity-item-${index}`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <Badge className={
                              activity.activity_type === 'diet_suggestion' ? 'badge-healthy' :
                              'badge-warning'
                            }>
                              {activity.activity_type?.replace('_', ' ')}
                            </Badge>
                            {activity.verified && (
                              <Badge className="badge-verified gap-1">
                                <Check className="w-3 h-3" /> Verified
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {activity.description}
                          </p>
                          {activity.tx_hash && (
                            <a 
                              href={`https://testnet.opbnbscan.com/tx/${activity.tx_hash}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-cyan-400 hover:underline flex items-center gap-1 mt-2"
                            >
                              View on opBNB <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                          <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {new Date(activity.timestamp).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </SheetContent>
              </Sheet>

              {/* Wallet Info */}
              {user?.wallet && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="hidden md:flex gap-2 font-mono text-xs"
                  data-testid="wallet-btn"
                >
                  <Wallet className="w-4 h-4" />
                  {user.wallet.address?.slice(0, 6)}...{user.wallet.address?.slice(-4)}
                </Button>
              )}

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" data-testid="user-menu-btn">
                    <Avatar className="h-8 w-8 border border-border">
                      <AvatarFallback className="bg-secondary text-foreground">
                        {user?.name?.charAt(0) || 'U'}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-card border-border">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium text-foreground">{user?.name}</p>
                      <p className="text-xs text-muted-foreground">{user?.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-border" />
                  {user?.wallet && (
                    <>
                      <DropdownMenuItem className="text-xs font-mono text-muted-foreground">
                        <Wallet className="w-4 h-4 mr-2" />
                        {user.wallet.address?.slice(0, 10)}...
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-xs">
                        <Badge variant="outline" className="text-xs">
                          {user.wallet.network}
                        </Badge>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator className="bg-border" />
                    </>
                  )}
                  <DropdownMenuItem 
                    onClick={logout}
                    className="text-red-400 focus:text-red-400 focus:bg-red-400/10"
                    data-testid="logout-btn"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-6 mt-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-cyan-400" />
              <span>OmniHealth Guardian</span>
              <Badge variant="outline" className="text-xs">v1.0.0</Badge>
            </div>
            <div className="flex items-center gap-4">
              <span>Powered by opBNB & OpenClaw</span>
              <a 
                href="https://testnet.opbnbscan.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-cyan-400 hover:underline flex items-center gap-1"
              >
                Explorer <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
