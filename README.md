# Cogniflow on GitHub Pages

The design is unchanged. This version fixes project-subdirectory links and builds a static GitHub Pages artifact. Signup, withdrawal and measurement call one configurable hosted API. GitHub Pages cannot run `server.py`.

## Status

**The hosted backend is not connected yet.** `config.js` currently has an empty API address. On a public Pages site, signup will show an honest unavailable message rather than claim to save data. Local Python preview still works and uses its own local database. Do not recruit visitors until the live backend is configured and tested.

The connected Supabase account has unrelated existing projects. No existing project was changed and no new project was created while the organisation choice is pending.

## Publish the page

1. Commit the folder contents, including the hidden `.github` directory, to your GitHub repository. Do not upload `data/`, any database, personal-data export or `local-backup/`. They are excluded by `.gitignore`.
2. In repository **Settings > Pages**, select **GitHub Actions** as the source.
3. Use the `main` branch, or change the branch in `.github/workflows/pages.yml` if needed. Push the files. The included workflow runs `build_site.py` and publishes only its explicit seven-file public allowlist from `dist/`.
4. After the backend is connected, test signup, withdrawal and anonymous measurement at the actual Pages URL before distributing recruitment links.

You can also run `python build_site.py` and publish only the resulting `dist/` contents using a separate static publishing branch. Do not select the entire repository root for branch-based publication, because it also contains local-only helper code.

## Hosted API configuration

`config.js` is public. It may contain the public API endpoint and a publishable client key. Never add a service-role key, database password or secret token.

```
window.COGNIFLOW_CONFIG = Object.freeze({
  apiBaseUrl: 'https://YOUR-HOSTED-API/research',
  publishableKey: 'PUBLIC-CLIENT-KEY-IF-REQUIRED'
});
```

The frontend appends `/signup`, `/event` or `/withdraw` to `apiBaseUrl`. The API must support JSON POST, cross-origin preflight from the GitHub Pages origin, and server-side validation. It must keep registrations private, deduplicate emails and measurement events, and return a withdrawal token only for a new signup. Private reporting must use the same cohort definitions as below. A generic form endpoint alone will not implement this entire contract.

- `POST /signup`: email, optional programme, true eligible/consent flags, recruitment channel, optional consenting visitor ID, and hidden honeypot field. Success: `{ "ok": true, "withdrawal": "PRIVATE-NEW-REGISTRATION-CODE" }`. Duplicate responses should not expose the existing code.
- `POST /event`: random visitor UUID, event `visit` or `cta`, channel and true self-declared eligible flag. Called only after optional measurement consent.
- `POST /withdraw`: private withdrawal token. Generic success after removing a matching active registration.
- Errors: non-2xx JSON with an `error` message. The frontend does not show success if the request fails.

The backend's identity, retention and contact information must be reflected in `privacy.html` before recruitment. Live data must stay on the backend, never in the GitHub repository. No account creation, payment or health-data access is implemented or implied.

## Experiment 2 reporting

Use links such as `https://USERNAME.github.io/REPOSITORY/?utm_source=campus_group`. The frontend preserves this source when submitting events or signups. Do not put names or emails in tracking URLs.

Visit counting is optional and self-selects an adult higher-education cohort. Deduplicate visits by visitor ID over the reporting window, not page loads. Report unique CTA clickers separately. Calculate conversion using only signups linked to eligible consenting visitors in the same source/window. Keep unmeasured signups separate from that numerator. The client waits for its pending visit request before signup, reducing measurement races.

Document consent-related sampling bias, browser resets, unverified email ownership, exclusions and the reporting window. Use at least 100 measured eligible unique visitors and a proposed 10% completed-registration threshold. Less traffic is inconclusive, not a failed hypothesis. Neither clicks nor registrations establish payment, retention or health outcomes.

Retain the public URL, full-page screenshot, channel links and posting dates, aggregate counts, spend and the actual findings. No public traffic results have been fabricated or collected as part of this adaptation.

## Local preview

Double-click `Start Cogniflow.cmd` or run `python server.py`, then open `http://127.0.0.1:8080`. While API configuration is empty, localhost uses the local Python API. Once a hosted API is configured, local preview uses that hosted API too, so do not mix test submissions with experiment data. Browser opening of `index.html` directly cannot provide local API functionality.

Local checks: `python test_server.py`, `python build_site.py`, and `node test_pages.cjs` (Node.js needed only for this last developer test). These checks do not prove that an unconfigured remote backend works.
