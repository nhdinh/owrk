import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
// @ts-ignore - Module Federation remote import
import { useAuth } from 'shared_components/AuthContext';
import { authAPI } from '@/lib/auth-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AppLayout } from '@/components/AppLayout';
import {
  ArrowLeft,
  Mail,
  Shield,
  Key,
  ShieldCheck,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { toast } from 'sonner';

const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export default function Profile() {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isSettingUpMFA, setIsSettingUpMFA] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [otpCode, setOtpCode] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  });

  const onChangePassword = async (data: ChangePasswordFormData) => {
    setIsChangingPassword(true);

    try {
      await authAPI.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      });
      toast.success('Password changed successfully');
      reset();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleSetupMFA = async () => {
    setIsSettingUpMFA(true);

    try {
      const response = await authAPI.setupMFA();
      setQrCodeUrl(response.qr_code_url);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to setup MFA');
      setIsSettingUpMFA(false);
    }
  };

  const handleEnableMFA = async () => {
    if (!otpCode || otpCode.length !== 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }

    try {
      await authAPI.enableMFA({ otp_code: otpCode });
      toast.success('MFA enabled successfully');
      setQrCodeUrl('');
      setShowOtpInput(false);
      setOtpCode('');
      setIsSettingUpMFA(false);
      refreshUser();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Invalid OTP code');
    }
  };

  const handleDisableMFA = async () => {
    if (!confirm('Are you sure you want to disable MFA?')) return;

    try {
      await authAPI.disableMFA();
      toast.success('MFA disabled successfully');
      refreshUser();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to disable MFA');
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (!user) {
    return null;
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
                  <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                  <h1 className="text-2xl font-bold">Profile Settings</h1>
                  <p className="text-sm text-muted-foreground">Manage your account and security</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <div className="grid gap-6 md:grid-cols-3">
            {/* Profile Card */}
            <Card className="md:col-span-1">
              <CardHeader className="text-center pb-4">
                <Avatar className="w-24 h-24 mx-auto mb-4">
                  <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                    {getInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
                <CardTitle className="text-xl">{user.full_name}</CardTitle>
                <CardDescription>{user.position || 'No position'}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-center gap-2">
                  <Badge variant={user.is_active ? 'default' : 'secondary'}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  {user.is_superuser && <Badge variant="destructive">Admin</Badge>}
                </div>

                <Separator />

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{user.email}</span>
                  </div>

                  {user.role && (
                    <div className="flex items-center gap-2 text-sm">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <span>{user.role.display_name}</span>
                    </div>
                  )}
                </div>

                <Separator />

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">MFA Enabled:</span>
                    <Badge variant={user.mfa_enabled ? 'default' : 'outline'}>
                      {user.mfa_enabled ? 'Yes' : 'No'}
                    </Badge>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Email Verified:</span>
                    <Badge variant={user.email_verified ? 'default' : 'outline'}>
                      {user.email_verified ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                </div>

                <Separator />

                <Button variant="destructive" className="w-full" onClick={logout}>
                  Logout
                </Button>
              </CardContent>
            </Card>

            {/* Settings Tabs */}
            <Card className="md:col-span-2">
              <Tabs defaultValue="security">
                <CardHeader>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="security">Security</TabsTrigger>
                    <TabsTrigger value="info">Information</TabsTrigger>
                  </TabsList>
                </CardHeader>

                <CardContent>
                  <TabsContent value="security" className="space-y-6">
                    {/* Change Password */}
                    <div>
                      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Key className="h-5 w-5" />
                        Change Password
                      </h3>
                      <form onSubmit={handleSubmit(onChangePassword)} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="current_password">Current Password</Label>
                          <Input
                            id="current_password"
                            type="password"
                            {...register('current_password')}
                          />
                          {errors.current_password && (
                            <p className="text-sm text-destructive">
                              {errors.current_password.message}
                            </p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="new_password">New Password</Label>
                          <Input id="new_password" type="password" {...register('new_password')} />
                          {errors.new_password && (
                            <p className="text-sm text-destructive">{errors.new_password.message}</p>
                          )}
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="confirm_password">Confirm New Password</Label>
                          <Input
                            id="confirm_password"
                            type="password"
                            {...register('confirm_password')}
                          />
                          {errors.confirm_password && (
                            <p className="text-sm text-destructive">
                              {errors.confirm_password.message}
                            </p>
                          )}
                        </div>

                        <Button type="submit" disabled={isChangingPassword}>
                          {isChangingPassword ? 'Changing...' : 'Change Password'}
                        </Button>
                      </form>
                    </div>

                    <Separator />

                    {/* MFA Management */}
                    <div>
                      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <ShieldCheck className="h-5 w-5" />
                        Two-Factor Authentication (MFA)
                      </h3>

                      {user.mfa_enabled ? (
                        <Alert className="mb-4">
                          <CheckCircle className="h-4 w-4" />
                          <AlertDescription>
                            MFA is currently enabled for your account. Your account is protected with
                            an additional layer of security.
                          </AlertDescription>
                        </Alert>
                      ) : (
                        <Alert variant="destructive" className="mb-4">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            MFA is not enabled. We strongly recommend enabling MFA to secure your
                            account.
                          </AlertDescription>
                        </Alert>
                      )}

                      {qrCodeUrl ? (
                        <div className="space-y-4">
                          {!showOtpInput ? (
                            <>
                              <Alert>
                                <AlertDescription>
                                  Scan this QR code with your authenticator app (Google Authenticator,
                                  Authy, etc.)
                                </AlertDescription>
                              </Alert>
                              <div className="flex justify-center p-4 border rounded-lg bg-white">
                                <img src={qrCodeUrl} alt="MFA QR Code" className="w-64 h-64" />
                              </div>
                              <Button onClick={() => setShowOtpInput(true)}>Done</Button>
                            </>
                          ) : (
                            <>
                              <Alert>
                                <AlertDescription>
                                  Enter the 6-digit code from your authenticator app to complete setup
                                </AlertDescription>
                              </Alert>
                              <div className="space-y-2">
                                <Label htmlFor="otp">Verification Code</Label>
                                <Input
                                  id="otp"
                                  type="text"
                                  placeholder="000000"
                                  maxLength={6}
                                  value={otpCode}
                                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                                />
                              </div>
                              <div className="flex gap-2">
                                <Button onClick={handleEnableMFA}>Verify & Enable</Button>
                                <Button
                                  variant="outline"
                                  onClick={() => {
                                    setShowOtpInput(false);
                                    setQrCodeUrl('');
                                    setOtpCode('');
                                    setIsSettingUpMFA(false);
                                  }}
                                >
                                  Cancel
                                </Button>
                              </div>
                            </>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {user.mfa_enabled ? (
                            <Button variant="destructive" onClick={handleDisableMFA}>
                              Disable MFA
                            </Button>
                          ) : (
                            <Button onClick={handleSetupMFA} disabled={isSettingUpMFA}>
                              {isSettingUpMFA ? 'Setting up...' : 'Enable MFA'}
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="info" className="space-y-4">
                    <div className="grid gap-4">
                      <div>
                        <Label className="text-muted-foreground">User ID</Label>
                        <p className="mt-1 font-medium">#{user.id}</p>
                      </div>

                      <div>
                        <Label className="text-muted-foreground">Email</Label>
                        <p className="mt-1">{user.email}</p>
                      </div>

                      <div>
                        <Label className="text-muted-foreground">Username</Label>
                        <p className="mt-1">{user.username || 'Not set'}</p>
                      </div>

                      <div>
                        <Label className="text-muted-foreground">Phone Number</Label>
                        <p className="mt-1">{user.phone_number || 'Not set'}</p>
                      </div>

                      <div>
                        <Label className="text-muted-foreground">Address</Label>
                        <p className="mt-1">{user.address || 'Not set'}</p>
                      </div>

                      <div>
                        <Label className="text-muted-foreground">Department</Label>
                        <p className="mt-1">
                          {user.department_id ? `Department #${user.department_id}` : 'Not assigned'}
                        </p>
                      </div>

                      <Separator />

                      <div>
                        <Label className="text-muted-foreground">Last Login</Label>
                        <p className="mt-1 text-sm">{user.last_login_at || 'Never'}</p>
                        {user.last_login_ip && (
                          <p className="text-sm text-muted-foreground">From IP: {user.last_login_ip}</p>
                        )}
                      </div>
                    </div>
                  </TabsContent>
                </CardContent>
              </Tabs>
            </Card>
          </div>
        </main>
      </div>
    </AppLayout>
  );
}
