import { useState } from "react";
import { api } from "../services/api"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export function LoginForm() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    
    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        try {
            const response = await api.post("/auth/login", { email, password});
            localStorage.setItem("token", response.data.access_token);
            console.log("Login successful!");
        } catch (err) {
            setError("Invalid email or password");
        }

    };

    return (
        <div className = "flex items-center justify-center min-h-screen bg-slate-900">
            <Card className = "w-[400px] bg-slate-950 border-slate-800 text-white">
                <CardHeader>
                    <CardTitle className = "text-2xl font-bold text-center">Welcome back!</CardTitle>
                    <CardDescription className = "text-center text-slate-400">
                        We're so excited to see you again!
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin} className = "space-y-4">
                        <div className = "space-y-2">
                            <Label htmlFor="email" className = "text-slate-300 uppercase text-xs font-bold">
                                Email
                            </Label>
                            <Input
                                id = "email"
                                type = "email"
                                value = {email}
                                onChange = {(e) => setEmail(e.target.value)}
                                className = "bg-slate-900 border-none focus-visible:ring-indigo-500"
                                required
                            />
                        </div>
                        <div className = "space-y-2">
                            <Label htmlFor = "password" className = "text-slate-300 uppercase text-xs font-bold">
                                Password
                            </Label>
                            <Input 
                                id="password" 
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-slate-900 border-none focus-visible:ring-indigo-500" 
                                required 
                            />
                        </div>

                        {error && <p className = "text-red-500 text-sm">{error}</p>}

                        <Button type = "submit" className = "w-full bg-indigo-500 hover:big-indigo-600 text-white font-semibold">
                            Log In
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}