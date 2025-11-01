import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import GoogleLoginButton from './GoogleLoginButton';
import { MessageCircle, ArrowRight } from 'lucide-react';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleTelegramLogin = () => {
    // Redirect to Telegram bot or registration
    navigate('/registrationOfNewUser');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold text-white">P</span>
          </div>
          <CardTitle className="text-2xl font-bold">Welcome to PUTANA.DATE</CardTitle>
          <CardDescription>
            Choose your preferred authentication method
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Google Sign In */}
          <GoogleLoginButton />

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <Separator />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">Or</span>
            </div>
          </div>

          {/* Telegram Sign In */}
          <Button
            onClick={handleTelegramLogin}
            variant="outline"
            className="w-full"
            size="lg"
          >
            <MessageCircle className="w-5 h-5 mr-2" />
            Sign in with Telegram
          </Button>

          {/* Registration Link */}
          <div className="text-center pt-4">
            <p className="text-sm text-gray-600">
              New user?{' '}
              <button
                onClick={() => navigate('/registrationOfNewUser')}
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
              >
                Register here
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginPage;

