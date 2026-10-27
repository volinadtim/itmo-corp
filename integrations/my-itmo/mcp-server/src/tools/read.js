import { z } from "zod";
import { searchCatalog, sitemap } from "../catalog.js";
import { assertApiPath } from "../client.js";
import { currentWeek, defineTool } from "../format.js";
import { getPublicSchedule, searchPublicSchedule } from "../public-schedule.js";

const READ = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true };
const date = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD");

/** Parameter-free GET endpoints exposed through itmo_student_info. Keep this a closed list. */
export const INFO_SECTIONS = {
  dashboard: "/api/system/dashboard",
  dormitory_status: "/api/dormitory/status/full",
  dormitory_apartments: "/api/dormitory/apartments",
  dormitory_documents: "/api/dormitory/documents",
  sport_semester: "/api/sport/semesters/current",
  sport_semesters: "/api/sport/semesters/list",
  sport_score: "/api/sport/personal/score",
  sport_debt: "/api/sport/personal/debt",
  sport_health_level: "/api/sport/personal/health_level",
  sport_selections: "/api/sport/personal/selections",
  sport_chosen: "/api/sport/sign/chosen",
  sport_limits: "/api/sport/sign/schedule/limits",
  sport_filters: "/api/sport/sign/schedule/filters",
  sport_attempts: "/api/sport/personal/have_attempts",
  sport_briefings: "/api/sport/personal/briefing/list",
  sport_externat: "/api/sport/personal/externat",
  sport_competitions: "/api/sport/competitions/list",
  sport_projects: "/api/sport/projects/list",
  sport_types: "/api/sport/sport_types",
  practices_programs: "/api/practices/practices/op",
  election_availability: "/api/election/students/availability",
  election_selected_chains: "/api/election/students/selected_flow_chains",
  election_chosen_flows: "/api/election/students/chosen_flows",
  facultative_status: "/api/facultative/status/",
  intro_status: "/api/intro/status/",
  queues_current: "/api/queues/current",
  queues_archive: "/api/queues/archive",
  booking_status: "/api/booking/users/status",
  booking_mine: "/api/booking/bookings/my",
  booking_categories: "/api/booking/dictionary/rooms/categories",
  agreements: "/api/agreements/agreements",
  individual_plan_semester: "/api/individual-plan/semesters/current",
  individual_plan_role: "/api/individual-plan/plan/role",
  individual_plan_flags: "/api/individual-plan/flags",
  diplomas_mine: "/api/gia-students/diplomas/my",
};

const FINANCE_SECTIONS = {
  scholarship_total: "/api/finances/scholarship/total",
  scholarship_income: "/api/finances/scholarship/income",
  scholarship_account: "/api/finances/scholarship/account",
  tuition_contracts: "/api/finances/edupayments/contracts",
  tuition_payments: "/api/finances/edupayments/payments",
  tuition_availability: "/api/finances/edupayments/availability",
};

export function registerReadTools(server, { client, session }) {
  defineTool(
    server,
    "itmo_whoami",
    {
      title: "Who am I logged in as",
      description: "Show the ITMO ID account behind this MCP session (ISU number, email, token expiry). Logs in on first use. Never returns tokens.",
      inputSchema: {},
      annotations: READ,
    },
    () => session.whoami()
  );

  defineTool(
    server,
    "itmo_sitemap",
    {
      title: "Map of my.itmo.ru",
      description:
        "Map of the ITMO web properties: all my.itmo.ru pages (SPA routes), the live navigation menu for this account, and related sites. Use it to find which page/section covers a topic before choosing a tool.",
      inputSchema: { section: z.enum(["all", "pages", "menu", "sites"]).default("all") },
      annotations: READ,
    },
    async ({ section = "all" }) => {
      const map = sitemap();
      const out = { generatedAt: map.generatedAt };
      if (section === "all" || section === "pages") out.pages = map.routes;
      if (section === "all" || section === "menu") out.menu = map.menu ?? "run `node scripts/crawl-sitemap.mjs --probe` to include the live menu";
      if (section === "all" || section === "sites") out.sites = map.publicSites;
      return out;
    }
  );

  defineTool(
    server,
    "itmo_api_catalog",
    {
      title: "Search the my.itmo.ru API catalog",
      description:
        "Search the catalog of ~750 my.itmo.ru JSON endpoints extracted from the front-end. audience=student endpoints are for regular students; staff/adviser ones need other roles. liveStatus is the HTTP status seen by the last probe (200 = works for this account, 403 = no rights/not open now). Use itmo_api_get to call a GET endpoint.",
      inputSchema: {
        query: z.string().optional().describe("substring of the path, e.g. 'scholarship'"),
        module: z.string().optional().describe("first path segment after /api/, e.g. 'finances'"),
        audience: z.enum(["student", "mixed", "adviser", "staff"]).optional(),
        method: z.enum(["GET", "POST", "PUT", "PATCH", "DELETE"]).optional(),
        only_working: z.boolean().optional().describe("only endpoints that returned 200 in the last probe"),
        limit: z.number().int().min(1).max(300).default(80),
      },
      annotations: READ,
    },
    (args) => searchCatalog({ ...args, onlyWorking: args.only_working })
  );

  defineTool(
    server,
    "itmo_schedule",
    {
      title: "My timetable",
      description: "Personal class schedule from my.itmo.ru for a date range (default: the current Mon–Sun week, Moscow time). Empty days mean no classes are scheduled (e.g. between semesters).",
      inputSchema: {
        date_start: date.optional(),
        date_end: date.optional(),
      },
      annotations: READ,
    },
    async ({ date_start, date_end }) => {
      const week = currentWeek();
      const range = { date_start: date_start ?? week.start, date_end: date_end ?? week.end };
      const days = await client.get("/api/schedule/schedule/personal", range);
      const slots = await client.get("/api/schedule/meta/time_slots").catch(() => null);
      return { range, days, time_slots: slots };
    }
  );

  defineTool(
    server,
    "itmo_record_book",
    {
      title: "Gradebook (зачётная книжка)",
      description:
        "Grades and credits. Without arguments: lists study plans/semesters and returns the current ('actual') semester. With plan_id+semester_id: that semester. With est_id: details of one discipline (est_id comes from the semester list).",
      inputSchema: {
        plan_id: z.number().int().optional().describe("main_plan from the plans list"),
        semester_id: z.number().int().optional().describe("sem_id from the plans list, e.g. 202620271"),
        est_id: z.number().int().optional(),
      },
      annotations: READ,
    },
    async ({ plan_id, semester_id, est_id }) => {
      if (est_id) return client.get(`/api/record_book/${est_id}`);
      const plans = await client.get("/api/record_book/specializations");
      if (plan_id && semester_id) return client.get(`/api/record_book/${plan_id}/${semester_id}`);
      const plan = plans.find((p) => p.semesters?.some((s) => s.actual)) ?? plans[0];
      const sem = plan?.semesters?.find((s) => s.actual) ?? plan?.semesters?.[0];
      const disciplines = plan && sem ? await client.get(`/api/record_book/${plan.main_plan}/${sem.sem_id}`) : [];
      return { plans, shown: { plan_id: plan?.main_plan, semester: sem }, disciplines };
    }
  );

  defineTool(
    server,
    "itmo_requests",
    {
      title: "Requests (заявки)",
      description:
        "scope=mine: my submitted requests with statuses. scope=catalog: all request types grouped by category (ids are template ids for itmo_request_form). scope=mine_v2: requests of the new workflow engine. scope=tasks: my approval tasks.",
      inputSchema: { scope: z.enum(["mine", "catalog", "mine_v2", "tasks"]).default("mine") },
      annotations: READ,
    },
    ({ scope = "mine" }) =>
      client.get({ mine: "/api/requests/my", catalog: "/api/requests/all", mine_v2: "/api/requests/v2/requests/mine", tasks: "/api/requests/v2/requests/my-tasks" }[scope])
  );

  defineTool(
    server,
    "itmo_request_details",
    {
      title: "One of my requests",
      description: "Details of a request I submitted (entered fields, status, files). request_id comes from itmo_requests scope=mine.",
      inputSchema: { request_id: z.number().int() },
      annotations: READ,
    },
    ({ request_id }) => client.get(`/api/requests/my/${request_id}`)
  );

  defineTool(
    server,
    "itmo_request_form",
    {
      title: "Request form definition",
      description:
        "Fields of a request template (id, name, type, required, dictionary_id), whether I can apply now, and responsible units. Use before itmo_request_submit (write server). template_id comes from itmo_requests scope=catalog.",
      inputSchema: { template_id: z.number().int() },
      annotations: READ,
    },
    ({ template_id }) => client.get(`/api/requests/${template_id}`)
  );

  defineTool(
    server,
    "itmo_request_dictionary",
    {
      title: "Request form dictionary values",
      description: "Allowed values for a dictionary-type field of a request form (dictionary_id from itmo_request_form).",
      inputSchema: { dictionary_id: z.number().int(), params: z.record(z.string(), z.union([z.string(), z.number()])).optional() },
      annotations: READ,
    },
    ({ dictionary_id, params }) => client.get(`/api/requests/dict/${dictionary_id}`, params)
  );

  defineTool(
    server,
    "itmo_finances",
    {
      title: "Scholarship and tuition",
      description: `Money-related data. section: ${Object.keys(FINANCE_SECTIONS).join(" | ")}.`,
      inputSchema: { section: z.enum(Object.keys(FINANCE_SECTIONS)) },
      annotations: READ,
    },
    ({ section }) => client.get(FINANCE_SECTIONS[section])
  );

  defineTool(
    server,
    "itmo_student_info",
    {
      title: "Student services overview",
      description: `Read one of the parameter-free student sections. section: ${Object.keys(INFO_SECTIONS).join(" | ")}. A 403 usually means the service is closed for this account right now (e.g. no election window).`,
      inputSchema: { section: z.enum(Object.keys(INFO_SECTIONS)) },
      annotations: READ,
    },
    ({ section }) => client.get(INFO_SECTIONS[section])
  );

  defineTool(
    server,
    "itmo_sport_calendar",
    {
      title: "Physical-education calendar",
      description: "My PE (sport) lessons between two dates.",
      inputSchema: { date_start: date, date_end: date },
      annotations: READ,
    },
    ({ date_start, date_end }) => client.get("/api/sport/personal/calendar", { date_start, date_end })
  );

  defineTool(
    server,
    "itmo_sport_schedule",
    {
      title: "PE signup schedule",
      description:
        "Lessons open for PE signup (page /sport/sign): section, group, time, room, limit, free places, can_sign_in and other_lessons of the group. building_id comes from itmo_student_info section=sport_filters (-1 Online, 273 Ломоносова 9, 5 Вяземский 5-7, 0 other). Without dates the server answers 'filter not found'; keep ranges to ~2 weeks.",
      inputSchema: {
        building_id: z.number().int(),
        date_start: date,
        date_end: date,
        sport_type_id: z.array(z.number().int()).optional(),
        teacher_isu: z.array(z.number().int()).optional(),
      },
      annotations: READ,
    },
    ({ building_id, date_start, date_end, sport_type_id, teacher_isu }) => client.get("/api/sport/sign/schedule", { building_id, date_start, date_end, sport_type_id, teacher_isu })
  );

  defineTool(
    server,
    "itmo_people_search",
    {
      title: "Search people at ITMO",
      description: "Search the university directory (students and staff) by name via the personalities module.",
      inputSchema: { query: z.string().min(2), limit: z.number().int().min(1).max(50).default(10), offset: z.number().int().min(0).default(0) },
      annotations: READ,
    },
    ({ query, limit = 10, offset = 0 }) => client.get("/api/personalities/persons", { q: query, limit, offset })
  );

  defineTool(
    server,
    "itmo_api_get",
    {
      title: "Raw GET on my.itmo.ru API",
      description:
        "Escape hatch: GET any /api/... path (same origin, authenticated). Prefer the specific tools; find paths with itmo_api_catalog. Response envelopes are unwrapped.",
      inputSchema: { path: z.string().describe("e.g. /api/finances/scholarship/total"), query: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).optional() },
      annotations: READ,
    },
    ({ path, query }) => {
      assertApiPath(path);
      if (/bypass/i.test(path)) throw new Error("This path is blocked (looks like a state-changing GET).");
      return client.get(path, query);
    }
  );

  defineTool(
    server,
    "itmo_public_schedule_search",
    {
      title: "Public timetable search (itmo.ru)",
      description:
        "Find a teacher / group / room in the public timetable at itmo.ru (no login). Returns ids for itmo_public_schedule. For teachers, 'Власова Ассоль' works (the first word is searched, the rest filters).",
      inputSchema: { kind: z.enum(["teacher", "group", "room"]), query: z.string().min(2) },
      annotations: READ,
    },
    ({ kind, query }) => searchPublicSchedule(kind, query)
  );

  defineTool(
    server,
    "itmo_public_schedule",
    {
      title: "Public timetable (itmo.ru)",
      description:
        "Full recurring timetable of a teacher/group/room from itmo.ru: weekday, time, week numbers, group, room, building, subject, format. id comes from itmo_public_schedule_search.",
      inputSchema: { kind: z.enum(["teacher", "group", "room"]), id: z.string().min(1), week: z.enum(["all", "even", "odd"]).default("all") },
      annotations: READ,
    },
    ({ kind, id, week = "all" }) => getPublicSchedule(kind, id, week)
  );
}
