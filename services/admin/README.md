# admin

Internal dashboard covering the services that don't have one of their own — currently `history` (events) and `notifications` (notifications, user replicas, email logs), alongside `tasks` (projects/boards/tasks/members). Talks directly to each service's REST API; not part of the RabbitMQ event flow described in the root [README](../../README.md).

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

## Configuring service endpoints

Each backend service's base URL is read from `.env` — see the root README's [Changing a service's host/port/route](../../README.md#changing-a-services-hostportroute) section for the full variable list and behavior. In short: edit `.env`, restart `npm run dev` (env vars are read at server start, not live).

## Adding a new view

1. Add the view component under `src/views/<service>_service/`.
2. Register its route in `src/router.js`.
3. Add an entry to `navItems` in `src/router.js` so it shows up in the navbar — either a plain `{ label, path }` link, or `{ label, path, children: [...] }` if the service has more than one top-level view (renders as a hover dropdown, see `Navbar.vue`).
4. If it's a new backend service, add its base URL to `.env` / `.env.example` and use it via `import.meta.env.VITE_..._API_URL`.

## Project Setup

```sh
npm install
npm run dev      # dev server with hot reload
npm run build     # production build
npm run preview   # preview the production build
```

See the [Vite Configuration Reference](https://vite.dev/config/) for build customization.
