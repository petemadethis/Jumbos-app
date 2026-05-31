import React from 'react';
import Link from 'next/link';

interface ProfessionalCardProps {
  id: string;
  name: string;
  role: string;
  zip: string;
  imageUrl: string;
}

const ProfessionalCard = ({ id, name, role, zip, imageUrl }: ProfessionalCardProps) => {
  return (
    <Link href={`/profile/${id}`} className="flex items-center p-4 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors cursor-pointer group">
      <div className="w-16 h-16 rounded-full overflow-hidden mr-4 border-2 border-slate-200 group-hover:border-secondary transition-all">
        <img src={imageUrl} alt={name} className="w-full h-full object-cover" />
      </div>
      <div className="flex-grow">
        <h3 className="text-lg font-bold text-primary group-hover:text-secondary transition-colors capitalize">{name}</h3>
        <p className="text-slate-500 text-sm capitalize">{role.replace('_', ' ')}</p>
      </div>
      <div className="text-slate-400 font-bold bg-slate-50 px-3 py-1 rounded-lg border border-slate-100 group-hover:border-secondary transition-colors">
        {zip}
      </div>
    </Link>
  );
};

export default ProfessionalCard;
