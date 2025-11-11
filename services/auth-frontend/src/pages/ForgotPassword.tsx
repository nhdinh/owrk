import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { authAPI } from '@/lib/auth-api';
// @ts-expect-error - Module Federation remote import
import { Button } from 'shared_components/ui/button';
// @ts-expect-error - Module Federation remote import
import { Input } from 'shared_components/ui/input';
// @ts-expect-error - Module Federation remote import
import { Label } from 'shared_components/ui/label';
// @ts-expect-error - Module Federation remote import
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from 'shared_components/ui/card';
// @ts-expect-error - Module Federation remote import
import { Alert, AlertDescription } from 'shared_components/ui/alert';
import { Mail, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const forgotPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      await authAPI.forgotPassword({ email: data.email });
      setSuccess(true);
      toast.success('Password reset email sent!');
    } catch (err: any) {
      console.error('Forgot password error:', err);
      setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
              <Mail className="w-8 h-8 text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">Reset Password</CardTitle>
          <CardDescription className="text-center">
            Enter your email address and we'll send you a reset link
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success ? (
            <div className="space-y-4">
              <Alert className="border-green-500 bg-green-50 text-green-900">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription>
                  Password reset instructions have been sent to your email address. Please check your
                  inbox and follow the link to reset your password.
                </AlertDescription>
              </Alert>

              <div className="text-center text-sm text-muted-foreground">
                <p className="mb-2">Didn't receive the email?</p>
                <Button variant="link" size="sm" onClick={() => setSuccess(false)}>
                  Try again
                </Button>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => (window.location.href = '/login')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Login
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@example.com"
                    className="pl-10"
                    {...register('email')}
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Sending...' : 'Send Reset Link'}
              </Button>

              <div className="text-center">
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => (window.location.href = '/login')}
                  className="text-muted-foreground"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back to Login
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
