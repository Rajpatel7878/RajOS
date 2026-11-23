# RAJOS V2 — Phase 11: Professional Frontend 2.0

## Overview

Phase 11 upgrades the RajOS frontend into a premium, production-quality AI operating system interface while preserving all working backend functionality. The design is inspired by Linear, Notion, Raycast, and modern AI SaaS dashboards, featuring a professional dark theme as the primary experience with optional light theme support.

## Design System

### Color Tokens
- **Charcoal**: `#0a0c12` - Primary background
- **Slate**: `#1e293b` - Card backgrounds
- **Sky**: `#38bdf8` - Primary accent
- **Cyan**: `#a78bfa` - Secondary accent
- **Emerald**: `#10b981` - Success/positive
- **Violet**: `#8b5cf6` - Intelligence/knowledge
- **Amber**: `#f59e0b` - Warnings/attention
- **Border**: `rgba(255, 255, 255, 0.08)` - Element borders
- **Muted**: `rgba(255, 255, 255, 0.4)` - Secondary text
- **Muted Foreground**: `rgba(255, 255, 255, 0.6)` - Tertiary text

### Typography Scale
- **Font Family**: `Inter`, `system-ui`, `sans-serif` (sans), `JetBrains Mono`, `ui-monospace`, `monospace` (mono)
- **Size**: xs(12px), sm(14px), base(16px), lg(18px), xl(22px), 2xl(28px), 3xl(36px), 4xl(48px)
- **Weight**: thin(100), light(300), regular(400), medium(500), semibold(600), bold(700)
- **Line Height**: tight, normal, relaxed, loose

### Spacing Scale
- **0**: 0px, **1**: 4px, **2**: 8px, **3**: 12px, **4**: 16px, **5**: 20px, **6**: 24px, **8**: 32px, **10**: 40px, **12**: 48px, **16**: 64px, **20**: 80px, **24**: 96px

### Border and Radius Tokens
- **Radius**: sm(calc(var(--radius) - 4px), md(calc(var(--radius) - 2px), lg(var(--radius))))
- **Border**: `rgba(255, 255, 255, 0.08)`

### Shadow Tokens
- **Depth**: `0 4px 12px -4px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.06)`
- **Glass**: `0 32px 64px -16px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.06)`
- **Glow Sky**: `0 0 40px -10px rgba(56,189,248,0.4), 0 0 80px -20px rgba(56,189,248,0.2)`
- **Glow Cyan**: `0 0 40px -10px rgba(34,211,238,0.4), 0 0 80px -20px rgba(34,211,238,0.2)`

## Application Layout

### Sidebar Navigation
- **Collapsible**: Persistent preference in localStorage
- **Responsive**: Collapses to icon-only mode on mobile
- **Sections**:
  - **WORKSPACE**: Dashboard, AI Chat, Search
  - **PRODUCTIVITY**: Tasks, Notes, Documents
  - **INTELLIGENCE**: Memory, Knowledge Base, AI Agents
  - **AUTOMATION**: Automations
  - **SYSTEM**: Settings
- **Active navigation indicator**: Highlighted with sky accent
- **Tooltips**: Visible when sidebar is collapsed

### Top Navigation
- **Current page title**: Prominent display with gradient cyan accent
- **Breadcrumbs**: Hierarchical navigation path
- **Global search**: Ctrl+K keyboard shortcut, expandable search dialog
- **Notifications**: Bell icon with unread count
- **Theme control**: Light/dark mode toggle
- **User profile menu**: Avatar with dropdown (profile, AI providers, notifications, security, sign out)

### Global Search Integration (Phase 10)
- **Keyboard shortcut**: Ctrl+K
- **Search suggestions**: Recent searches and resource matches
- **Resource filters**: Tasks, Notes, Documents, Memories, Agents
- **Recent searches**: Persistent history in localStorage
- **Keyboard navigation**: Arrow keys to navigate, Enter to select

## Pages Redesigned

### 1. Dashboard
- **Real backend data**: `getDashboardStats()`, `getDashboardActivity()`, `getDailyBrief()`
- **Loading skeletons**: During data fetch
- **Empty states**: When no data available
- **Error handling**: Clear error messages
- **Sections**:
  - Premium hero command center with 3D AI Core canvas
  - Quick metrics pills with gradient progress bars
  - Agent workforce telemetry
  - AI interaction load chart (AreaChart)
  - LLM provider distribution (PieChart)
  - Live activity timeline
  - Quick action command center tiles

### 2. AI Chat
- **Markdown rendering**: Using marked library
- **Code block rendering**: Syntax-highlighted code blocks
- **Thinking indicators**: Animated typing indicators
- **Message timestamps**: Per-message timestamps
- **Message differentiation**: User vs assistant bubbles
- **Features**:
  - New conversation button
  - Conversation history persistence
  - Search conversations
  - Copy response
  - Retry failed response
  - Agent execution with tool activity badges
  - Suggested tasks protocol
  - Memory integration indicators
  - Auto-scroll behavior
  - Loading and thinking indicators

### 3. Tasks
- **Real backend APIs**: `getTasks()`, `createTask()`, `completeTask()`, `toggleTaskStatus()`, `deleteTask()`
- **Functional task actions**: Edit, complete, delete
- **Priority indicators**: High/Normal/Low with color coding
- **Due dates**: Visual due date displays
- **Status filters**: All/Active/Completed filters
- **Sorting**: By due date, priority, alphabetical
- **Empty state**: When no tasks exist
- **Loading/error states**: Proper handling
- **Task timer integration**: Pomodoro-style timer

### 4. Notes
- **Notes list**: With search and filter
- **Create/edit**: Rich text content with save
- **Delete**: With confirmation
- **Empty state**: Welcome screen for new users
- **Updated timestamps**: Per-note modification times
- **Backend integration**: `getNotes()`, `createNote()`, `deleteNote()`

### 5. Documents
- **Document listing**: With processing status
- **Upload support**: Document upload functionality
- **Processing status**: Real-time processing indicators
- **Search**: Full-text search capability
- **Delete**: With confirmation
- **Source metadata**: Document origin information
- **Error states**: Clear error messages

### 6. Memory
- **View saved memories**: List with categories
- **Search memories**: Query-based search
- **Memory categories**: preference, goal, project, instruction, fact
- **Importance indicators**: Low/Medium/High/Critical
- **Backend integration**: `getMemories()`, `createMemory()`, `updateMemory()`, `deleteMemory()`, `getMemoryStats()`, `searchMemory()`

### 7. Knowledge Base
- **Knowledge document listing**: RAG-powered documents
- **Upload**: Document upload capability
- **Processing status**: Vectorization status indicators
- **Search**: Vector search integration
- **Document details**: Sources and metadata
- **Backend integration**: Existing RAG functionality

### 8. AI Agents
- **Agent listing**: With cards/rows
- **Agent descriptions**: Role and capabilities
- **Agent status**: Online/Offline indicators
- **Agent details**: Full configuration view
- **Create/edit agents**: Where supported
- **Run agent**: Execution progress monitoring
- **Execution history**: Past run records
- **Tool activity**: Where supported
- **Error handling**: Proper error states
- **Confirmation dialogs**: For risky operations

### 9. Automations
- **Automation list**: With enable/disable toggles
- **Create automation**: Wizard-style creation
- **Enable/disable**: Toggle switches
- **Edit**: Inline editing
- **Delete**: With confirmation dialog
- **Trigger information**: Source and conditions
- **Next scheduled execution**: Date/time display
- **Last execution**: Timestamp
- **Execution status**: Success/failure indicators
- **Run history**: Past executions
- **Failure details**: Error information
- **Phase 9 Automation Engine integration**

### 10. Analytics
- **Task completion trends**: Line charts over time
- **Productivity statistics**: Key metrics display
- **Task distribution**: Priority/status breakdown
- **Activity summaries**: Recent activity feed
- **Agent usage**: Agent interaction metrics
- **Automation execution statistics**: Run counts and success rates
- **Charts only where backend provides reliable data**
- **Empty states**: When data unavailable

### 11. Settings
- **General**: Basic configuration
- **Appearance**: Theme, color scheme
- **AI providers**: LLM provider configuration
- **Model configuration**: Temperature, max tokens
- **Notifications**: Alert preferences
- **Privacy**: Data retention and opt-outs
- **Security**: Token management, session settings
- **Application information**: Version, build info
- **Only settings backed by real APIs**

## API Integration

### Consistent API Client
- **Base URL**: Configured from backend deployment
- **Authentication**: JWT Bearer tokens via localStorage
- **Headers**: `Authorization: Bearer ${token}` on all requests
- **Error normalization**: Consistent error format across all services
- **Token handling**: Automatic token refresh where supported

### API Services
- **Dashboard**: `getDashboardStats()`, `getDashboardActivity()`, `getDailyBrief()`
- **Chat**: `sendMessage()`, `getHistory()`, `processExplicitMemory()`
- **Tasks**: `getTasks()`, `createTask()`, `completeTask()`, `toggleTaskStatus()`, `deleteTask()`
- **Notes**: `getNotes()`, `createNote()`, `deleteNote()`
- **Memory**: `getMemories()`, `createMemory()`, `updateMemory()`, `deleteMemory()`, `getMemoryStats()`, `searchMemory()`
- **Documents**: `getDocuments()`, `uploadDocument()`, `deleteDocument()`
- **Search**: Phase 10 unified search API
- **Agents**: Agent API and Tool Registry integration
- **Automations**: Phase 9 Automation Engine integration

### Request Configuration
- **One consistent API client**: `Frontend/services/api/client.ts`
- **Correct backend base URL**: Environment-configured
- **Authentication headers**: Consistent `Authorization: Bearer` format
- **Token handling**: LocalStorage persistence with renewal
- **Error normalization**: Unified error format
- **TypeScript types**: Full type safety across all API calls
- **Request cancellation**: Where appropriate for long-running operations

## Responsive Design

### Viewport Support
- **Desktop**: Full sidebar, expanded topbar
- **Laptop**: Full sidebar, compact topbar
- **Tablet**: Collapsible sidebar, mobile-style topbar
- **Mobile**: Hamburger menu, full-width content

### Design Patterns
- **Responsive sidebar**: Collapses from 280px to 80px
- **Mobile navigation**: Bottom drawer or off-canvas menu
- **Responsive tables**: Horizontally scrollable on narrow viewports
- **Flexible cards**: Graceful scaling with max-width constraints
- **Scrollable content**: Overflow-hidden with scrollbars where needed
- **Correct modal behavior**: Focus trap, escape key closure
- **Touch-friendly controls**: Minimum 44px tap targets
- **No horizontal overflow**: Constrained content width
- **Readable typography**: Scales based on viewport size

### Breakpoints
- **sm**: 640px - Mobile-first styles
- **md**: 768px - Tablet styles
- **lg**: 1024px - Laptop styles
- **xl**: 1280px - Desktop styles
- **2xl**: 1536px - Large desktop styles

## Accessibility

### Semantic HTML
- **Proper heading hierarchy**: h1-h6 in logical order
- **Landmark regions**: nav, main, aside, header, footer
- **Form labels**: Associated with inputs via for/id
- **Button labels**: Clear text descriptions

### Keyboard Navigation
- **Tab order**: Logical focus order
- **Escape key**: Close modals/dialogs
- **Focus indicators**: Visible focus rings (sky-400)
- **Keyboard shortcuts**: Documented and consistent (Ctrl+K for search)

### Accessible Forms
- **Labels**: All form controls have associated labels
- **Error messages**: Programmatically associated with fields
- **Validation**: Client-side with clear messages
- **Disabled state**: Keyboard-focusable where appropriate

### Dialog Accessibility
- **Focus trap**: Focus stays within modal
- **Escape key**: Close dialog
- **ARIA roles**: dialog, alertdialog as appropriate
- **Backdrop**: Dimming with safe close behavior

### Contrast
- **Minimum contrast ratio**: 4.5:1 for normal text, 3:1 for large text
- **Focus ring**: 3px sky-400 outline on focus
- **Inverted text**: On colored backgrounds

### Screen Reader Friendly
- **ARIA labels**: On interactive elements
- **Live regions**: For dynamic content updates
- **Roles**: Proper use of generic roles
- **Skip links**: To main content

## Performance

### Optimizations
- **Component rendering**: React.memo where beneficial
- **Lazy loading**: Route-level code splitting
- **Image handling**: Next.js Image component with blur-up technique
- **API request efficiency**: Debounced searches, cached responses
- **State management**: React Query or SWR patterns
- **Bundle size**: Minimized dependencies
- **Loading experience**: Skeleton screens during data fetch

### Performance Metrics
- **First Contentful Paint**: < 1.0s
- **Time to Interactive**: < 2.0s
- **Total Blocking Time**: < 100ms
- **Largest Contentful Paint**: < 2.5s

## Testing and Quality Checks

### TypeScript
- Full type safety across all components
- No `any` types where interfaces exist
- Comprehensive type coverage

### Lint
- ESLint configuration consistent with project
- Prettier formatting
- No lint errors on core files

### Build
- Production build succeeds
- No TypeScript errors
- No lint errors

### Manual Verification
1. Login and logout - JWT token management
2. Dashboard loading - Real backend data
3. AI Chat - Full functionality
4. Conversation history - Persistence
5. Global search - Ctrl+K integration
6. Tasks - Create, edit, complete, delete
7. Notes - Create, edit, delete
8. Documents - Upload, list, delete
9. Memory - View, search, add, edit, delete
10. Knowledge Base - View, search, upload
11. AI Agents - List, run, manage
12. Automations - Create, enable/disable, run history
13. Analytics - Metrics display
14. Settings - Configuration options
15. Mobile navigation - All viewports

## Known Limitations

- 3D AI Core canvas: SSR disabled, client-side only
- Some animation effects: Reduced on motion preference
- Offline functionality: Limited (token-dependent APIs)
- Real-time updates: Polling-based rather than websocket
- Some agent operations: Require Phase 9 engine availability

## Build and Commands

```bash
# Install dependencies
npm install

# TypeScript check
npx tsc --noEmit --skipLibCheck

# Lint
npm run lint

# Production build
npm run build

# Development
npm run dev
```

## Git Status

All changes made in Phase 11 are tracked. Key modified files:
- `Frontend/tailwind.config.ts` - Design tokens extended
- `Frontend/components/topbar.tsx` - Redesigned with global search
- `Frontend/components/sidebar.tsx` - Redesigned with collapsible functionality
- `Frontend/app/dashboard/page.tsx` - Premium redesign with real API data
- `Frontend/app/chat/page.tsx` - Markdown rendering, thinking indicators
- `Frontend/app/tasks/page.tsx` - Real backend API integration
- `Frontend/app/notes/page.tsx` - Already had good API integration
- `Frontend/app/documents/page.tsx` - Real API integration
- `Frontend/app/memory/page.tsx` - Full backend integration
- `Frontend/app/knowledge/page.tsx` - RAG integration
- `Frontend/app/analytics/page.tsx` - Real data charts
- `Frontend/app/settings/page.tsx` - Real configuration APIs

## Readiness for Phase 12

Phase 11 is complete when:
- Frontend has consistent professional design
- All main workspace pages integrated
- Dashboard uses real backend data
- AI Chat remains functional with markdown
- Tasks, Notes, Documents, Memory, Knowledge, Agents, Automations use real APIs
- Phase 10 search integrated
- Authentication functional
- Loading, empty, and error states implemented
- Mobile and desktop layouts work
- Production frontend build succeeds
- Existing functionality remains intact
- Documentation complete

Phase 12 would focus on: Streaming, Realtime & UX improvements.