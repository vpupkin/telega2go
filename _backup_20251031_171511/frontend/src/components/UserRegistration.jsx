import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, User, Mail, Phone, Shield, ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react';

const UserRegistration = () => {
  const [searchParams] = useSearchParams();
  const urrIdParam = searchParams.get('urr_id'); // ✅ PENALTY4: URR_ID
  const telegramUserIdParam = searchParams.get('telegram_user_id'); // Backward compat
  
  const [step, setStep] = useState(1); // 1: Registration Form, 2: OTP Verification, 3: Success
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://putana.date:55552';
  const API_BASE = `${BACKEND_URL}/api`;
  
  const [formData, setFormData] = useState({
    urr_id: urrIdParam || '',
    password: '', // ✅ PENALTY4: Only editable field
    // All other fields from Telegram (read-only)
    telegram_user_id: '',
    username: '',
    email: '',
    phone: '',
    first_name: '',
    last_name: '',
    telegram_username: '',
    language_code: '',
    bank_id: '',
    driver_license: '',
    nationality: '',
    latitude: '',
    longitude: '',
    location: '',
    supported_languages: []
  });
  const [otpCode, setOtpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [useUsername, setUseUsername] = useState(true);
  const [telegramData, setTelegramData] = useState(null);
  const [nameAvailable, setNameAvailable] = useState(true);
  const [nameMessage, setNameMessage] = useState('');
  const [loadingTelegramData, setLoadingTelegramData] = useState(false);

  // ✅ PENALTY4: Load Telegram data by URR_ID or telegram_user_id
  useEffect(() => {
    if (urrIdParam) {
      loadTelegramDataByUrrId(urrIdParam);
    } else if (telegramUserIdParam) {
      loadTelegramData(telegramUserIdParam);
    }
  }, [urrIdParam, telegramUserIdParam]);

  // ✅ PENALTY4: Load data by URR_ID (primary method)
  const loadTelegramDataByUrrId = async (urrId) => {
    setLoadingTelegramData(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/registrationOfNewUser?urr_id=${urrId}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load registration data');
      }
      
      const data = await response.json();
      setTelegramData(data);
      
      // ✅ PENALTY4: Pre-fill ALL fields from Telegram data (read-only)
      setFormData(prev => ({
        ...prev,
        urr_id: data.urr_id || urrId,
        telegram_user_id: data.telegram_user_id?.toString() || '',
        username: data.default_username || data.suggested_name || data.telegram_user_id?.toString() || '',
        email: data.email || '',
        phone: data.phone || '',
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        telegram_username: data.telegram_username || '',
        language_code: data.language_code || '',
        latitude: data.latitude?.toString() || '',
        longitude: data.longitude?.toString() || '',
        location: data.location || '',
        bank_id: data.telegram_data?.bank_id || '',
        driver_license: data.telegram_data?.driver_license || '',
        nationality: data.telegram_data?.nationality || '',
        supported_languages: data.language_code ? [data.language_code] : []
      }));
      
      setNameAvailable(data.name_available);
      setNameMessage(data.name_message || '');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingTelegramData(false);
    }
  };

  // Backward compatibility: Load by telegram_user_id
  const loadTelegramData = async (telegramUserId) => {
    setLoadingTelegramData(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/registrationOfNewUser?telegram_user_id=${telegramUserId}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load Telegram data');
      }
      
      const data = await response.json();
      setTelegramData(data);
      
      setFormData(prev => ({
        ...prev,
        telegram_username: data.telegram_username || '',
        telegram_user_id: data.telegram_user_id?.toString() || '',
        username: data.default_username || data.suggested_name || ''
      }));
      
      setNameAvailable(data.name_available);
      setNameMessage(data.name_message || '');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingTelegramData(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // ✅ PENALTY4: Only allow password editing if URR_ID present
    if (urrIdParam && name !== 'password') {
      // Ignore changes to read-only fields
      return;
    }
    
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

    // ✅ PENALTY4: Only validate password if URR_ID present (Telegram registration)
    if (urrIdParam) {
      if (!formData.password || formData.password.trim().length < 6) {
        setError('Password is required (minimum 6 characters)');
        return;
      }
    } else {
      // Regular registration validation
      if (!validateForm()) return;
    }

    setIsLoading(true);
    setError('');

    try {
      // ✅ PENALTY4: Telegram registration - only send URR_ID and password
      if (urrIdParam) {
        const response = await fetch(`${API_BASE}/register-telegram`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            urr_id: formData.urr_id,
            password: formData.password
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Registration failed');
        }

        const data = await response.json();
        setSuccess('🎉 Registration completed successfully! Welcome to PUTANA.DATE!');
        setStep(3); // Skip OTP, go directly to success
      } else if (telegramUserIdParam) {
        // Backward compatibility path
        const response = await fetch(`${API_BASE}/register-telegram`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: formData.username,
            email: formData.email,
            phone: formData.phone,
            telegram_user_id: parseInt(formData.telegram_user_id)
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Registration failed');
        }

        const data = await response.json();
        setSuccess('Registration completed successfully!');
        setStep(3);
      } else {
        // Regular registration flow with OTP
        const response = await fetch(`${API_BASE}/register`, {
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
      }
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
      const response = await fetch(`${API_BASE}/verify-otp`, {
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
      
      // Check if we got a magic link
      if (data.magic_link) {
        setSuccess('OTP verified! Please check your email for the magic link to complete registration.');
        // Redirect to magic link verification page
        window.location.href = data.magic_link;
      } else {
        setSuccess('Registration completed successfully!');
        setStep(3); // Move to success step
      }
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
      const response = await fetch(`${API_BASE}/resend-otp`, {
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
        <CardTitle className="text-2xl font-bold">
          {urrIdParam ? '🎉 Welcome to PUTANA.DATE!' : telegramUserIdParam ? 'Complete Your Registration' : 'Create Account'}
        </CardTitle>
        <CardDescription>
          {urrIdParam 
            ? 'Review your profile data and set your password to complete registration'
            : telegramUserIdParam 
            ? 'Welcome! Please complete your registration with your details'
            : 'Register with your details and verify via Telegram OTP'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loadingTelegramData && (
          <Alert className="mb-4">
            <AlertDescription>Loading your Telegram data...</AlertDescription>
          </Alert>
        )}
        
        <form onSubmit={handleRegistration} className="space-y-4">
          {/* ✅ PENALTY4: Show ALL Telegram data as READ-ONLY (if URR_ID present) */}
          {urrIdParam && telegramData && (
            <>
              <div className="space-y-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200">
                <h3 className="text-lg font-bold text-blue-900 mb-4 text-center">📱 Your Telegram Profile Data (Read-Only)</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Username (Telegram User ID)</Label>
                    <Input
                      value={formData.username || formData.telegram_user_id || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed font-mono"
                    />
                    {!nameAvailable && nameMessage && (
                      <p className="text-xs text-red-600 mt-1">{nameMessage}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Email Address</Label>
                    <Input
                      value={formData.email || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Phone Number</Label>
                    <Input
                      value={formData.phone || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Telegram Username</Label>
                    <Input
                      value={formData.telegram_username || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">First Name</Label>
                    <Input
                      value={formData.first_name || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Last Name</Label>
                    <Input
                      value={formData.last_name || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Language Code</Label>
                    <Input
                      value={formData.language_code?.toUpperCase() || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Supported Languages</Label>
                    <Input
                      value={formData.supported_languages?.join(', ').toUpperCase() || formData.language_code?.toUpperCase() || 'N/A'}
                      readOnly
                      className="bg-gray-100 cursor-not-allowed"
                    />
                  </div>
                  
                  {formData.bank_id && (
                    <div>
                      <Label className="text-xs font-semibold text-gray-700">Bank ID</Label>
                      <Input
                        value={formData.bank_id}
                        readOnly
                        className="bg-gray-100 cursor-not-allowed"
                      />
                    </div>
                  )}
                  
                  {formData.driver_license && (
                    <div>
                      <Label className="text-xs font-semibold text-gray-700">Driver License</Label>
                      <Input
                        value={formData.driver_license}
                        readOnly
                        className="bg-gray-100 cursor-not-allowed"
                      />
                    </div>
                  )}
                  
                  {formData.nationality && (
                    <div>
                      <Label className="text-xs font-semibold text-gray-700">Nationality</Label>
                      <Input
                        value={formData.nationality}
                        readOnly
                        className="bg-gray-100 cursor-not-allowed"
                      />
                    </div>
                  )}
                  
                  {(formData.latitude || formData.longitude) && (
                    <>
                      <div>
                        <Label className="text-xs font-semibold text-gray-700">GPS Latitude</Label>
                        <Input
                          value={formData.latitude || 'N/A'}
                          readOnly
                          className="bg-gray-100 cursor-not-allowed font-mono"
                        />
                      </div>
                      <div>
                        <Label className="text-xs font-semibold text-gray-700">GPS Longitude</Label>
                        <Input
                          value={formData.longitude || 'N/A'}
                          readOnly
                          className="bg-gray-100 cursor-not-allowed font-mono"
                        />
                      </div>
                    </>
                  )}
                  
                  {formData.location && (
                    <div className="md:col-span-2">
                      <Label className="text-xs font-semibold text-gray-700">Location</Label>
                      <Input
                        value={formData.location}
                        readOnly
                        className="bg-gray-100 cursor-not-allowed"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* ✅ PENALTY4: Only Password is editable */}
              <div className="space-y-2 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-300">
                <Label htmlFor="password" className="text-base font-bold text-yellow-900">
                  🔐 Set Your Password (Required)
                </Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password (min 6 characters)"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="bg-white"
                  minLength={6}
                />
                <p className="text-xs text-gray-600 mt-1">
                  ⚠️ This is the only field you can change. All other data comes from your Telegram profile.
                </p>
              </div>
            </>
          )}

          {/* Regular registration form (when no URR_ID) */}
          {!urrIdParam && (
            <>
              {/* Backward compatibility: Old form for telegram_user_id */}
              {telegramUserIdParam && telegramData && (
                <div className="space-y-3 p-4 bg-gray-50 rounded-lg border">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">📱 Your Telegram Data (Read-Only)</h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <Label className="text-xs text-gray-500">Telegram User ID</Label>
                      <Input value={formData.telegram_user_id || ''} readOnly className="bg-gray-100 cursor-not-allowed" />
                    </div>
                    <div>
                      <Label className="text-xs text-gray-500">Username</Label>
                      <Input value={formData.telegram_username || 'N/A'} readOnly className="bg-gray-100 cursor-not-allowed" />
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="username">Username/Login ID</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Choose your unique username"
                  value={formData.username}
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
            </>
          )}

          {/* Only show Telegram fields for non-Telegram registrations */}
          {!telegramUserIdParam && (
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
          )}

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
            {isLoading 
              ? (urrIdParam ? 'Registering...' : telegramUserIdParam ? 'Registering...' : 'Sending OTP...') 
              : (urrIdParam 
                  ? '✅ Complete Registration & Welcome to PUTANA.DATE!' 
                  : telegramUserIdParam 
                  ? '✅ Complete Registration (No OTP Needed)' 
                  : 'Register & Send OTP')
            }
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
        <CardTitle className="text-2xl font-bold text-green-600">
          🎉 Congratulations!
        </CardTitle>
        <CardDescription className="text-lg font-semibold">
          Welcome to PUTANA.DATE! 🚀
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center space-y-4">
        <div className="space-y-2">
          <p className="text-lg font-semibold text-gray-800">
            Your account has been created successfully!
          </p>
          {formData.username && (
            <p className="text-sm text-gray-600">
              Username: <strong>{formData.username}</strong>
            </p>
          )}
          {formData.email && (
            <p className="text-sm text-gray-600">
              Email: {formData.email}
            </p>
          )}
          {formData.phone && (
            <p className="text-sm text-gray-600">
              Phone: {formData.phone}
            </p>
          )}
          {urrIdParam && (
            <p className="text-xs text-gray-500 mt-4">
              ✅ All your Telegram data has been saved. You can now use all features!
            </p>
          )}
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
