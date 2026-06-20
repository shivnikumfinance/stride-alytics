import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Card, Input, Button } from "../components/ui";
import { useAuthStore } from "../store";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);
  const loading = useAuthStore((s) => s.loading);
  const error = useAuthStore((s) => s.error);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
      const redirect = (location.state as any)?.from?.pathname ?? "/";
      navigate(redirect, { replace: true });
    } catch {
      /* error already in store */
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Card title="Sign in to StrideAlytics" subtitle="Free screener & Greeks — no credit card" className="w-full max-w-md">
        <form onSubmit={onSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" className="w-full" loading={loading}>
            Sign in
          </Button>
        </form>
        <p className="text-sm text-gray-500 mt-4 text-center">
          No account?{" "}
          <Link to="/signup" className="text-indigo-600 hover:underline">
            Create one
          </Link>
        </p>
      </Card>
    </div>
  );
}
