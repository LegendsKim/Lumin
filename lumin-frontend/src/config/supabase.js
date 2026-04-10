/**
 * Supabase client configuration.
 * Used for authentication and direct DB operations from the frontend.
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error(
    'Missing Supabase env vars. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    // Use PKCE flow for maximum security (no client secret needed)
    flowType: 'pkce',
  },
});

/**
 * Get current session token for Django API calls.
 * Django validates the Supabase JWT server-side.
 */
export async function getAccessToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
}

/**
 * Sign in with Google OAuth via Supabase.
 */
export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/dashboard`,
    },
  });
  return { data, error };
}

/**
 * Sign out from Supabase.
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (!error) {
    window.location.href = '/login';
  }
  return { error };
}

/**
 * Get current user info.
 */
export async function getCurrentUser() {
  const { data: { user }, error } = await supabase.auth.getUser();
  return { user, error };
}

export default supabase;
