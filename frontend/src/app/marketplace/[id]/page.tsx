'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { dealApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Card, { CardContent } from '@/components/ui/Card';

export default function DealDetailPage() {
  const { id } = useParams();
  const [deal, setDeal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDeal = async () => {
      if (typeof id !== 'string') return;
      const data = await dealApi.get(id);
      if (data) setDeal(data);
      setLoading(false);
    };
    fetchDeal();
  }, [id]);

  if (loading) return <div className="p-20 text-center">Loading deal details...</div>;
  if (!deal) return <div className="p-20 text-center text-red-500">Deal not found.</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-primary mb-8">{deal.title}</h1>
      
      <div className="flex flex-col lg:flex-row gap-8 mb-8">
        {/* Main Image */}
        <div className="flex-grow">
          <div className="aspect-video rounded-xl overflow-hidden shadow-lg bg-slate-100">
            <img 
              src={deal.image_url || 'https://via.placeholder.com/1200x675'} 
              alt={deal.title} 
              className="w-full h-full object-cover" 
            />
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="w-full lg:w-80">
          <Card className="bg-[#10B981]/10 border-none">
            <CardContent className="flex flex-col items-center py-10 text-center">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4 border-4 border-white shadow-md bg-slate-200">
                <img 
                  src={deal.posted_by?.image_url || 'https://via.placeholder.com/200'} 
                  alt={deal.posted_by?.full_name} 
                  className="w-full h-full object-cover" 
                />
              </div>
              <p className="text-slate-600 mb-1">Posted by</p>
              <h2 className="text-2xl font-bold text-primary mb-6">
                {deal.posted_by?.full_name || 'System User'}
              </h2>
              <Button fullWidth className="bg-primary text-white hover:bg-primary/90">
                Direct Message
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        <Card className="bg-white text-center py-6">
          <p className="text-sm text-slate-500 mb-1 font-medium">Price</p>
          <p className="text-2xl font-bold text-primary">${deal.price.toLocaleString()}</p>
        </Card>
        <Card className="bg-white text-center py-6">
          <p className="text-sm text-slate-500 mb-1 font-medium">State</p>
          <p className="text-2xl font-bold text-primary">{deal.state_code}</p>
        </Card>
        <Card className="bg-white text-center py-6">
          <p className="text-sm text-slate-500 mb-1 font-medium">ZIP</p>
          <p className="text-2xl font-bold text-primary">{deal.zip_code}</p>
        </Card>
        <Card className="bg-white text-center py-6">
          <p className="text-sm text-slate-500 mb-1 font-medium">Type</p>
          <p className="text-xl font-bold text-primary capitalize">{deal.property_type.replace('_', ' ')}</p>
        </Card>
      </div>

      {/* Description */}
      <Card className="bg-white p-8">
        <h2 className="text-2xl font-bold text-primary mb-6 text-secondary border-b pb-4">Description</h2>
        <p className="text-slate-700 leading-relaxed text-lg whitespace-pre-wrap">
          {deal.description}
        </p>
      </Card>
    </div>
  );
}
