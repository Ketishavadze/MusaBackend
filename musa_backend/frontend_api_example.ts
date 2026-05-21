const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export type ApiUser = {
  id: number;
  name: string;
  username: string;
  email: string;
  isSeller: boolean;
  memberSince: string;
  earnings: string;
  rating: string;
};

let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(access: string | null, refresh: string | null) {
  accessToken = access;
  refreshToken = refresh;
  if (typeof window !== "undefined") {
    if (access) localStorage.setItem("musa_access", access);
    else localStorage.removeItem("musa_access");
    if (refresh) localStorage.setItem("musa_refresh", refresh);
    else localStorage.removeItem("musa_refresh");
  }
}

export function loadTokens() {
  if (typeof window === "undefined") return;
  accessToken = localStorage.getItem("musa_access");
  refreshToken = localStorage.getItem("musa_refresh");
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? JSON.stringify(body) ?? "API request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function login(email: string, password: string) {
  const data = await api<{ user: ApiUser; access: string; refresh: string }>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setTokens(data.access, data.refresh);
  return data.user;
}

export async function signup(payload: { name: string; username?: string; email: string; password: string }) {
  const data = await api<{ user: ApiUser; access: string; refresh: string }>("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setTokens(data.access, data.refresh);
  return data.user;
}

export const getMe = () => api<ApiUser>("/auth/me/");
export const getProducts = (search = "", category = "All Crafts") =>
  api(`/products/?search=${encodeURIComponent(search)}&category=${encodeURIComponent(category)}`);
export const registerStudio = (payload: { name: string; craft_type: string; description?: string }) =>
  api("/studios/me/", { method: "POST", body: JSON.stringify(payload) });
export const createProduct = (payload: { title: string; category: string; price: string; description?: string; image?: string }) =>
  api("/products/", { method: "POST", body: JSON.stringify(payload) });
export const addToCart = (product_id: number, qty = 1) =>
  api("/cart/", { method: "POST", body: JSON.stringify({ product_id, qty }) });
export const getCart = () => api("/cart/");
export const updateCartQty = (itemId: number, qty: number) =>
  api(`/cart/${itemId}/`, { method: "PATCH", body: JSON.stringify({ qty }) });
export const checkout = (gift_wrap: boolean) =>
  api("/orders/", { method: "POST", body: JSON.stringify({ gift_wrap }) });
