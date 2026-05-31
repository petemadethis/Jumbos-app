'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { userApi } from '@/lib/api';
import Card, { CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function PublicProfilePage() {
  const { id } = useParams();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (typeof id !== 'string') return;
      const data = await userApi.getProfile(id);
      if (data) setUser(data);
      setLoading(false);
    };
    fetchUser();
  }, [id]);

  if (loading) return <div className="p-20 text-center text-secondary font-bold text-xl">Loading profile...</div>;
  if (!user) return <div className="p-20 text-center text-red-500 font-bold text-xl">Profile not found.</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Profile Info */}
        <div className="flex-grow">
          <Card className="p-8">
            <div className="flex items-center gap-8 mb-10 pb-10 border-b border-slate-100">
              <div className="w-40 h-40 rounded-full overflow-hidden border-4 border-slate-100 shadow-sm bg-slate-200">
                <img 
                  src={user.image_url || 'https://via.placeholder.com/400'} 
                  alt={user.full_name} 
                  className="w-full h-full object-cover" 
                />
              </div>
              <div>
                <div className="flex items-center gap-4 mb-2">
                  <h1 className="text-5xl font-bold text-primary tracking-tight">{user.full_name}</h1>
                  <span className="bg-secondary text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest">
                    {user.subscription_tier === 'premium' ? 'PREMIUM' : 'FREE'}
                  </span>
                </div>
                <p className="text-2xl text-slate-500 font-medium capitalize">{user.role.replace('_', ' ')}</p>
                {user.company_name && (
                  <p className="text-lg text-slate-400 mt-1">{user.company_name}</p>
                )}
              </div>
            </div>

            <div className="mb-12">
              <h2 className="text-2xl font-bold text-primary mb-6">Market Coverage</h2>
              <div className="flex flex-wrap gap-3">
                {user.locations?.length > 0 ? (
                  user.locations.map((loc: any) => (
                    <span 
                      key={loc.zip_code} 
                      className={`px-6 py-3 rounded-xl font-bold text-lg border transition-all ${
                        loc.is_primary 
                        ? 'bg-secondary/10 border-secondary text-primary shadow-sm ring-1 ring-secondary/20' 
                        : 'bg-slate-50 border-slate-200 text-slate-600'
                      }`}
                    >
                      {loc.zip_code}
                    </span>
                  ))
                ) : (
                  <p className="text-slate-400 italic">No markets listed yet.</p>
                )}
              </div>
            </div>

            <div className="mb-12">
              <h2 className="text-2xl font-bold text-primary mb-6">Recent Deals</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border border-slate-100 rounded-xl bg-slate-50/50">
                  <p className="text-slate-400 italic text-center py-4">No active deals posted by this user.</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-primary mb-6 text-secondary border-b pb-4">About</h2>
              <p className="text-xl text-slate-600 leading-relaxed max-w-3xl">
                {user.bio || `${user.full_name} is a real estate professional specializing in ${user.role.replace('_', ' ')} services. Connect with them to explore opportunities in their covered markets.`}
              </p>
            </div>
            
            <div className="mt-12 pt-10 border-t border-slate-100 flex gap-4">
              <Button variant="secondary" size="lg" className="px-10 py-5 text-xl">
                Send Message
              </Button>
              <Button variant="outline" size="lg" className="px-10 py-5 text-xl">
                Connect
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
