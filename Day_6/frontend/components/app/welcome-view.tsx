import { Button } from '@/components/livekit/button';
import Image from 'next/image';

function WelcomeImage() {
  return (
    <div className="relative mb-8 flex justify-center">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl" />
      <div className="relative z-10 w-32 h-32 flex items-center justify-center">
        <svg
          className="w-full h-full text-blue-600 dark:text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
      </div>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-blue-50/30 dark:to-blue-950/10">
      <section className="flex flex-col items-center justify-center text-center px-4 py-12 max-w-3xl">
        <WelcomeImage />

        <h1 className="text-foreground text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent">
          SecureBank Fraud Alert
        </h1>

        <p className="text-foreground/90 text-lg md:text-xl max-w-2xl pt-2 leading-7 font-medium">
          24/7 AI-powered fraud detection system protecting your financial security
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 mb-8 w-full max-w-2xl">
          <div className="bg-card/50 backdrop-blur p-5 rounded-xl border border-border/50 hover:border-primary/50 transition-colors">
            <div className="text-3xl mb-2">🔒</div>
            <h3 className="font-semibold text-foreground mb-1">Real-Time Monitoring</h3>
            <p className="text-sm text-muted-foreground">Instant alerts for suspicious activity</p>
          </div>
          <div className="bg-card/50 backdrop-blur p-5 rounded-xl border border-border/50 hover:border-primary/50 transition-colors">
            <div className="text-3xl mb-2">🛡️</div>
            <h3 className="font-semibold text-foreground mb-1">Identity Verification</h3>
            <p className="text-sm text-muted-foreground">Secure multi-factor authentication</p>
          </div>
          <div className="bg-card/50 backdrop-blur p-5 rounded-xl border border-border/50 hover:border-primary/50 transition-colors">
            <div className="text-3xl mb-2">⚡</div>
            <h3 className="font-semibold text-foreground mb-1">Instant Response</h3>
            <p className="text-sm text-muted-foreground">Immediate fraud case resolution</p>
          </div>
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-4 px-8 py-6 text-lg font-semibold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all"
        >
          {startButtonText}
        </Button>

        <p className="text-muted-foreground text-sm mt-6">
          Connect with our AI fraud detection agent for immediate assistance
        </p>
      </section>
    </div>
  );
};
