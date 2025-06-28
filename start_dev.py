#!/usr/bin/env python3
"""
AI Agent Education Platform - Development Startup Script
This script starts both backend and frontend services for development.
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class DevServer:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down services...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up running processes"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error cleaning up process: {e}")
    
    def check_prerequisites(self):
        """Check if required files and dependencies exist"""
        print("🔍 Checking prerequisites...")
        
        # Check if .env exists
        if not os.path.exists('.env'):
            print("❌ .env file not found")
            print("   Please copy env_template.txt to .env and configure your settings")
            return False
        
        # Check if backend dependencies are installed
        if not os.path.exists('venv'):
            print("❌ Virtual environment not found")
            print("   Please run 'python setup_dev.py' first")
            return False
        
        # Check if frontend is set up
        if not os.path.exists('frontend/package.json'):
            print("❌ Frontend not set up")
            print("   Please run 'python setup_dev.py' first")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🐍 Starting FastAPI backend...")
        
        if sys.platform.startswith('win'):
            activate_cmd = ['venv\\Scripts\\activate.bat', '&&']
        else:
            activate_cmd = ['source', 'venv/bin/activate', '&&']
        
        # For Windows, we need to use shell=True and a different approach
        if sys.platform.startswith('win'):
            cmd = 'venv\\Scripts\\activate.bat && cd backend && python main.py'
            process = subprocess.Popen(
                cmd, 
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            cmd = 'source venv/bin/activate && cd backend && python main.py'
            process = subprocess.Popen(
                cmd,
                shell=True,
                preexec_fn=os.setsid
            )
        
        self.processes.append(process)
        print("✅ Backend started on http://localhost:8000")
        return process
    
    def start_frontend(self):
        """Start the React frontend"""
        print("⚛️ Starting React frontend...")
        
        try:
            # Change to frontend directory and start
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd='frontend',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(process)
            print("✅ Frontend started on http://localhost:3000")
            return process
            
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js")
            return None
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to start...")
        time.sleep(3)
        
        # Check if services are responding
        try:
            import requests
            
            # Check backend
            backend_ready = False
            for i in range(10):
                try:
                    response = requests.get("http://localhost:8000/", timeout=2)
                    if response.status_code == 200:
                        backend_ready = True
                        break
                except:
                    time.sleep(1)
            
            if backend_ready:
                print("✅ Backend is ready")
            else:
                print("⚠️ Backend may not be ready yet")
                
        except ImportError:
            print("⚠️ requests library not available for health check")
    
    def show_info(self):
        """Show service information"""
        print("\n" + "="*60)
        print("🎓 AI Agent Education Platform - Development Mode")
        print("="*60)
        print("📍 Services:")
        print("   Backend API:  http://localhost:8000")
        print("   Frontend:     http://localhost:3000")
        print("   API Docs:     http://localhost:8000/docs")
        print("   Redis:        redis://localhost:6379")
        print("\n📖 Quick Actions:")
        print("   • Open http://localhost:3000 to use the platform")
        print("   • Visit http://localhost:8000/docs for API documentation")
        print("   • Press Ctrl+C to stop all services")
        print("="*60)
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        while self.running:
            try:
                time.sleep(5)
                
                # Check if processes are still running
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"⚠️ Process {i} has stopped")
                        
            except KeyboardInterrupt:
                break
    
    def run(self):
        """Main run method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Starting AI Agent Education Platform...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            sys.exit(1)
        
        try:
            # Start services
            backend_process = self.start_backend()
            if not backend_process:
                print("❌ Failed to start backend")
                sys.exit(1)
            
            time.sleep(2)  # Give backend time to start
            
            frontend_process = self.start_frontend()
            if not frontend_process:
                print("❌ Failed to start frontend")
                self.cleanup()
                sys.exit(1)
            
            # Wait for services to be ready
            self.wait_for_services()
            
            # Show information
            self.show_info()
            
            # Monitor processes
            self.monitor_processes()
            
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            self.cleanup()
            sys.exit(1)

def main():
    """Main function"""
    server = DevServer()
    server.run()

if __name__ == "__main__":
    main() 