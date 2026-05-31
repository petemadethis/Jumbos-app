'use client';

import { useState, useEffect } from 'react';
import { locationApi, dealApi } from '@/lib/api';
import DealCard from '@/components/ui/DealCard';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function MarketplacePage() {
  const [states, setStates] = useState<any[]>([]);
  const [filters, setFilters] = useState({
    state_code: '',
    zip_code: '',
    deal_type: '',
    q: '',
  });

  const [deals, setDeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStates = async () => {
      const data = await locationApi.getStates();
      if (data) setStates(data);
    };
    fetchStates();
    handleFilter();
  }, []);

  const handleFilter = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.q) params.q = filters.q;
      if (filters.state_code) params.state_code = filters.state_code;
      if (filters.zip_code) params.zip_code = filters.zip_code;
      if (filters.deal_type) params.deal_type = filters.deal_type;

      const data = await dealApi.list(params);
      if (data) {
        setDeals(data);
      }
    } catch (err) {
      console.error('Filter failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="flex flex-col md:flex-row gap-12">
        {/* Sidebar Filters */}
        <aside className="w-full md:w-72 space-y-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-primary mb-6">Marketplace Filters</h2>
            <div className="space-y-4">
              <Input 
                label="Keyword" 
                placeholder="Fixer-upper..." 
                value={filters.q}
                onChange={(e) => setFilters({...filters, q: e.target.value})}
              />
              
              <div className="space-y-1">
                <label className="block text-sm font-medium text-slate-700">Deal Type</label>
                <select 
                  className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
                  value={filters.deal_type}
                  onChange={(e) => setFilters({...filters, deal_type: e.target.value})}
                >
                  <option value="">All Types</option>
                  <option value="property_for_sale">Property for Sale</option>
                  <option value="property_wanted">Property Wanted</option>
                  <option value="joint_venture">Joint Venture</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="block text-sm font-medium text-slate-700">State</label>
                <select 
                  className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
                  value={filters.state_code}
                  onChange={(e) => setFilters({...filters, state_code: e.target.value})}
                >
                  <option value="">All States</option>
                  {states.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                </select>
              </div>

              <Input 
                label="ZIP Code" 
                placeholder="e.g. 33101" 
                value={filters.zip_code}
                onChange={(e) => setFilters({...filters, zip_code: e.target.value})}
              />

              <Button fullWidth className="mt-4" variant="secondary" onClick={handleFilter} disabled={loading}>
                {loading ? 'Filtering...' : 'Apply Filters'}
              </Button>
            </div>
          </div>
        </aside>

        {/* Deals Grid */}
        <div className="flex-grow">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-primary">Deal Marketplace</h1>
            <Button variant="primary">Post a Deal</Button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {deals.length > 0 ? (
              deals.map((deal) => (
                <DealCard 
                  key={deal.id}
                  id={deal.id}
                  title={deal.title}
                  price={`$${deal.price.toLocaleString()}`}
                  roi={deal.roi || 'N/A'}
                  zip={deal.zip_code}
                  imageUrl={deal.image_url || 'https://via.placeholder.com/800x450'}
                />
              ))
            ) : (
              <div className="col-span-full py-20 text-center bg-white rounded-xl border border-dashed border-slate-300">
                <p className="text-slate-500 text-lg">
                  {loading ? 'Fetching deals...' : 'No deals found in this area yet.'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
