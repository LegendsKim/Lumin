# Lumin Frontend - האור של העסק שלך

React frontend application for Lumin SaaS - Multi-Tenant Inventory & Sales Management System.

## 🎨 Design System

### Brand Colors
- **Primary (Turquoise)**: `#00ADB5`
- **Gradient**: Purple (`#8c7ae6`) → Pink (`#f64e60`)
- **Neutrals**: Gray scale from `#F9FAFB` to `#111827`

### Typography
- **Hebrew**: Heebo font family
- **English/Numbers**: Inter font family

### Key Features
- ✨ RTL (Right-to-Left) support for Hebrew
- 🎨 Tailwind CSS with custom Lumin design tokens
- 📱 Fully responsive design
- ♿ Accessibility-first approach
- 🌓 Smooth animations and transitions

## 🚀 Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Server State**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Routing**: React Router DOM v6
- **Icons**: Lucide React
- **Charts**: Recharts
- **Notifications**: React Hot Toast

## 📦 Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup Steps

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your backend API URL
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

   App will be available at `http://localhost:5173`

4. **Build for Production**
   ```bash
   npm run build
   ```

5. **Preview Production Build**
   ```bash
   npm run preview
   ```

## 📂 Project Structure

```
lumin-frontend/
├── src/
│   ├── features/          # Feature modules
│   │   ├── auth/          # Authentication
│   │   ├── dashboard/     # Dashboard & Analytics
│   │   ├── inventory/     # Inventory Management
│   │   ├── sales/         # Sales & Orders
│   │   └── customers/     # CRM
│   ├── components/        # Reusable components
│   │   ├── layout/        # Layout components
│   │   └── ui/            # UI components
│   ├── config/            # Configuration
│   │   ├── api.js         # Axios setup
│   │   └── constants.js   # Global constants
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── styles/            # Global styles
│   │   └── index.css      # Tailwind + custom styles
│   ├── App.jsx            # Root component
│   └── main.jsx           # Entry point
├── public/                # Static assets
├── index.html             # HTML template
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies
```

## 🎯 Development Guidelines

### RTL Support
- All layouts are RTL by default
- Numbers and English text use `.ltr` class
- Icons may need `.rtl-flip` class for proper orientation

### Component Naming
- Use PascalCase for component files: `MyComponent.jsx`
- Use camelCase for utility files: `myUtility.js`

### Styling
- Prefer Tailwind utility classes
- Use custom classes from `styles/index.css` when needed
- Follow BEM naming for custom classes if required

### State Management
- **Global State**: Zustand (auth, tenant, user)
- **Server State**: TanStack Query (API data)
- **Local State**: useState, useReducer

## 🧪 Testing (Future)
```bash
npm run test
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🔗 Related

- Backend: `../lumin-backend`
- Docs: See `Lumin Project.txt` for full specification

## 📄 License

Proprietary - All rights reserved
