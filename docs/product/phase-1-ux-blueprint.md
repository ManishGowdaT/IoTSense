# Phase 1 — Product flows and UX architecture

**Status:** Draft UX blueprint, ready for review.

**Purpose:** Define who uses IoTSense, how they move through the product, and what each of its 20 screens must communicate before visual design and UI implementation begin.

**Product boundary:** IoTSense supports washroom monitoring and facility operations. Sensor outputs are indicators; they do not establish pathogen presence, medical risk, or microbiological cleanliness. Live readings, derived estimates and simulation data must be distinguished everywhere.

## 1. Product goals

1. Let facility teams see which washrooms need attention and why.
2. Show the age, source and quality of the data behind each status.
3. Turn incidents into trackable cleaning work.
4. Let administrators manage sites, devices, users and operating thresholds.
5. Support demos and development through simulation without presenting generated values as hardware observations.

## 2. Primary roles

- **Super Admin:** Manages the platform and organizations; has broad administrative access.
- **Facility Admin:** Manages a facility’s washrooms, devices, staff, settings and operations.
- **Maintenance Staff:** Views assigned facilities, acknowledges or updates operational work as allowed, and records cleaning activity.
- **Viewer:** Reads dashboards, washroom status and permitted analytics without changing operational or administrative records.

Role names describe product permissions, not job titles. An organization boundary must be enforced on the server for every record and action.

## 3. Information architecture

### Global shell

- **Top bar:** organization/site selector when available; page title/breadcrumb; notifications; user menu.
- **Primary navigation:** Dashboard; Washrooms; Hygiene Analysis; Alerts; Cleaning Operations; Analytics.
- **Supporting navigation:** Devices; Administration (Users, Settings, Audit Logs); System Health.
- **Mobile:** compact menu/drawer with the same destinations and current-page indication.
- **Persistent context:** current organization/site and data mode. When relevant, show **LIVE HARDWARE**, **SIMULATION**, or **SAMPLE DATA** with last live update.

### Navigation priorities

1. **Daily operations:** Dashboard, Washrooms, Alerts, Cleaning Operations.
2. **Investigation:** Washroom Detail, Sensors, Hygiene Analysis, Cause Identification, Analytics.
3. **Administration:** Devices, Provisioning, Users and Roles, Settings, Audit Logs, System Health.
4. **Account:** Profile, Login and Forgot Password.

### Global state vocabulary

| State | Meaning | UX treatment |
|---|---|---|
| Clean | Current score falls in the approved clean band | Green plus explicit “Clean” text; show last update and score explanation |
| Moderate | Current score falls in the approved moderate band | Amber plus explicit “Moderate” text; identify contributing indicators |
| Dirty | Current score falls in the approved dirty band | Red plus explicit “Dirty” text; offer investigation/alert workflow |
| Cleaning | A cleaning task is currently in progress | Blue/purple plus task owner and start time |
| Offline | Device cannot currently report | Grey plus last-seen time; do not show stale readings as current |
| Stale | Data is older than the configured freshness window | Warning label and age; mark resulting score as stale/unknown as rules specify |
| Sensor issue | One or more inputs are missing, invalid or uninitialized | Identify affected input; suppress unsupported score/cause claims |
| Unknown | Insufficient valid data to assign a meaningful state | Neutral state; explain what is missing |
| Simulation | Values are generated for demo/development | Persistent simulation banner and scenario name; never label as live |

Clean/moderate/dirty thresholds are configurable product rules and must be approved/versioned before being treated as validated measurements.

## 4. Role and action matrix

Legend: **Manage** = create/update/delete or administer; **Operate** = perform operational action; **Read** = view; **Own** = own account; **—** = no access by default. Server-side authorization is authoritative.

| Capability / screen | Super Admin | Facility Admin | Maintenance Staff | Viewer |
|---|---:|---:|---:|---:|
| Landing page | Read | Read | Read | Read |
| Login / forgot password | Own | Own | Own | Own |
| Dashboard | Read all orgs | Read own org | Read assigned sites | Read permitted sites |
| Washrooms list/detail | Manage all orgs | Manage own org | Read assigned sites | Read permitted sites |
| Sensor detail / hygiene analysis / cause identification | Read all orgs | Read own org | Read assigned sites | Read permitted sites |
| Analytics | Read all orgs | Read own org | Read assigned sites | Read permitted sites |
| Alerts / incidents | Manage all orgs | Operate own org | Operate assigned incidents | Read permitted incidents |
| Cleaning operations | Manage all orgs | Manage/operate own org | Operate assigned tasks; record events | Read permitted tasks/history |
| Cleaning-event verification | Read all orgs | Review own org | Record own task evidence | Read permitted evidence |
| Devices | Manage all orgs | Manage own org | Read assigned devices; report issue | Read permitted device status |
| Device provisioning | Manage all orgs | Manage own org | — | — |
| Users and roles | Manage all orgs | Manage own org, excluding platform-level roles | — | — |
| Settings | Manage platform | Manage own org | — | — |
| Audit logs | Read all orgs | Read own org | — | — |
| System health | Manage/read platform | Read own org/device health | Read assigned device health only | — |
| Profile | Own | Own | Own | Own |

### Authorization notes

- Facility Admin cannot grant Super Admin privileges.
- Maintenance Staff can only see assigned facilities/tasks and cannot provision credentials or change scoring thresholds.
- Viewer access is read-only, including no alert acknowledgement, task updates, exports with restricted data, or settings changes unless a later explicit policy permits it.
- Super Admin access is audited. Cross-organization scope must be explicit in the UI.
- If a user lacks access, explain that access is unavailable without leaking whether another organization’s record exists.

## 5. Critical user journeys

### Journey A — Check today’s facility status

1. User signs in and lands on Dashboard.
2. Dashboard shows organization/site context, summary counts, current data mode and last live update.
3. User filters or searches washrooms; each row shows status, freshness, active alert and cleaning state.
4. User opens a washroom; detail shows current/unknown state, available sensor readings, recent timeline and input health.
5. If data is stale/offline, user sees last-seen time and device troubleshooting path instead of a falsely current score.

**Success:** A user can tell which washroom needs attention, whether the information is fresh, and what evidence supports the status.

### Journey B — Investigate an alert and assign cleaning

1. Facility Admin or Maintenance Staff opens Alerts and filters to active/high priority.
2. User opens an incident and sees severity, affected washroom, evidence window, source mode, freshness and contributing indicators.
3. User acknowledges the incident; the actor and timestamp are recorded.
4. An authorized user creates or links a cleaning task and assigns staff/due time.
5. Maintenance Staff opens the task, reviews instructions, starts work and records completion/notes.
6. Detail screen shows before/after sensor observations only when available; otherwise verification is “unavailable.”
7. Authorized user resolves the incident with a resolution note; audit history is retained.

**Success:** Alert-to-task-to-completion is traceable without implying that sensor change proves cleanliness.

### Journey C — Understand a hygiene score or cause indicator

1. User opens Hygiene Analysis from Dashboard, Washroom Detail or an alert.
2. The page shows score band, score version, data quality, time window and last update.
3. User expands the explanation to inspect valid inputs, missing sensors, weighting/rules and thresholds.
4. User opens Cause Identification to see ranked indicators and supporting chart intervals.
5. UI uses cautious language such as “may be associated with” and displays confidence/quality limits.

**Success:** Every score/cause can be traced to recorded data and rules; no unsupported causal certainty is implied.

### Journey D — Provision a new ESP32 device

1. Facility Admin or Super Admin opens Devices → Provision Device.
2. User selects organization/site/washroom, enters device label and expected sensor capabilities.
3. System creates a device identity and one-time/revocable credential through a secure flow.
4. User follows setup instructions; credentials are shown only when required and are not written into public logs.
5. Device sends a first authenticated heartbeat/telemetry packet.
6. Device page confirms last-seen, firmware, registered sensors and any missing/invalid inputs.

**Success:** Device is bound to the intended washroom and its initial telemetry is authenticated, traceable and visible.

### Journey E — Review historical performance

1. User opens Analytics and chooses organization/site/washroom and period (30 min, 1 hour, 24 hours, 7 days or custom).
2. Charts distinguish raw observations, derived score and alert/task events.
3. Missing or offline intervals remain visible; tooltips expose units, time, source mode and quality.
4. Authorized user exports only data permitted by their role.

**Success:** Trends reconcile to stored observations without hiding gaps or blending simulation with live readings.

### Journey F — Demonstrate the product without hardware

1. Authorized user enters Simulation mode and chooses a named scenario.
2. Persistent banner identifies simulation and scenario across dashboard/detail/analytics.
3. Scenario produces coherent status, sensor cards, alerts and cleaning events with synthetic timestamps/labels.
4. User exits/reset simulation; live state remains separate and no synthetic event is stored as device telemetry.

**Success:** A demo is repeatable and no viewer mistakes generated values for hardware readings.

### Journey G — Recover a user account

1. User chooses Forgot Password on Login.
2. User submits an email; response does not reveal whether the account exists.
3. User follows a single-use, time-limited reset link and sets a new password.
4. Old sessions are invalidated according to the session policy; action is audited without logging the reset token.

**Success:** Account recovery is secure and does not expose account enumeration information.

## 6. Screen-by-screen low-fidelity blueprint

These are content/layout specifications, not final visual designs. Each page must support loading, empty, error, permission and responsive states where applicable.

| # | Screen | Purpose and low-fidelity layout | Main actions | Role / required data states |
|---:|---|---|---|---|
| 1 | Landing | Top navigation; product statement; sample status card; how-it-works steps; capabilities and limitations; footer | View demo; sign in | Public; sample state visibly marked; no unsupported AI/health claims |
| 2 | Login | Centered form; email/password; remember/session help; links to reset | Sign in | Public; validation, locked/throttled and server-error states |
| 3 | Forgot Password | Short explanation; email form; generic confirmation | Request reset | Public; do not disclose account existence |
| 4 | Dashboard | Header/site selector; status summary; alerts/tasks; washroom table/cards; recent trend; mode/freshness banner | Filter/site select; open washroom/alert/task | All authenticated roles, scoped; empty site, stale, offline, simulation |
| 5 | Washrooms | Search/filter; table/list with name, location, status, freshness, active alert, cleaning state | Search/filter; open; admin create/edit | Read according to scope; manage for Super/Facility Admin |
| 6 | Washroom Detail / Live Monitor | Washroom identity/status; score explanation; sensor cards; timeline; device/input health; active alerts and tasks | Open analysis/sensors; acknowledge/create task where allowed | Scoped access; never imply stale values are current |
| 7 | Sensor Detail | Sensor identity/type/pin or device metadata; current raw/normalized values; validity and last read; historical chart | Select range; inspect device | Read scoped; missing, invalid, warm-up and offline states |
| 8 | Hygiene Analysis | Score/band; engine version; data completeness; contributing indicators; time-series and thresholds | Select period; inspect inputs | Read scoped; unknown if insufficient valid data |
| 9 | Cause Identification | Ranked possible contributors; evidence cards with supporting periods and quality; cautious explanation | Open evidence chart; navigate to sensor/alert | Read scoped; no causal certainty; show low confidence/unknown |
| 10 | Analytics | Filter bar; site/washroom/time; trend charts, comparison and event overlays | Filter; export if authorized | Read scoped; visible gaps; live/simulation series separated |
| 11 | Alerts / Incidents | Status/severity filters; incident list; selected incident evidence/detail panel | Acknowledge; resolve; create/link task | Operate for admins/staff; Viewer read-only; deduped states |
| 12 | Cleaning Operations | Task board/list with status, washroom, assignee, due time; filters | Create/assign/start/complete/cancel as allowed | Staff assigned tasks; admins manage; Viewer read-only |
| 13 | Cleaning-event Verification | Task/event timeline; human completion record; before/after readings if available; evidence quality | Add note/evidence; review; link/resolution | Record for assigned staff; review for admins; unavailable state supported |
| 14 | Devices | Device list/status, washroom binding, firmware, last seen and sensor health | Open device; edit/revoke if authorized | Read scope; offline/missing sensors visible |
| 15 | Device Provisioning / Setup | Guided steps; organization/site/washroom; capability selection; credential instruction; first heartbeat status | Create/revoke/retry setup | Super/Facility Admin only; secret handling and one-time visibility |
| 16 | Users and Roles | User list, role, org/site scope, status, last sign-in | Invite/edit/deactivate/reset role | Super Admin all; Facility Admin own org; no staff/viewer management |
| 17 | Settings | Organization/site; score thresholds and versions; stale timeout; notification preferences; security controls | Save/version settings | Admin only; changes validated and audited |
| 18 | Audit Logs | Filterable timeline/table with actor, action, target, time, outcome | Search/filter/view event detail | Super Admin / scoped Facility Admin read; immutable records |
| 19 | System Health | API/database/ingestion health; latency/error summaries; telemetry lag; device offline summary | Inspect service/device detail | Super Admin; Facility Admin limited to own devices |
| 20 | Profile | Account details, password/session controls, preferences | Update profile/password; sign out/revoke sessions | Own account only |

## 7. Shared screen requirements

Every screen that displays sensor-derived information must provide, as applicable:

- **Source:** Live Hardware, Simulation or Sample Data.
- **Freshness:** reading timestamp and age; device last-seen where applicable.
- **Quality:** valid, partial, stale, warming up, missing or invalid input state.
- **Units and meaning:** raw measurement versus normalized index versus score.
- **Context:** selected organization/site/washroom and time zone.
- **Action:** clear next step for offline/alert/task states, permission permitting.

## 8. Phase 1 completion checklist

- [x] Product goals and boundaries documented.
- [x] Four roles and an initial access matrix defined.
- [x] Navigation hierarchy and global state vocabulary defined.
- [x] Critical journeys documented with success criteria.
- [x] All 20 screens have purpose, layout, actions and state requirements.
- [ ] Project owner reviews terminology, roles, screen order and first-release scope.
- [ ] Decisions from review are recorded before Phase 2 visual design begins.

## 9. Review decisions to confirm before Phase 2

1. Is the initial installation single-facility, multi-facility within one organization, or multi-organization from the first release?
2. Should Maintenance Staff be allowed to acknowledge alerts, or only update assigned cleaning tasks?
3. Should Viewers see detailed sensor readings and audit/event history, or only summaries and analytics?
4. Which screen should open after sign-in: Dashboard (recommended) or Washrooms?
5. Should the public Landing page be part of the first demonstrable release, or can it be deferred behind the authenticated app?

These choices affect visual flow and permissions, but do not block the current blueprint. Use the defaults represented above until review changes them.
