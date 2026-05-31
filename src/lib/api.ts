const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T | null> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('jumbos_token') : null;
  
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jumbos_token');
        // Optional: redirect to login
      }
      return null;
    }

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      console.error(`API Error (${res.status}):`, errorData);
      return null;
    }

    return await res.json();
  } catch (e) {
    console.error('API Fetch Exception:', e);
    return null;
  }
}

export const authApi = {
  login: async (email: string, password: string) => {
    const data = await apiFetch<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data?.access_token) {
      localStorage.setItem('jumbos_token', data.access_token);
      localStorage.setItem('jumbos_user', JSON.stringify(data.user));
    }
    return data;
  },
  register: async (userData: any) => {
    const data = await apiFetch<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (data?.access_token) {
      localStorage.setItem('jumbos_token', data.access_token);
      localStorage.setItem('jumbos_user', JSON.stringify(data.user));
    }
    return data;
  },
  logout: () => {
    localStorage.removeItem('jumbos_token');
    localStorage.removeItem('jumbos_user');
  },
  me: () => apiFetch<any>('/auth/me'),
};

export const locationApi = {
  getStates: () => apiFetch<any[]>('/locations/states'),
  getCities: (stateCode: string) => apiFetch<any[]>(`/locations/states/${stateCode}/cities`),
  getZipcodes: (cityId: number) => apiFetch<any[]>(`/locations/cities/${cityId}/zipcodes`),
  searchLocations: (q: string) => apiFetch<any[]>(`/locations/search?q=${encodeURIComponent(q)}`),
};

export const userApi = {
  search: (params: Record<string, string>) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch<any>(`/users/search?${query}`);
  },
  getProfile: (userId: string) => apiFetch<any>(`/users/${userId}`),
};

export const dealApi = {
  list: (params: Record<string, string>) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch<any>(`/deals/?${query}`);
  },
  get: (id: string) => apiFetch<any>(`/deals/${id}`),
  create: (dealData: any) => apiFetch<any>('/deals/', {
    method: 'POST',
    body: JSON.stringify(dealData),
  }),
};
