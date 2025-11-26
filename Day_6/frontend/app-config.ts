export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'SecureBank',
  pageTitle: 'SecureBank - Fraud Alert System',
  pageDescription: 'Secure fraud detection and verification system powered by AI to protect your account',
  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/logo.png',
  accent: '#1e40af',
  logoDark: '/logo.png',
  accentDark: '#3b82f6',
  startButtonText: 'Connect to Fraud Department',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};

