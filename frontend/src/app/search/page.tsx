'use client';

import { useState, useEffect } from 'react';
import { locationApi, userApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import ProfessionalCard from '@/components/ui/ProfessionalCard';

export default function SearchPage() {
  const [states, setStates] = useState<any[]>([]);
  const [cities, setCities] = useState<any[]>([]);
  const [zips, setZipcodes] = useState<any[]>([]);
  
  const [filters, setFilters] = useState({
    state: '',
    city: '',
    zip: '',
    role: '',
    q: '',
  });

  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStates = async () => {
      const data = await locationApi.getStates();
      if (data) setStates(data);
    };
    fetchStates();
    handleSearch();
  }, []);

  const handleStateChange = async (stateCode: string) => {
    setFilters({ ...filters, state: stateCode, city: '', zip: '' });
    if (stateCode) {
      const data = await locationApi.getCities(stateCode);
      if (data) setCities(data);
    } else {
      setCities([]);
    }
    setZipcodes([]);
  };

  const handleCityChange = async (cityId: string) => {
    const city = cities.find(c => c.id.toString() === cityId);
    setFilters({ ...filters, city: city?.name || '', zip: '' });
    if (cityId) {
      const data = await locationApi.getZipcodes(parseInt(cityId));
      if (data) setZipcodes(data);
    } else {
      setZipcodes([]);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.q) params.q = filters.q;
      if (filters.role) params.role = filters.role;
      if (filters.state) params.state_code = filters.state;
      if (filters.city) params.city = filters.city;
      if (filters.zip) params.zip_code = filters.zip;

      const data = await userApi.search(params);
      if (data?.items) {
        setResults(data.items);
      }
    } catch (err) {
      console.error('Search failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-primary mb-12 text-center">
        Professional Directory
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-6 bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
          <Input 
            label="Search Name" 
            placeholder="Jane Doe" 
            value={filters.q}
            onChange={(e) => setFilters({...filters, q: e.target.value})}
          />

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Role</label>
            <select 
              className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
              value={filters.role}
              onChange={(e) => setFilters({...filters, role: e.target.value})}
            >
              <option value="">All Roles</option>
              <option value="agent">Agent</option>
              <option value="investor">Investor</option>
              <option value="wholesaler">Wholesaler</option>
              <option value="contractor">Contractor</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">State</label>
            <select 
              className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
              value={filters.state}
              onChange={(e) => handleStateChange(e.target.value)}
            >
              <option value="">Select State</option>
              {states.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">City</label>
            <select 
              className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
              value={cities.find(c => c.name === filters.city)?.id || ''}
              onChange={(e) => handleCityChange(e.target.value)}
              disabled={!filters.state}
            >
              <option value="">Select City</option>
              {cities.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">ZIP Code</label>
            <select 
              className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-secondary focus:border-secondary transition-colors bg-white appearance-none"
              value={filters.zip}
              onChange={(e) => setFilters({...filters, zip: e.target.value})}
              disabled={!filters.city}
            >
              <option value="">Select ZIP</option>
              {zips.map(z => <option key={z.code} value={z.code}>{z.code}</option>)}
            </select>
          </div>

          <Button fullWidth variant="secondary" onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Apply Filters'}
          </Button>
        </div>

        {/* Results Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden divide-y divide-slate-100">
            {results.length > 0 ? (
              results.map((prof) => (
                <ProfessionalCard 
                  key={prof.id}
                  id={prof.id}
                  name={prof.full_name}
                  role={prof.role}
                  zip={prof.primary_zip || 'N/A'}
                  imageUrl={prof.image_url || 'https://via.placeholder.com/150'}
                />
              ))
            ) : (
              <div className="p-12 text-center text-slate-500">
                {loading ? 'Searching for professionals...' : 'No professionals found matching your criteria.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
