import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { Send, Shield, Clock, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const OTPDashboard = () => {
  const [otpData, setOtpData] = useState({
    chatId: '',
    otp: '',
    expireSeconds: 30
  });
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    otpGateway: 'unknown',
    backend: 'unknown',
    mongodb: 'unknown'
  });
  const [otpHistory, setOtpHistory] = useState([]);
  const [stats, setStats] = useState({
    totalSent: 0,
    totalFailed: 0,
    rateLimitRemaining: 5
  });

  // API endpoints
  const OTP_GATEWAY_URL = process.env.REACT_APP_OTP_GATEWAY_URL || 'http://localhost:5571';
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5572';

  // Check system health
  const checkSystemHealth = async () => {
    try {
      // Check OTP Gateway
      const otpResponse = await axios.get(`${OTP_GATEWAY_URL}/health`);
      setSystemStatus(prev => ({ ...prev, otpGateway: 'healthy' }));
    } catch (error) {
      setSystemStatus(prev => ({ ...prev, otpGateway: 'error' }));
    }

    try {
      // Check Backend
      const backendResponse = await axios.get(`${BACKEND_URL}/api/`);
      setSystemStatus(prev => ({ ...prev, backend: 'healthy' }));
    } catch (error) {
      setSystemStatus(prev => ({ ...prev, backend: 'error' }));
    }

    // MongoDB status (assumed healthy if backend is healthy)
    setSystemStatus(prev => ({ 
      ...prev, 
      mongodb: prev.backend === 'healthy' ? 'healthy' : 'error' 
    }));
  };

  // Send OTP
  const sendOTP = async () => {
    if (!otpData.chatId || !otpData.otp) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${OTP_GATEWAY_URL}/send-otp`, {
        chat_id: otpData.chatId,
        otp: otpData.otp,
        expire_seconds: otpData.expireSeconds
      });

      if (response.data.success) {
        toast.success('OTP sent successfully!');
        
        // Add to history
        const newEntry = {
          id: Date.now(),
          chatId: otpData.chatId,
          otp: otpData.otp,
          sentAt: new Date().toLocaleString(),
          expireSeconds: otpData.expireSeconds,
          status: 'sent',
          messageId: response.data.message_id
        };
        setOtpHistory(prev => [newEntry, ...prev.slice(0, 9)]); // Keep last 10
        
        // Update stats
        setStats(prev => ({ ...prev, totalSent: prev.totalSent + 1 }));
        
        // Clear form
        setOtpData({ chatId: '', otp: '', expireSeconds: 30 });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to send OTP';
      toast.error(errorMessage);
      
      // Update stats
      setStats(prev => ({ ...prev, totalFailed: prev.totalFailed + 1 }));
    } finally {
      setIsLoading(false);
    }
  };

  // Generate random OTP
  const generateOTP = () => {
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    setOtpData(prev => ({ ...prev, otp }));
  };

  // Load initial data
  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">OTP Social Gateway</h1>
            <p className="text-gray-600">Send secure OTPs via Telegram with auto-delete</p>
          </div>
          <Button onClick={checkSystemHealth} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Status
          </Button>
        </div>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.otpGateway)}
                  <span className="font-medium">OTP Gateway</span>
                </div>
                <Badge className={getStatusColor(systemStatus.otpGateway)}>
                  {systemStatus.otpGateway}
                </Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.backend)}
                  <span className="font-medium">Backend API</span>
                </div>
                <Badge className={getStatusColor(systemStatus.backend)}>
                  {systemStatus.backend}
                </Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.mongodb)}
                  <span className="font-medium">MongoDB</span>
                </div>
                <Badge className={getStatusColor(systemStatus.mongodb)}>
                  {systemStatus.mongodb}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <Tabs defaultValue="send" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="send">Send OTP</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
          </TabsList>

          {/* Send OTP Tab */}
          <TabsContent value="send">
            <Card>
              <CardHeader>
                <CardTitle>Send OTP via Telegram</CardTitle>
                <CardDescription>
                  Send a secure OTP that will auto-delete after the specified time
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="chatId">Telegram Chat ID *</Label>
                      <Input
                        id="chatId"
                        placeholder="123456789"
                        value={otpData.chatId}
                        onChange={(e) => setOtpData(prev => ({ ...prev, chatId: e.target.value }))}
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        Get your Chat ID from @userinfobot on Telegram
                      </p>
                    </div>

                    <div>
                      <Label htmlFor="otp">OTP Code *</Label>
                      <div className="flex gap-2">
                        <Input
                          id="otp"
                          placeholder="123456"
                          value={otpData.otp}
                          onChange={(e) => setOtpData(prev => ({ ...prev, otp: e.target.value }))}
                          maxLength={8}
                        />
                        <Button onClick={generateOTP} variant="outline">
                          Generate
                        </Button>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        4-8 digits only
                      </p>
                    </div>

                    <div>
                      <Label htmlFor="expireSeconds">Auto-delete after (seconds)</Label>
                      <Select
                        value={otpData.expireSeconds.toString()}
                        onValueChange={(value) => setOtpData(prev => ({ ...prev, expireSeconds: parseInt(value) }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="5">5 seconds</SelectItem>
                          <SelectItem value="10">10 seconds</SelectItem>
                          <SelectItem value="15">15 seconds</SelectItem>
                          <SelectItem value="30">30 seconds</SelectItem>
                          <SelectItem value="45">45 seconds</SelectItem>
                          <SelectItem value="60">60 seconds</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Rate Limit Status</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Remaining this hour:</span>
                          <span className="font-medium">{stats.rateLimitRemaining}/5</span>
                        </div>
                        <Progress value={(stats.rateLimitRemaining / 5) * 100} className="h-2" />
                      </div>
                    </div>

                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Security Notice:</strong> OTPs are never stored and messages auto-delete for maximum security.
                      </AlertDescription>
                    </Alert>
                  </div>
                </div>

                <Separator />

                <div className="flex justify-end">
                  <Button 
                    onClick={sendOTP} 
                    disabled={isLoading || !otpData.chatId || !otpData.otp}
                    className="min-w-[120px]"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send OTP
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>OTP History</CardTitle>
                <CardDescription>
                  Recent OTP sends (last 10 entries)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {otpHistory.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No OTPs sent yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {otpHistory.map((entry) => (
                      <div key={entry.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <div>
                            <p className="font-medium">Chat ID: {entry.chatId}</p>
                            <p className="text-sm text-gray-500">OTP: {entry.otp}</p>
                          </div>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>{entry.sentAt}</p>
                          <p>Expires in {entry.expireSeconds}s</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Statistics Tab */}
          <TabsContent value="stats">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Sent</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalSent}</div>
                  <p className="text-xs text-gray-500">OTPs successfully sent</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Failed</CardTitle>
                  <XCircle className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalFailed}</div>
                  <p className="text-xs text-gray-500">Failed attempts</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <Clock className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {stats.totalSent + stats.totalFailed > 0 
                      ? Math.round((stats.totalSent / (stats.totalSent + stats.totalFailed)) * 100)
                      : 0}%
                  </div>
                  <p className="text-xs text-gray-500">Delivery success rate</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default OTPDashboard;
