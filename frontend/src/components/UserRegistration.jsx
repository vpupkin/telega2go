import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, User, Mail, Phone, Shield, ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react';

const UserRegistration = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const urrIdParam = searchParams.get('urr_id'); // ✅ PENALTY4: URR_ID
  const telegramUserIdParam = searchParams.get('telegram_user_id'); // Backward compat
  const tokenParam = searchParams.get('token'); // ✅ WelcomeBack: JWT token from magic link
  
  // ✅ NEW: Detect if this is the direct Telegram registration route
  const isDirectTelegramRegistration = location.pathname === '/telegram-register';
  
  const [step, setStep] = useState(1); // 1: Registration Form, 2: OTP Verification, 3: Success
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://putana.date:55552';
  // ✅ Fix: Normalize URL to avoid duplicate /api/
  const normalizedBackendUrl = BACKEND_URL.replace(/\/+$/, ''); // Remove trailing slashes
  const API_BASE = normalizedBackendUrl.endsWith('/api') 
    ? normalizedBackendUrl 
    : `${normalizedBackendUrl}/api`;
  
  const [formData, setFormData] = useState({
    urr_id: urrIdParam || '',
    password: '', // ✅ PENALTY4: Only editable field
    // All other fields from Telegram (read-only)
    telegram_user_id: '',
    username: '',
    name: '', // ✅ NEW: For direct Telegram registration
    email: '',
    phone: '',
    first_name: '',
    last_name: '',
    telegram_username: '',
    telegram_chat_id: '', // ✅ NEW: For direct Telegram registration
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
  const [useUsername, setUseUsername] = useState(false); // ✅ PENALTY FIX: Restore toggle
  const [telegramData, setTelegramData] = useState(null);
  const [nameAvailable, setNameAvailable] = useState(true);
  const [nameMessage, setNameMessage] = useState('');
  const [loadingTelegramData, setLoadingTelegramData] = useState(false);
  const [skipTelegramDataLoad, setSkipTelegramDataLoad] = useState(false); // ✅ FIX: Prevent reloading Telegram data when registering another user

  // ✅ WelcomeBack: Check for JWT token first (registered user clicking magic link)
  useEffect(() => {
    if (tokenParam) {
      console.log('🔐 JWT token detected - registered user authentication');
      // Store token in localStorage
      localStorage.setItem('access_token', tokenParam);
      // Redirect to admin dashboard (user is already registered)
      console.log('✅ Redirecting registered user to dashboard');
      navigate('/admin', { replace: true });
      return; // Don't load registration form
    }
  }, [tokenParam, navigate]);

  // ✅ FIX: Reset skipTelegramDataLoad flag when URL params change (new registration request)
  useEffect(() => {
    // If we get new URL params (urrIdParam or telegramUserIdParam), reset the skip flag
    if (urrIdParam || telegramUserIdParam) {
      setSkipTelegramDataLoad(false);
    }
  }, [urrIdParam, telegramUserIdParam]);

  // ✅ PENALTY4: Load Telegram data by URR_ID or telegram_user_id
  useEffect(() => {
    // Skip if token is present (user is being redirected)
    if (tokenParam) return;
    
    // ✅ FIX: Skip loading if user explicitly wants to register another user
    if (skipTelegramDataLoad) {
      console.log('⚠️ Skipping Telegram data load - user wants to register another user');
      return;
    }
    
    // ✅ NEW: Skip loading Telegram data for direct Telegram registration (user will enter manually)
    if (isDirectTelegramRegistration) {
      console.log('📱 Direct Telegram registration - user will enter data manually');
      return;
    }
    
    console.log('🔍 Registration form loaded:', {
      urrIdParam,
      telegramUserIdParam,
      formData_urr_id: formData.urr_id
    });
    
    if (urrIdParam) {
      console.log('📥 Loading Telegram data by URR_ID:', urrIdParam);
      loadTelegramDataByUrrId(urrIdParam);
    } else if (telegramUserIdParam) {
      console.log('📥 Loading Telegram data by telegram_user_id:', telegramUserIdParam);
      loadTelegramData(telegramUserIdParam);
    } else {
      console.warn('⚠️ No URR_ID or telegram_user_id in URL parameters');
    }
  }, [urrIdParam, telegramUserIdParam, tokenParam, isDirectTelegramRegistration, skipTelegramDataLoad]);

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
      
      // ✅ CRITICAL: Check if user is already registered - MUST BE FIRST!
      console.log('🔍 Checking registration data:', { already_registered: data.already_registered, has_urr_id: !!data.urr_id });
      
      if (data.already_registered === true) {
        console.log('✅ User already registered - redirecting to dashboard');
        // Generate magic link for already-registered user
        try {
          const magicLinkResponse = await fetch(`${API_BASE}/generate-magic-link`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: data.email || `user${data.user_id}@telegram.local`,
              user_id: data.user_id
            })
          });
          
          if (magicLinkResponse.ok) {
            const magicLinkData = await magicLinkResponse.json();
            // Redirect to magic link verification
            window.location.href = magicLinkData.magic_link_url;
            return; // Exit early - redirecting
          }
        } catch (magicLinkError) {
          console.error('Error generating magic link:', magicLinkError);
          // Fallback: just redirect to dashboard
          navigate('/admin', { replace: true });
          return;
        }
        return; // Exit early if redirecting
      }
      setTelegramData(data);
      
      // ✅ PENALTY4: Pre-fill ALL fields from Telegram data
      const loadedUrrId = data.urr_id || urrId;
      console.log('✅ Telegram data loaded:', {
        urr_id: loadedUrrId,
        username: data.telegram_username || data.default_username,
        has_email: !!data.email,
        has_phone: !!data.phone
      });
      
      setFormData(prev => ({
        ...prev,
        urr_id: loadedUrrId, // ✅ CRITICAL: Ensure URR_ID is set from loaded data
        telegram_user_id: data.telegram_user_id?.toString() || '',
        username: data.telegram_username || data.default_username || data.suggested_name || data.telegram_user_id?.toString() || '', // ✅ Use Telegram username first
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

  // ✅ Generate password: double consonant + vowel + 3 random numbers
  // Pattern examples: Cafebabe123, Sukiroma234, Zedagowi710, Kitanijo600, Nigodala711
  // Pattern: CCVCVCVC + 3 numbers (double consonant + vowel, repeated 4 times)
  const generatePassword = () => {
    const consonants = 'bcdfghjklmnpqrstvwxyz';
    const vowels = 'aeiou';
    const getRandom = (str) => str[Math.floor(Math.random() * str.length)];
    
    // Generate 4 groups: CC-VC-CV-CV (e.g., Ca-fe-ba-be = Cafebabe)
    const group1 = getRandom(consonants) + getRandom(consonants) + getRandom(vowels); // e.g., "ca"
    const group2 = getRandom(consonants) + getRandom(vowels); // e.g., "fe"
    const group3 = getRandom(consonants) + getRandom(vowels); // e.g., "ba"
    const group4 = getRandom(consonants) + getRandom(vowels); // e.g., "be"
    const numbers = String(Math.floor(Math.random() * 900) + 100); // 3 random digits
    
    // Combine: Capitalize first letter + rest + numbers
    const word = group1 + group2 + group3 + group4;
    const generated = word.charAt(0).toUpperCase() + word.slice(1) + numbers;
    
    setFormData(prev => ({
      ...prev,
      password: generated
    }));
    setError(''); // Clear error
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // ✅ PENALTY4: Always allow editing password and username, allow editing empty fields (email, phone)
    if (urrIdParam && name !== 'password' && name !== 'username' && name !== 'email' && name !== 'phone') {
      // Only allow editing if field is empty (for validation purposes)
      const currentValue = formData[name];
      if (currentValue && currentValue !== 'N/A' && currentValue.trim() !== '') {
        // Field has value - don't allow editing (read-only from Telegram)
        return;
      }
    }
    
    // ✅ Allow editing email and phone if empty (even for Telegram users)
    if (urrIdParam && (name === 'email' || name === 'phone')) {
      // Always allow editing email and phone (they may be empty)
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
    // ✅ PENALTY FIX: Validate EITHER username OR chat_id (one required)
    if (useUsername) {
      if (!formData.telegram_username || !formData.telegram_username.trim()) {
        setError('Telegram Username is required');
        return false;
      }
    } else {
      if (!formData.telegram_chat_id || !formData.telegram_chat_id.trim()) {
        setError('Telegram Chat ID is required');
        return false;
      }
    }
    return true;
  };

  const handleRegistration = async (e) => {
    e.preventDefault();

    // ✅ NEW: Direct Telegram Registration - validate with toggle
    if (isDirectTelegramRegistration && !urrIdParam) {
      if (!validateForm()) return;
      // validateForm already checks for telegram_username or telegram_chat_id based on useUsername
    }
    // ✅ PENALTY4: Only validate password and username if URR_ID present (Telegram registration)
    else if (urrIdParam) {
      // ✅ CRITICAL VALIDATION: Ensure URR_ID is present
      if (!urrIdParam || !urrIdParam.trim()) {
        setError('Registration request ID (URR_ID) is missing. Please start registration again via Telegram bot.');
        return;
      }
      
      // ✅ CRITICAL VALIDATION: Ensure formData.urr_id is set
      const urrIdToSend = urrIdParam || formData.urr_id;
      if (!urrIdToSend || !urrIdToSend.trim()) {
        setError('Registration request ID is missing. Please refresh the page and try again.');
        return;
      }
      
      if (!formData.password || formData.password.trim().length < 6) {
        setError('Password is required (minimum 6 characters)');
        return;
      }
      if (!formData.username || formData.username.trim().length < 1) {
        setError('Username on Site is required');
        return;
      }
      
      // ✅ Log request payload for debugging
      console.log('📤 Sending registration request:', {
        urr_id: urrIdToSend,
        password_length: formData.password?.length || 0,
        username: formData.username || 'N/A'
      });
    } else {
      // Regular registration validation
      if (!validateForm()) return;
    }

    setIsLoading(true);
    setError('');

    try {
      // ✅ PENALTY4: Telegram registration - send URR_ID, password, and username (if changed)
      if (urrIdParam) {
        // ✅ CRITICAL: Priority order: URL param > loaded data > formData
        const urrIdToSend = urrIdParam || formData.urr_id || '';
        
        console.log('🔍 URR_ID resolution:', {
          urrIdParam,
          formData_urr_id: formData.urr_id,
          urrIdToSend,
          isValid: !!urrIdToSend && urrIdToSend.trim().length > 0
        });
        
        // ✅ CRITICAL: Ensure urr_id is never empty or undefined
        if (!urrIdToSend || !urrIdToSend.trim()) {
          const errorMsg = 'Registration request ID is missing. Please start registration again via Telegram bot (@taxoin_bot).';
          console.error('❌', errorMsg, { urrIdParam, formData_urr_id: formData.urr_id });
          throw new Error(errorMsg);
        }
        
        const requestPayload = {
          urr_id: urrIdToSend.trim(),
          password: formData.password?.trim() || '',
        };
        
        // Only include username if it's not empty
        if (formData.username && formData.username.trim()) {
          requestPayload.username = formData.username.trim();
        }
        
        console.log('📤 Final payload being sent:', { 
          urr_id: requestPayload.urr_id, 
          password_length: requestPayload.password.length,
          has_username: !!requestPayload.username,
          username: requestPayload.username || 'N/A'
        });
        
        const response = await fetch(`${API_BASE}/register-telegram`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestPayload),
        });

        if (!response.ok) {
          // ✅ Try to parse error response
          let errorData;
          try {
            errorData = await response.json();
          } catch (parseErr) {
            errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
          }
          
          console.error('❌ Registration error:', {
            status: response.status,
            statusText: response.statusText,
            error: errorData,
            payload_sent: { ...requestPayload, password: '***' }
          });
          
          // ✅ Better error messages for common issues
          let errorMessage = errorData.detail || `Registration failed (${response.status})`;
          
          if (errorMessage.includes('not found') || errorMessage.includes('expired')) {
            errorMessage = 'Registration request expired or not found. Please start registration again via Telegram bot (@taxoin_bot).';
          } else if (errorMessage.includes('Password')) {
            errorMessage = errorMessage; // Keep original password error
          } else if (errorMessage.includes('already taken') || errorMessage.includes('Username')) {
            // ✅ Username conflict - suggest changing username
            errorMessage = `${errorMessage}\n\n💡 Please enter a different username in the "Username on Site" field above.`;
          } else if (response.status === 400) {
            // Generic 400 - add more context
            errorMessage = `${errorMessage} (Please check your registration data and try again)`;
          }
          
          throw new Error(errorMessage);
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
      } else if (isDirectTelegramRegistration) {
        // ✅ NEW: Direct Telegram Registration flow with OTP
        // ✅ FIX: Username requires chat_id for OTP delivery
        const payload = {
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
        };
        
        // ✅ PENALTY FIX: Send ONLY the selected identifier (backend will resolve the other)
        // ✅ CRITICAL: Only include non-empty values to avoid validation issues
        // ✅ CRITICAL FIX: Handle both toggle states explicitly
        if (useUsername) {
          // User selected username mode
          const usernameValue = formData.telegram_username?.trim() || '';
          if (!usernameValue) {
            throw new Error('Telegram Username is required when using username mode');
          }
          payload.telegram_username = usernameValue;
          // ✅ NEVER send chat_id when using username
          // Backend will resolve chat_id from username
        } else {
          // User selected chat_id mode
          const chatIdValue = formData.telegram_chat_id?.trim() || '';
          if (!chatIdValue) {
            throw new Error('Telegram Chat ID is required when using Chat ID mode');
          }
          payload.telegram_chat_id = chatIdValue;
          // ✅ NEVER send username when using chat_id
          // Backend will resolve username from chat_id
        }
        
        // ✅ DEBUG: Log payload before sending (for geshatele debugging)
        console.log('📤 Sending registration payload:', {
          name: payload.name,
          email: payload.email,
          phone: payload.phone,
          has_telegram_chat_id: !!payload.telegram_chat_id,
          has_telegram_username: !!payload.telegram_username,
          useUsername: useUsername
        });
        
        const response = await fetch(`${API_BASE}/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        // ✅ DEBUG: Log response details
        console.log('📥 Registration response:', {
          status: response.status,
          ok: response.ok,
          url: response.url
        });

        if (!response.ok) {
          let errorData;
          try {
            errorData = await response.json();
          } catch (e) {
            errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
          }
          const errorMessage = errorData.detail || 'Registration failed';
          
          // ✅ DEBUG: Log the payload that failed (for geshatele debugging)
          console.error('❌ Registration failed:', {
            status: response.status,
            error: errorMessage,
            payload: payload,
            errorData: errorData
          });
          
          // ✅ Better error messages for common cases
          if (errorMessage.includes('already registered') || errorMessage.includes('already exists')) {
            throw new Error(`${errorMessage} Please log in or use a different account.`);
          }
          if (errorMessage.includes('already taken')) {
            throw new Error(errorMessage);
          }
          throw new Error(errorMessage);
        }

        const data = await response.json();
        setSuccess('Registration initiated! Check your Telegram for OTP.');
        setStep(2); // Move to OTP verification step
      } else {
        // Regular registration flow with OTP (no Telegram)
        const response = await fetch(`${API_BASE}/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            phone: formData.phone
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
          {urrIdParam 
            ? '🎉 Welcome to PUTANA.DATE!' 
            : telegramUserIdParam 
            ? 'Complete Your Registration' 
            : isDirectTelegramRegistration
            ? '📱 Telegram Registration'
            : 'Create Account'}
        </CardTitle>
        <CardDescription>
          {urrIdParam 
            ? 'Review your profile data and set your password to complete registration'
            : telegramUserIdParam 
            ? 'Welcome! Please complete your registration with your details'
            : isDirectTelegramRegistration
            ? 'Register with Telegram and verify via OTP'
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
                    <Label className="text-xs font-semibold text-gray-700">Email Address {!formData.email && '(Editable)'}</Label>
                    <Input
                      name="email"
                      value={formData.email || ''}
                      onChange={handleInputChange}
                      placeholder={formData.email ? '' : 'Enter email (if not provided by Telegram)'}
                      readOnly={!!formData.email && formData.email !== ''}
                      className={formData.email ? "bg-gray-100 cursor-not-allowed" : "bg-white"}
                    />
                  </div>
                  
                  <div>
                    <Label className="text-xs font-semibold text-gray-700">Phone Number {!formData.phone && '(Editable)'}</Label>
                    <Input
                      name="phone"
                      value={formData.phone || ''}
                      onChange={handleInputChange}
                      placeholder={formData.phone ? '' : 'Enter phone (if not provided by Telegram)'}
                      readOnly={!!formData.phone && formData.phone !== ''}
                      className={formData.phone ? "bg-gray-100 cursor-not-allowed" : "bg-white"}
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

            </>
          )}

          {/* ✅ PENALTY4: Username on Site (unique user ID) - editable for validation */}
          {urrIdParam && (
            <div className="space-y-2 p-4 bg-green-50 rounded-lg border-2 border-green-300">
              <Label htmlFor="username" className="text-base font-bold text-green-900">
                👤 Username on Site (Unique User ID)
              </Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="Your unique username (will be validated)"
                value={formData.username}
                onChange={handleInputChange}
                required
                className={`bg-white ${!nameAvailable && nameMessage ? 'border-red-500 bg-red-50' : ''}`}
                disabled={loadingTelegramData}
              />
              {!nameAvailable && nameMessage && (
                <p className="text-xs text-red-600 mt-1">{nameMessage}</p>
              )}
              <p className="text-xs text-gray-600 mt-1">
                This will be your unique identifier on the site. Must be unique across all users.
              </p>
            </div>
          )}

          {/* ✅ PENALTY4: Password field - ALWAYS visible when URR_ID present (even if telegramData still loading) */}
          {urrIdParam && (
            <div className="space-y-2 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-300">
              <div className="flex items-center justify-between mb-2">
                <Label htmlFor="password" className="text-base font-bold text-yellow-900">
                  🔐 Set Your Password (Required)
                </Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={generatePassword}
                  className="text-xs"
                >
                  🎲 Generate Password
                </Button>
              </div>
              <Input
                id="password"
                name="password"
                type="text"
                placeholder="Enter your password (min 6 characters) or use generator"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="bg-white font-mono"
                minLength={6}
                disabled={loadingTelegramData}
              />
              <p className="text-xs text-gray-600 mt-1">
                ⚠️ This is the only field you can change. All other data comes from your Telegram profile.
              </p>
            </div>
          )}

          {/* ✅ NEW: Direct Telegram Registration Form (with toggle) */}
          {isDirectTelegramRegistration && !urrIdParam && !telegramUserIdParam && (
            <>
              <div className="space-y-4 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200">
                <h3 className="text-lg font-bold text-purple-900 mb-4 text-center">📱 Telegram Registration</h3>
                {/* ✅ PENALTY FIX: Toggle between Username OR Chat ID (NEVER both) */}
                <div className="flex gap-2 mb-4">
                  <Button
                    type="button"
                    variant={useUsername ? "default" : "outline"}
                    onClick={() => setUseUsername(true)}
                    className="flex-1"
                  >
                    @username
                  </Button>
                  <Button
                    type="button"
                    variant={!useUsername ? "default" : "outline"}
                    onClick={() => setUseUsername(false)}
                    className="flex-1"
                  >
                    Chat ID
                  </Button>
                </div>

                {/* ✅ Show ONLY ONE field based on toggle */}
                {useUsername ? (
                  <div className="space-y-2">
                    <Label htmlFor="telegram_username">Telegram Username *</Label>
                    <Input
                      id="telegram_username"
                      name="telegram_username"
                      placeholder="@username"
                      value={formData.telegram_username || ''}
                      onChange={handleInputChange}
                      required
                    />
                    <p className="text-xs text-gray-600">
                      Enter your Telegram username (e.g., @username). Chat ID will be resolved automatically.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Label htmlFor="telegram_chat_id">Telegram Chat ID *</Label>
                    <Input
                      id="telegram_chat_id"
                      name="telegram_chat_id"
                      placeholder="123456789"
                      value={formData.telegram_chat_id}
                      onChange={handleInputChange}
                      required
                    />
                    <p className="text-xs text-gray-600">
                      Get your Chat ID from @userinfobot on Telegram. Username will be resolved automatically.
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Full Name *</Label>
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
                <Label htmlFor="username">Username on Site (Unique User ID) *</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Choose your unique username (will be validated for uniqueness)"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
                <p className="text-xs text-gray-600">
                  This will be your unique identifier. Must be unique across all users.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
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
                <Label htmlFor="phone">Phone Number *</Label>
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

          {/* Regular registration form (when no URR_ID and not direct Telegram registration) */}
          {!urrIdParam && !isDirectTelegramRegistration && (
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
                <Label htmlFor="username">Username on Site (Unique User ID)</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="Choose your unique username (will be validated for uniqueness)"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
                <p className="text-xs text-gray-600">
                  This will be your unique identifier. Must be unique across all users.
                </p>
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
              ? (urrIdParam ? 'Registering...' : telegramUserIdParam ? 'Registering...' : isDirectTelegramRegistration ? 'Sending OTP...' : 'Sending OTP...') 
              : (urrIdParam 
                  ? '✅ Complete Registration & Welcome to PUTANA.DATE!' 
                  : telegramUserIdParam 
                  ? '✅ Complete Registration (No OTP Needed)' 
                  : isDirectTelegramRegistration
                  ? '📱 Register with Telegram & Send OTP'
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
              onClick={() => {
                setStep(1);
                // ✅ FIX: Don't reset form data when going back (user might want to edit)
                // Only clear OTP code and errors
                setOtpCode('');
                setError('');
                setSuccess('');
              }}
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
            // ✅ FIX: Clear URL parameters to prevent reloading expired Telegram data
            navigate('/telegram-register', { replace: true });
            
            // ✅ FIX: Reset all state including Telegram data flags
            setStep(1);
            setFormData({ 
              name: '', 
              email: '', 
              phone: '', 
              telegram_chat_id: '', 
              telegram_username: '',
              urr_id: '',
              telegram_user_id: '',
              username: '',
              password: ''
            });
            setOtpCode('');
            setError('');
            setSuccess('');
            setTelegramData(null);
            setNameAvailable(true);
            setNameMessage('');
            setLoadingTelegramData(false);
            setSkipTelegramDataLoad(true); // ✅ Prevent reloading Telegram data from old URL params
            setUseUsername(false); // Reset toggle
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
