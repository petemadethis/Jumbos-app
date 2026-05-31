import React from 'react';
import Button from './Button';
import Card, { CardContent } from './Card';
import Link from 'next/link';

interface DealCardProps {
  id: string;
  title: string;
  price: string;
  roi: string;
  zip: string;
  imageUrl: string;
}

const DealCard = ({ id, title, price, roi, zip, imageUrl }: DealCardProps) => {
  return (
    <Card className="flex flex-col h-full">
      <div className="relative aspect-video overflow-hidden">
        <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
        <div className="absolute top-2 right-2 bg-secondary text-primary px-2 py-1 rounded text-xs font-bold">
          ZIP {zip}
        </div>
      </div>
      <CardContent className="flex-grow flex flex-col justify-between p-5">
        <div>
          <h3 className="text-xl font-bold text-primary mb-2 leading-tight">{title}</h3>
          <div className="flex justify-between items-center mb-4">
            <span className="text-2xl font-bold text-secondary">{price}</span>
            <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-sm font-medium">
              ROI: {roi}
            </span>
          </div>
        </div>
        <Link href={`/marketplace/${id}`} className="w-full">
          <Button variant="secondary" fullWidth>View Details</Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export default DealCard;
