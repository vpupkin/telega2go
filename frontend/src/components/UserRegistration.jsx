import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, User, Mail, Phone, Shield, ArrowRight, ArrowLeft } from 'lucide-react';

const UserRegistration = () => {
  const [step, setStep] = useState(1); // 1: Registration Form, 2: OTP Verification, 3: Success
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    telegram_chat_id: '',
    telegram_username: ''
  });
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [useUsername, setUseUsername] = useState(true); // Default to username for simplicity

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error on input change
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError('Name is required');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!formData.phone.trim()) {
      setError('Phone number is required');
      return false;
    }
    if (useUsername && !formData.telegram_username.trim()) {
      setError('Telegram Username is required');
      return false;
    }
    if (!useUsername && !formData.telegram_chat_id.trim()) {
      setError('Telegram Chat ID is required');
      return false;
    }
    return true;
  };

  const handleRegistration = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setError('');

    try {
      // Step 1: Register user and send OTP
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          // Only send the relevant field based on user choice
          ...(useUsername 
            ? { telegram_username: formData.telegram_username }
            : { telegram_chat_id: formData.telegram_chat_id }
          )
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      setSuccess('Registration initiated! Check your Telegram for OTP.');
      setStep(2); // Move to OTP verification step
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPVerification = async (e) => {
    e.preventDefault();
    if (!otpCode.trim()) {
      setError('Please enter the OTP code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          otp: otpCode
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'OTP verification failed');
      }

      const data = await response.json();
      setSuccess('Registration completed successfully!');
      setStep(3); // Move to success step
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/resend-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to resend OTP');
      }

      setSuccess('OTP resent successfully! Check your Telegram.');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderRegistrationForm = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <User className="w-6 h-6 text-blue-600" />
        </div>
        <CardTitle className="text-2xl font-bold">Create Account</CardTitle>
        <CardDescription>
          Register with your details and verify via Telegram OTP
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleRegistration} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              name="name"
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              name="phone"
              type="tel"
              placeholder="Enter your phone number"
              value={formData.phone}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-4">
              <Button
                type="button"
                variant={useUsername ? "default" : "outline"}
                size="sm"
                onClick={() => setUseUsername(true)}
              >
                @username
              </Button>
              <Button
                type="button"
                variant={!useUsername ? "default" : "outline"}
                size="sm"
                onClick={() => setUseUsername(false)}
              >
                Chat ID
              </Button>
            </div>
            
            {useUsername ? (
              <div className="space-y-2">
                <Label htmlFor="telegram_username">Telegram Username</Label>
                <Input
                  id="telegram_username"
                  name="telegram_username"
                  type="text"
                  placeholder="@yourusername"
                  value={formData.telegram_username}
                  onChange={handleInputChange}
                  required
                />
                <p className="text-xs text-green-600">
                  ✨ Super easy! Just enter your @username (e.g., @john_doe)
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="telegram_chat_id">Telegram Chat ID</Label>
                <Input
                  id="telegram_chat_id"
                  name="telegram_chat_id"
                  type="text"
                  placeholder="Your Telegram Chat ID"
                  value={formData.telegram_chat_id}
                  onChange={handleInputChange}
                  required
                />
                <p className="text-xs text-gray-500">
                  Get your Chat ID from @userinfobot on Telegram
                </p>
              </div>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Registering...' : 'Register & Send OTP'}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );

  const renderOTPVerification = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <Shield className="w-6 h-6 text-green-600" />
        </div>
        <CardTitle className="text-2xl font-bold">Verify OTP</CardTitle>
        <CardDescription>
          Enter the OTP code sent to your Telegram
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleOTPVerification} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="otp">OTP Code</Label>
            <Input
              id="otp"
              name="otp"
              type="text"
              placeholder="Enter 6-digit OTP"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              maxLength={6}
              required
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Verifying...' : 'Verify OTP'}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>

            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={handleResendOTP}
              disabled={isLoading}
            >
              Resend OTP
            </Button>

            <Button
              type="button"
              variant="ghost"
              className="w-full"
              onClick={() => setStep(1)}
              disabled={isLoading}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Registration
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );

  const renderSuccess = () => (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        <CardTitle className="text-2xl font-bold text-green-600">Success!</CardTitle>
        <CardDescription>
          Your account has been created successfully
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center space-y-4">
        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            Welcome, <strong>{formData.name}</strong>!
          </p>
          <p className="text-sm text-gray-600">
            Email: {formData.email}
          </p>
          <p className="text-sm text-gray-600">
            Phone: {formData.phone}
          </p>
        </div>

        <div className="flex flex-wrap gap-2 justify-center">
          <Badge variant="secondary">
            <Mail className="w-3 h-3 mr-1" />
            Email Verified
          </Badge>
          <Badge variant="secondary">
            <Phone className="w-3 h-3 mr-1" />
            Phone Verified
          </Badge>
          <Badge variant="secondary">
            <Shield className="w-3 h-3 mr-1" />
            Telegram Verified
          </Badge>
        </div>

        <Button
          onClick={() => {
            setStep(1);
            setFormData({ name: '', email: '', phone: '', telegram_chat_id: '', telegram_username: '' });
            setOtpCode('');
            setError('');
            setSuccess('');
          }}
          className="w-full"
        >
          Register Another User
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              1
            </div>
            <div className={`w-8 h-0.5 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              2
            </div>
            <div className={`w-8 h-0.5 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              3
            </div>
          </div>
        </div>

        {/* Step Content */}
        {step === 1 && renderRegistrationForm()}
        {step === 2 && renderOTPVerification()}
        {step === 3 && renderSuccess()}
      </div>
    </div>
  );
};

export default UserRegistration;
