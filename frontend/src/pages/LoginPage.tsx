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
  const devAdminLogin = useAuthStore((s) => s.devAdminLogin);

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
      <Card title="Sign in to StrideAlytics" subtitle="Works on mobile, tablet, and desktop" className="w-full max-w-md">
        <form onSubmit={onSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" className="w-full" loading={loading}>
            Sign in
          </Button>
          <button
            type="button"
            onClick={() => {
              devAdminLogin();
              navigate("/", { replace: true });
            }}
            className="w-full mt-2 rounded-md border border-gray-300 bg-white py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Continue as Admin (dev)
          </button>
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
