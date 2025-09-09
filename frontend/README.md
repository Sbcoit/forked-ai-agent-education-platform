# AI Agent Education Platform - Frontend

This is the frontend application for the AI Agent Education Platform, built with **Next.js 15**, **TypeScript**, and **Tailwind CSS**.

## 🚀 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **Theme**: Next Themes (dark/light mode support)

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── dashboard/         # User dashboard and analytics
│   ├── chat-box/          # Interactive chat interface
│   ├── agent-builder/     # AI agent creation tools
│   ├── marketplace/       # Community scenarios marketplace
│   ├── simulation-builder/  # PDF upload and simulation creation
│   ├── login/            # Authentication pages
│   ├── layout.tsx        # Root layout component
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── components/            # React components
│   ├── ui/               # shadcn/ui component library
│   ├── PersonaCard.tsx   # Persona display component
│   ├── SceneCard.tsx     # Scenario display component
│   └── theme-provider.tsx # Theme context provider
├── lib/                  # Utilities and configurations
│   ├── api.ts           # API client functions
│   ├── auth-context.tsx # Authentication context
│   └── utils.ts         # Utility functions
├── hooks/               # Custom React hooks
│   ├── use-mobile.tsx   # Mobile detection hook
│   └── use-toast.ts     # Toast notification hook
└── public/              # Static assets
```

## 🛠️ Available Scripts

### `npm run dev`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload automatically when you make edits.\
You will also see any lint errors in the console.

### `npm run build`

Builds the app for production to the `.next` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

### `npm run start`

Starts the production server after running `npm run build`.

### `npm run lint`

Runs ESLint to check for code quality issues.

## 🎨 Features

- **Modern UI**: Built with shadcn/ui components for a polished, accessible interface
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Dark/Light Mode**: Theme switching with system preference detection
- **Type Safety**: Full TypeScript support throughout the application
- **Form Validation**: Robust form handling with React Hook Form and Zod
- **API Integration**: Seamless communication with the FastAPI backend

## 🔧 Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (ensure backend is running)

## 📚 Key Pages

- **Dashboard** (`/dashboard`): User analytics and progress tracking
- **Chat Box** (`/chat-box`): Interactive AI conversations
- **Agent Builder** (`/agent-builder`): Create and customize AI agents
- **Marketplace** (`/marketplace`): Browse community scenarios
- **Simulation Builder** (`/simulation-builder`): Upload PDFs and create simulations
- **Login** (`/login`): User authentication

## 🎯 Component Library

The project uses [shadcn/ui](https://ui.shadcn.com/) for consistent, accessible UI components:

- **Layout**: Card, Sheet, Dialog, Drawer
- **Forms**: Input, Button, Select, Checkbox, Radio Group
- **Navigation**: Tabs, Breadcrumb, Navigation Menu
- **Feedback**: Toast, Alert, Progress, Skeleton
- **Data Display**: Table, Badge, Avatar, Chart

## 🌐 API Integration

The frontend communicates with the FastAPI backend through:

- **API Client** (`lib/api.ts`): Centralized API functions
- **Authentication** (`lib/auth-context.tsx`): User session management
- **Error Handling**: Comprehensive error boundaries and user feedback

## 🚀 Deployment

The application is optimized for deployment on platforms like:

- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- **Docker containers**

## 📖 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [TypeScript](https://www.typescriptlang.org/docs/)