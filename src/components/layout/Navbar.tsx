'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Logo from '@/components/ui/Logo';
import Button from '@/components/ui/Button';

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userData = localStorage.getItem('jumbos_user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('jumbos_token');
    localStorage.removeItem('jumbos_user');
    setUser(null);
    window.location.href = '/';
  };

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          <div className="flex items-center">
            <Link href="/">
              <Logo />
            </Link>
            <div className="hidden md:ml-12 md:flex md:space-x-10">
              <Link 
                href="/search" 
                className={`${pathname === '/search' ? 'text-secondary' : 'text-slate-600'} hover:text-primary font-bold transition-colors`}
              >
                Directory
              </Link>
              <Link 
                href="/marketplace" 
                className={`${pathname.startsWith('/marketplace') ? 'text-secondary' : 'text-slate-600'} hover:text-primary font-bold transition-colors`}
              >
                Marketplace
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            {user ? (
              <>
                <Link 
                  href="/messages" 
                  className={`${pathname === '/messages' ? 'text-secondary' : 'text-slate-600'} hover:text-primary font-bold transition-colors`}
                >
                  Messages
                </Link>
                <Link href={`/profile/${user.id}`} className="flex items-center gap-3 group">
                  <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden border-2 border-transparent group-hover:border-secondary transition-all">
                    <img src={user.image_url || 'https://via.placeholder.com/100'} alt={user.full_name} className="w-full h-full object-cover" />
                  </div>
                  <span className="text-slate-700 font-bold group-hover:text-primary transition-colors hidden sm:inline">
                    {user.full_name.split(' ')[0]}
                  </span>
                </Link>
                <button 
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-red-500 font-medium transition-colors text-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-slate-600 hover:text-primary font-bold transition-colors">
                  Log in
                </Link>
                <Link href="/signup">
                  <Button variant="secondary" className="px-8 shadow-sm">Join Network</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
