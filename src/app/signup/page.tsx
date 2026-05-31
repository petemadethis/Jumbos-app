'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Logo from '@/components/ui/Logo';

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'agent',
    phone: '',
    company_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authApi.register(formData);
      if (data) {
        router.push('/onboarding');
      } else {
        setError('Registration failed. Please check your details.');
      }
    } catch (err) {
      setError('An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white p-10 rounded-lg shadow-xl border-none">
        <div className="flex flex-col items-center mb-10">
          <Logo className="scale-125 mb-2" />
          <h1 className="text-xl font-medium text-slate-500 mt-4">Join the location-first network</h1>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6 text-sm">
            {error}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          <Input 
            label="Full Name" 
            name="full_name"
            required
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Jane Doe" 
          />
          
          <Input 
            label="Email Address" 
            name="email"
            type="email"
            required
            value={formData.email}
            onChange={handleChange}
            placeholder="jane@example.com" 
          />

          <Input 
            label="Password" 
            name="password"
            type="password"
            required
            value={formData.password}
            onChange={handleChange}
            placeholder="••••••••" 
          />
          
          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">
              Professional Role
            </label>
            <select 
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
            >
              <option value="agent">Real Estate Agent</option>
              <option value="broker">Broker</option>
              <option value="investor">Investor</option>
              <option value="wholesaler">Wholesaler</option>
              <option value="contractor">Contractor</option>
              <option value="mortgage_broker">Mortgage Broker</option>
              <option value="hard_money_lender">Hard Money Lender</option>
              <option value="property_manager">Property Manager</option>
              <option value="title_company">Title Company</option>
              <option value="inspector">Inspector</option>
              <option value="insurance">Insurance</option>
              <option value="attorney">Attorney</option>
              <option value="other">Other</option>
            </select>
          </div>

          <Input 
            label="Company Name (Optional)" 
            name="company_name"
            value={formData.company_name}
            onChange={handleChange}
            placeholder="Doe Realty" 
          />
          
          <Button 
            type="submit" 
            fullWidth 
            size="lg" 
            disabled={loading}
            variant="secondary"
            className="mt-6"
          >
            {loading ? 'Creating Account...' : 'Sign up'}
          </Button>
        </form>
        
        <div className="mt-8 text-center">
          <p className="text-slate-600">
            Already have an account? <Link href="/login" className="text-secondary font-bold hover:underline">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
