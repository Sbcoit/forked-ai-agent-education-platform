import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Bot, Users, Zap, Target, BookOpen, Play } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-yellow-500/20 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-yellow-500" />
            <span className="text-2xl font-bold">AgentCraft</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="hover:text-yellow-500 transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="hover:text-yellow-500 transition-colors">
              How it Works
            </Link>
            <Link href="#community" className="hover:text-yellow-500 transition-colors">
              Community
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" className="text-white hover:text-yellow-500">
              Sign In
            </Button>
            <Button asChild className="bg-yellow-500 text-black hover:bg-yellow-400">
              <Link href="/dashboard">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-yellow-500 to-white bg-clip-text text-transparent">
            Build AI Agents
            <br />
            <span className="text-yellow-500">Without Code</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Create, test, and deploy intelligent AI agents with our visual builder. Learn through hands-on experience
            and join a community of AI innovators.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-yellow-500 text-black hover:bg-yellow-400">
              <Link href="/dashboard">
                Start Building <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-yellow-500 text-yellow-500 hover:bg-yellow-500 hover:text-black bg-transparent"
            >
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-gray-900/50">
        <div className="container mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12">
            Everything You Need to <span className="text-yellow-500">Master AI Agents</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <Bot className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">Visual Agent Builder</CardTitle>
                <CardDescription className="text-gray-400">
                  Create AI agents with our intuitive drag-and-drop interface. No coding required.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <Users className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">Agent Marketplace</CardTitle>
                <CardDescription className="text-gray-400">
                  Discover, share, and remix agents created by the community.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <Target className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">Scenario Builder</CardTitle>
                <CardDescription className="text-gray-400">
                  Create complex scenarios from business cases or build them manually.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <Play className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">Live Simulation</CardTitle>
                <CardDescription className="text-gray-400">
                  Test your agents in real-time with our powerful simulation engine.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <BookOpen className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">Learn by Doing</CardTitle>
                <CardDescription className="text-gray-400">
                  Interactive tutorials and guided projects to master AI agent development.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="bg-black border-yellow-500/20 hover:border-yellow-500/40 transition-colors">
              <CardHeader>
                <Zap className="h-12 w-12 text-yellow-500 mb-4" />
                <CardTitle className="text-white">AI-Powered Tools</CardTitle>
                <CardDescription className="text-gray-400">
                  Leverage cutting-edge AI to analyze documents and suggest optimal agent configurations.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12">
            How It <span className="text-yellow-500">Works</span>
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500 text-black rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Build Your Agent</h3>
              <p className="text-gray-400">Define roles, goals, and capabilities using our visual builder</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500 text-black rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Create Scenarios</h3>
              <p className="text-gray-400">Upload business cases or manually design test scenarios</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500 text-black rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Run Simulations</h3>
              <p className="text-gray-400">Test your agents in realistic environments</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-500 text-black rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                4
              </div>
              <h3 className="text-xl font-semibold mb-2">Share & Learn</h3>
              <p className="text-gray-400">Publish to the marketplace and learn from the community</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-yellow-500/10 to-yellow-600/10">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Build Your First <span className="text-yellow-500">AI Agent</span>?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of developers and business professionals who are already building the future with AI agents.
          </p>
          <Button asChild size="lg" className="bg-yellow-500 text-black hover:bg-yellow-400">
            <Link href="/dashboard">
              Start Your Journey <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-yellow-500/20 py-12 px-4">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Bot className="h-6 w-6 text-yellow-500" />
              <span className="text-xl font-bold">AgentCraft</span>
            </div>
            <div className="flex space-x-6 text-gray-400">
              <Link href="#" className="hover:text-yellow-500 transition-colors">
                Privacy
              </Link>
              <Link href="#" className="hover:text-yellow-500 transition-colors">
                Terms
              </Link>
              <Link href="#" className="hover:text-yellow-500 transition-colors">
                Support
              </Link>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-yellow-500/20 text-center text-gray-400">
            <p>&copy; 2024 AgentCraft. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
