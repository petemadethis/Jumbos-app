'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

export default function OnboardingPage() {
  const router = useRouter();
  const [zip, setZip] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleComplete = async () => {
    if (!zip) {
      router.push('/');
      return;
    }

    setLoading(true);
    const res = await apiFetch('/locations/me', {
      method: 'POST',
      body: JSON.stringify({
        zip_code: zip,
        is_primary: true
      }),
    });

    if (res) {
      router.push('/');
    } else {
      setError('Could not set your ZIP code. You can do this later in your profile.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <Card className="w-full max-w-xl p-12 text-center shadow-xl border-none">
        <div className="w-24 h-24 bg-secondary/10 text-secondary rounded-full flex items-center justify-center mx-auto mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        
        <h1 className="text-4xl font-bold text-primary mb-4 tracking-tight">Welcome to Jumbos!</h1>
        <p className="text-xl text-slate-600 mb-10 leading-relaxed">
          One last step: what's the primary ZIP code you operate in? This helps others find you in the directory.
        </p>

        {error && <p className="text-red-500 mb-4 text-sm font-medium">{error}</p>}

        <div className="max-w-xs mx-auto space-y-6">
          <Input 
            placeholder="e.g. 90210" 
            className="text-center text-2xl tracking-[0.5em] py-6 font-bold"
            maxLength={5}
            value={zip}
            onChange={(e) => setZip(e.target.value.replace(/\D/g, ''))}
          />
          
          <Button 
            variant="secondary" 
            fullWidth 
            size="lg" 
            onClick={handleComplete}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Finish Setup'}
          </Button>
          
          <button 
            onClick={() => router.push('/')}
            className="text-slate-400 hover:text-slate-600 font-medium transition-colors"
          >
            Skip for now
          </button>
        </div>
      </Card>
    </div>
  );
}
