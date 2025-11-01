import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const GoogleOAuthHandler = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing'); // 'processing', 'success', 'error'
  const [error, setError] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      // Handle OAuth errors
      setStatus('error');
      const errorMessages = {
        'invalid_oauth_state': 'Invalid or expired authentication request. Please try again.',
        'google_token_exchange_failed': 'Failed to authenticate with Google. Please try again.',
        'no_access_token': 'Authentication failed. Please try again.',
        'google_userinfo_failed': 'Failed to retrieve your Google account information.',
        'missing_google_user_info': 'Incomplete authentication. Please try again.',
        'oauth_callback_error': 'An error occurred during authentication. Please try again.'
      };
      setError(errorMessages[errorParam] || 'Authentication failed. Please try again.');
      toast.error('Google authentication failed');
      return;
    }

    if (token) {
      // Store token in localStorage
      localStorage.setItem('access_token', token);
      
      // Try to get user info from token (decode JWT - simple decode, not verification)
      try {
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));
          const userData = {
            id: payload.sub,
            email: payload.email,
            auth_provider: payload.auth_provider || 'google'
          };
          localStorage.setItem('user', JSON.stringify(userData));
        }
      } catch (e) {
        console.warn('Could not decode token payload:', e);
      }

      setStatus('success');
      toast.success('Successfully signed in with Google!');
      
      // Redirect to dashboard after 1 second
      setTimeout(() => {
        navigate('/admin', { replace: true });
      }, 1000);
    } else {
      setStatus('error');
      setError('No authentication token received. Please try again.');
    }
  }, [searchParams, navigate]);

  const renderContent = () => {
    switch (status) {
      case 'processing':
        return (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <p className="text-gray-600">Processing authentication...</p>
          </div>
        );

      case 'success':
        return (
          <div className="flex flex-col items-center space-y-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <p className="text-gray-600">Successfully authenticated! Redirecting...</p>
          </div>
        );

      case 'error':
        return (
          <div className="space-y-4">
            <div className="flex flex-col items-center space-y-4">
              <XCircle className="w-8 h-8 text-red-600" />
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </div>
            <div className="flex gap-2 justify-center">
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Try Again
              </button>
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Go Home
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Google Authentication</CardTitle>
          <CardDescription>Completing your sign-in</CardDescription>
        </CardHeader>
        <CardContent>
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
};

export default GoogleOAuthHandler;

