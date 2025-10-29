import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const MagicLinkVerification = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://putana.date:55552";
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError('No verification token provided');
      return;
    }

    verifyMagicLink();
  }, [token]);

  const verifyMagicLink = async () => {
    try {
      setStatus('verifying');
      
      const response = await axios.post(`${BACKEND_URL}/api/verify-magic-link`, null, {
        params: { token }
      });

      if (response.data.access_token) {
        // Store the token in localStorage
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        setUser(response.data.user);
        setStatus('success');
        toast.success('Registration completed successfully!');
        
        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          navigate('/admin');
        }, 3000);
      }
    } catch (error) {
      console.error('Magic link verification failed:', error);
      setStatus('error');
      setError(error.response?.data?.detail || 'Verification failed');
      toast.error('Magic link verification failed');
    }
  };

  const renderContent = () => {
    switch (status) {
      case 'verifying':
        return (
          <div className="text-center space-y-4">
            <Loader2 className="h-12 w-12 animate-spin mx-auto text-blue-500" />
            <h3 className="text-xl font-semibold">Verifying your registration...</h3>
            <p className="text-muted-foreground">
              Please wait while we complete your registration.
            </p>
          </div>
        );

      case 'success':
        return (
          <div className="text-center space-y-4">
            <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
            <h3 className="text-2xl font-semibold text-green-600">🎉 Registration Complete!</h3>
            <p className="text-muted-foreground">
              Welcome to Telega2Go! Your account has been successfully verified.
            </p>
            {user && (
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="font-medium">Welcome, {user.name}!</p>
                <p className="text-sm text-muted-foreground">{user.email}</p>
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              Redirecting to dashboard in a few seconds...
            </p>
            <Button 
              onClick={() => navigate('/admin')} 
              className="w-full"
            >
              Go to Dashboard
            </Button>
          </div>
        );

      case 'error':
        return (
          <div className="text-center space-y-4">
            <XCircle className="h-12 w-12 mx-auto text-red-500" />
            <h3 className="text-xl font-semibold text-red-600">Verification Failed</h3>
            <Alert variant="destructive">
              <AlertDescription>
                {error || 'An error occurred during verification. Please try again.'}
              </AlertDescription>
            </Alert>
            <div className="space-y-2">
              <Button 
                onClick={() => navigate('/')} 
                variant="outline" 
                className="w-full"
              >
                Back to Registration
              </Button>
              <Button 
                onClick={verifyMagicLink} 
                className="w-full"
              >
                Try Again
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center">Telega2Go</CardTitle>
          <CardDescription className="text-center">
            Magic Link Verification
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
};

export default MagicLinkVerification;
