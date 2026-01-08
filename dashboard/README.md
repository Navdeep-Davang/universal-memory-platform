# Universal Memory Engine Dashboard

A Next.js dashboard for managing and visualizing the Universal Cognitive Memory Engine.

## Features

- **System Overview:** Real-time stats on memory ingestion, graph nodes, and engine performance.
- **Query Playbox:** Interactive interface for testing recall and retrieval with detailed result metadata.
- **Conflict Resolution Center:** Manage contradictory memories and resolve them manually or via automated strategies.
- **Graph Explorer:** Visualize the complex relationships between entities, experiences, and contexts using D3.js.

## Tech Stack

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Visualization:** D3.js
- **API Communication:** Fetch API with built-in error handling

## Getting Started

1. **Configure Environment:**
   Create a `.env.local` file in the `dashboard/` directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_API_KEY=your-secret-api-key
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Run Development Server:**
   ```bash
   npm run dev
   ```

4. **Production Build:**
   ```bash
   npm run build
   ```

## API Integration

The dashboard communicates with the FastAPI backend. Ensure the backend is running and the `NEXT_PUBLIC_API_URL` is correctly set.
