import { UserManager, WebStorageStateStore } from "oidc-client-ts";

export const isDemo = process.env.NEXT_PUBLIC_AUTH_MODE === "demo";
let manager: UserManager | undefined;

export function getUserManager(): UserManager {
  if (!manager) {
    const authority = process.env.NEXT_PUBLIC_COGNITO_AUTHORITY;
    const clientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID;
    if (!authority || !clientId) throw new Error("School sign-in has not been configured.");
    manager = new UserManager({
      authority,
      client_id: clientId,
      redirect_uri: `${window.location.origin}/auth/callback`,
      response_type: "code",
      scope: "openid email profile",
      automaticSilentRenew: false,
      userStore: new WebStorageStateStore({ store: window.sessionStorage }),
      stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
    });
  }
  return manager;
}

export async function getAccessToken(): Promise<string | null> {
  if (isDemo) return null;
  const user = await getUserManager().getUser();
  if (!user || user.expired) throw new Error("Please sign in to your school account.");
  return user.access_token;
}

export async function signIn() {
  await getUserManager().signinRedirect();
}

export async function signOut() {
  const domain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN;
  const clientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID;
  if (!domain || !clientId) throw new Error("School sign-out has not been configured.");
  await getUserManager().removeUser();
  const url = new URL("/logout", domain);
  url.searchParams.set("client_id", clientId);
  url.searchParams.set("logout_uri", window.location.origin);
  window.location.assign(url.toString());
}
