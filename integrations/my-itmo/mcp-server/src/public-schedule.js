/**
 * Public timetable at itmo.ru/ru/schedule — server-rendered HTML, no login.
 * kind: teacher | group | room. Teacher search is verified; group/room reuse the same page layout.
 */
const ORIGIN = "https://itmo.ru";
const SEARCH_TYPE = { group: 0, teacher: 1, room: 2 };
const PAGE_TYPE = { group: 0, teacher: 3, room: 2 };
const DAYS = { 1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс" };

const decode = (s) =>
  s
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
const text = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

async function page(path) {
  const res = await fetch(ORIGIN + path, { redirect: "follow", signal: AbortSignal.timeout(30_000) });
  const body = await res.text();
  // The site answers with an HTML 404 page (sometimes with a 403 status) for malformed queries.
  if (res.status >= 400 || /<title>\s*404/.test(body)) throw new Error(`itmo.ru schedule: no such page (${path})`);
  return body;
}

/** Search by one token (spaces in the query are rejected by the site's WAF). Remaining tokens filter the hits locally. */
export async function searchPublicSchedule(kind, query) {
  const [first, ...rest] = query.trim().split(/\s+/);
  const html = await page(`/ru/schedule/${SEARCH_TYPE[kind]}/${encodeURIComponent(first)}/schedule.htm`);
  const hits = [...html.matchAll(/<a href="(\/ru\/schedule\/(\d)\/([^"/]+)\/raspisanie_zanyatiy\.htm)"[^>]*>([\s\S]*?)<\/a>/g)].map((m) => ({
    id: decodeURIComponent(m[3]),
    kind,
    title: text(m[4]),
    url: ORIGIN + m[1],
  }));
  const needles = rest.map((r) => r.toLowerCase());
  return hits.filter((h) => needles.every((n) => h.title.toLowerCase().includes(n)));
}

/** @param week "all" | "even" | "odd" */
export async function getPublicSchedule(kind, id, week = "all") {
  const wk = { all: "", even: "/1", odd: "/2" }[week];
  const html = await page(`/ru/schedule/${PAGE_TYPE[kind]}/${encodeURIComponent(id)}${wk}/raspisanie_zanyatiy.htm`);
  const title = text(html.match(/<h1 class="page-header">([\s\S]*?)<\/h1>/)?.[1] ?? "");
  const lessons = [];
  for (const table of html.matchAll(/<table id=["'](\d)day["'][\s\S]*?<\/table>/g)) {
    const day = DAYS[table[1]];
    // rows are not always closed with <tr>; split on the time cell instead
    for (const row of table[0].split(/<td class="time">/).slice(1)) {
      const time = text(row.match(/<div>([\s\S]*?)<\/div>/)?.[1] ?? "");
      const weeks = text(row.match(/<\/div>([\s\S]*?)<\/span>/)?.[1] ?? "");
      const cells = [...row.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((c) => c[1]);
      lessons.push({
        day,
        time,
        weeks,
        group: text(cells[0] ?? ""),
        room: text(row.match(/<dd>([\s\S]*?)<\/dd>/)?.[1] ?? ""),
        address: text(row.match(/<dt><i[^>]*><\/i><span>([\s\S]*?)<\/span>/)?.[1] ?? ""),
        subject: text(row.match(/class="lesson"><dl>\s*<dd>([\s\S]*?)<\/dd>/)?.[1] ?? ""),
        format: text(row.match(/class="lesson-format">([\s\S]*?)<\/td>/)?.[1] ?? ""),
      });
    }
  }
  return { title, url: `${ORIGIN}/ru/schedule/${PAGE_TYPE[kind]}/${encodeURIComponent(id)}${wk}/raspisanie_zanyatiy.htm`, lessons };
}
