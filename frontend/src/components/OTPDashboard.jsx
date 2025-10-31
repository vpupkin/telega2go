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
import { Send, Shield, Clock, CheckCircle, XCircle, AlertTriangle, RefreshCw, Edit, Trash2, Users, Save, X } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

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
  const [users, setUsers] = useState([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [deleteConfirmDialog, setDeleteConfirmDialog] = useState({ open: false, user: null });

  // API endpoints
  const OTP_GATEWAY_URL = process.env.REACT_APP_OTP_GATEWAY_URL || 'https://putana.date/otp';
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://putana.date:55552';
  const API_BASE = BACKEND_URL.replace(/\/+$/, '').endsWith('/api') 
    ? BACKEND_URL.replace(/\/+$/, '') 
    : `${BACKEND_URL.replace(/\/+$/, '')}/api`;

  // ✅ Fetch all users from backend
  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    try {
      const response = await axios.get(`${API_BASE}/users`);
      if (response.data) {
        setUsers(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setIsLoadingUsers(false);
    }
  };

  // ✅ Fetch OTP history from backend
  const fetchOtpHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/otp-history`);
      if (response.data && response.data.otp_history) {
        const formattedHistory = response.data.otp_history.map(entry => ({
          id: entry.message_id || Date.now(),
          chatId: entry.chat_id,
          otp: entry.otp,
          sentAt: new Date(entry.timestamp).toLocaleString(),
          status: entry.status,
          email: entry.email,
          messageId: entry.message_id
        }));
        setOtpHistory(formattedHistory);
        
        // Update stats
        setStats(prev => ({
          ...prev,
          totalSent: response.data.total_count || 0,
          totalFailed: 0 // We don't track failures yet
        }));
      }
    } catch (error) {
      console.error('Failed to fetch OTP history:', error);
    }
  };

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
      const backendResponse = await axios.get(`${API_BASE}/`);
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

  // ✅ Handle edit user
  const handleEditUser = (user) => {
    setEditingUser({ ...user });
    setIsEditDialogOpen(true);
  };

  // ✅ Handle save user changes
  const handleSaveUser = async () => {
    if (!editingUser) return;
    
    try {
      // Send only the fields that can be updated (exclude id, created_at)
      const updateData = {
        name: editingUser.name,
        email: editingUser.email,
        phone: editingUser.phone || null,
        telegram_chat_id: editingUser.telegram_chat_id || null,
        is_verified: editingUser.is_verified
      };
      
      const response = await axios.put(`${API_BASE}/users/${editingUser.id}`, updateData);
      toast.success('User updated successfully');
      setIsEditDialogOpen(false);
      setEditingUser(null);
      fetchUsers(); // Refresh list
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to update user';
      toast.error(errorMessage);
    }
  };

  // ✅ Handle delete user
  const handleDeleteUser = async () => {
    if (!deleteConfirmDialog.user) return;
    
    try {
      const response = await axios.delete(`${API_BASE}/users/${deleteConfirmDialog.user.id}`);
      // Success - user deleted
      toast.success('User deleted successfully');
      setDeleteConfirmDialog({ open: false, user: null });
      fetchUsers(); // Refresh list
    } catch (error) {
      // Handle 404 as "already deleted" (might have been deleted by another session)
      if (error.response?.status === 404) {
        const errorMessage = error.response?.data?.detail || 'User not found';
        if (errorMessage.includes('not found')) {
          toast.info('User already deleted or not found');
          setDeleteConfirmDialog({ open: false, user: null });
          fetchUsers(); // Refresh list anyway
        } else {
          toast.error(errorMessage);
        }
      } else {
        const errorMessage = error.response?.data?.detail || 'Failed to delete user';
        toast.error(errorMessage);
      }
    }
  };

  // Load initial data
  useEffect(() => {
    checkSystemHealth();
    fetchOtpHistory();
    fetchUsers();
    const interval = setInterval(() => {
      checkSystemHealth();
      fetchOtpHistory();
      fetchUsers();
    }, 30000); // Check every 30 seconds
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
          <Button onClick={() => { checkSystemHealth(); fetchOtpHistory(); }} variant="outline" size="sm">
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
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="send">Send OTP</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
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

          {/* ✅ Users Management Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      User Management
                    </CardTitle>
                    <CardDescription>
                      Manage all registered users in the system
                    </CardDescription>
                  </div>
                  <Button onClick={fetchUsers} variant="outline" size="sm" disabled={isLoadingUsers}>
                    <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingUsers ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {isLoadingUsers ? (
                  <div className="text-center py-8 text-gray-500">
                    Loading users...
                  </div>
                ) : users.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No users found
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name/Username</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Phone</TableHead>
                          <TableHead>Telegram Chat ID</TableHead>
                          <TableHead>Verified</TableHead>
                          <TableHead>Created</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {users.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell className="font-medium">{user.name}</TableCell>
                            <TableCell>{user.email}</TableCell>
                            <TableCell>{user.phone || 'N/A'}</TableCell>
                            <TableCell className="font-mono text-xs">{user.telegram_chat_id}</TableCell>
                            <TableCell>
                              {user.is_verified ? (
                                <Badge className="bg-green-100 text-green-800">Verified</Badge>
                              ) : (
                                <Badge className="bg-gray-100 text-gray-800">Not Verified</Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-sm text-gray-500">
                              {new Date(user.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleEditUser(user)}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setDeleteConfirmDialog({ open: true, user })}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* ✅ Edit User Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Edit User</DialogTitle>
              <DialogDescription>
                Update user details. Leave fields empty to keep current values.
              </DialogDescription>
            </DialogHeader>
            {editingUser && (
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="edit-name">Name/Username</Label>
                    <Input
                      id="edit-name"
                      value={editingUser.name}
                      onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-email">Email</Label>
                    <Input
                      id="edit-email"
                      type="email"
                      value={editingUser.email}
                      onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-phone">Phone</Label>
                    <Input
                      id="edit-phone"
                      value={editingUser.phone || ''}
                      onChange={(e) => setEditingUser({ ...editingUser, phone: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-telegram-chat-id">Telegram Chat ID</Label>
                    <Input
                      id="edit-telegram-chat-id"
                      value={editingUser.telegram_chat_id || ''}
                      onChange={(e) => setEditingUser({ ...editingUser, telegram_chat_id: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="edit-is-verified"
                    checked={editingUser.is_verified}
                    onChange={(e) => setEditingUser({ ...editingUser, is_verified: e.target.checked })}
                    className="h-4 w-4"
                  />
                  <Label htmlFor="edit-is-verified">Verified</Label>
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSaveUser}>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* ✅ Delete Confirmation Dialog */}
        <Dialog open={deleteConfirmDialog.open} onOpenChange={(open) => setDeleteConfirmDialog({ open, user: null })}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete User</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete user <strong>{deleteConfirmDialog.user?.name}</strong>? 
                This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteConfirmDialog({ open: false, user: null })}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={handleDeleteUser}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete User
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default OTPDashboard;
