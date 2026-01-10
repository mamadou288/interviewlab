# InterviewLab Frontend

Vue.js frontend application for InterviewLab - AI-powered interview practice platform.

## Tech Stack

- **Vue 3** with TypeScript
- **Vue Router** for routing
- **Pinia** for state management
- **Axios** for API calls
- **Tailwind CSS** for styling
- **Headless UI** for accessible components
- **Vite** for build tooling

## Project Setup

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Project Structure

```
src/
  ├── components/     # Reusable components
  ├── pages/          # Page components
  │   ├── auth/       # Authentication pages
  │   ├── profile/    # Profile pages
  │   ├── interviews/ # Interview pages
  │   ├── analytics/  # Analytics pages
  │   └── plans/      # Plan pages
  ├── stores/         # Pinia stores
  ├── services/       # API services
  ├── types/          # TypeScript types
  ├── router/         # Vue Router configuration
  └── main.ts         # Application entry point
```

## Features

- ✅ User authentication (login/register)
- ✅ CV upload and profile management
- ✅ Role suggestions
- ✅ Interview creation and taking
- ✅ Real-time feedback
- ✅ Interview reports
- ✅ Upgrade plans
- ✅ Analytics dashboard

## Development

The app runs on `http://localhost:5173` by default (Vite dev server).

Make sure the backend API is running on `http://localhost:8000` (or update `VITE_API_BASE_URL`).

## API Integration

All API calls are handled through services in `src/services/`:
- `auth.ts` - Authentication endpoints
- `profile.ts` - Profile and CV endpoints
- `roles.ts` - Role catalog and suggestions
- `interviews.ts` - Interview sessions and questions
- `plans.ts` - Upgrade plans
- `analytics.ts` - Analytics data

## State Management

Pinia stores are located in `src/stores/`:
- `auth.ts` - Authentication state
- `profile.ts` - Profile state
- `analytics.ts` - Analytics state

## Routing

Routes are defined in `src/router/index.ts`. Protected routes require authentication and will redirect to login if not authenticated.
