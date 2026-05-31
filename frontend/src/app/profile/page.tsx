import React from 'react';
import Card, { CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function ProfilePage() {
  const user = {
    name: 'Jane Doe',
    role: 'Wholesaler',
    imageUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=400',
    activeZips: ['90210', '90001', '30303'],
    recentDeals: [
      { address: '1254 Elm Street', price: '$350,000' },
      { address: '978 Maple Avenue', price: '$420,000' },
    ]
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Profile Info */}
        <div className="flex-grow">
          <Card className="p-8">
            <div className="flex items-center gap-6 mb-10">
              <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-slate-100 shadow-sm">
                <img src={user.imageUrl} alt={user.name} className="w-full h-full object-cover" />
              </div>
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-4xl font-bold text-primary">{user.name}</h1>
                  <span className="bg-secondary/10 text-secondary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    PRO
                  </span>
                </div>
                <p className="text-xl text-slate-500 font-medium">{user.role}</p>
              </div>
            </div>

            <div className="mb-10">
              <h2 className="text-2xl font-bold text-primary mb-6">Active ZIP Codes</h2>
              <div className="flex flex-wrap gap-3">
                {user.activeZips.map(zip => (
                  <span key={zip} className="bg-slate-100 text-slate-700 px-6 py-3 rounded-xl font-bold text-lg border border-slate-200">
                    {zip}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-primary mb-6">Recent Deals</h2>
              <div className="space-y-4">
                {user.recentDeals.map((deal, idx) => (
                  <div key={idx} className="flex justify-between items-center py-4 border-b border-slate-100 last:border-0">
                    <p className="text-xl font-medium text-slate-700">{deal.address}</p>
                    <p className="text-xl font-bold text-primary">{deal.price}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <Button variant="secondary" size="lg" className="w-full mt-10 py-5 text-xl">
              Message
            </Button>
          </Card>
        </div>

        {/* Messaging Interface Sidebar */}
        <div className="w-full lg:w-96">
          <Card className="h-full flex flex-col">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-2xl font-bold text-primary">Message</h2>
            </div>
            
            <div className="flex-grow p-6 space-y-6 overflow-y-auto min-h-[400px] bg-slate-50">
              <div className="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-200 max-w-[90%]">
                <p className="text-slate-700">
                  Hi, I'm getting in touch about the property listed at 1254 Elm Street.
                </p>
              </div>
            </div>
            
            <div className="p-6 border-t border-slate-200 bg-white">
              <textarea 
                placeholder="Type your message..." 
                className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent resize-none h-32 mb-4"
              />
              <Button variant="secondary" fullWidth size="lg">Send</Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
