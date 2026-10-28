# GitHub publishing checklist

- [ ] Create a new GitHub repository (for example, `travel-itinerary-planner`).
- [ ] Upload the contents of this folder, not the ZIP itself, if using GitHub's web interface.
- [ ] Replace `YOUR-USERNAME` in the README clone command with your GitHub username.
- [ ] Configure your real API keys and Supabase credentials in local `.env` files or your deployment provider's environment settings.
- [ ] Never commit `.env` files, API keys, service-role keys, access tokens, or database credentials.
- [ ] Check that `.env.example` contains placeholders only.

The package intentionally excludes `.git` history, real `.env` files, dependency folders, virtual environments, caches, and generated build output. Install dependencies locally using the README instructions.
